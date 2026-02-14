"""
Base AI Agent - Pure AI Reasoning
NO HARDCODING, NO NLP RULES
Everything decided by AI dynamically
"""

import asyncio
import json
import os
import sys
from typing import Optional, List, Dict
from datetime import datetime

import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
load_dotenv()


class BaseAgentAI:
    """
    Base class for AI-driven negotiation agents
    Pure AI reasoning - no hardcoded strategies or NLP rules
    """
    
    def __init__(self, 
                 role: str,
                 name: str,
                 system_prompt: str,
                 websocket_url: str = "ws://localhost:9000"):
        """
        Initialize AI agent
        
        Args:
            role: "company" or "investor"
            name: Agent name
            system_prompt: AI prompt with research context
            websocket_url: WebSocket server URL
        """
        self.role = role
        self.name = name
        self.system_prompt = system_prompt
        self.websocket_url = websocket_url
        
        # Conversation state
        self.conversation_history: List[Dict] = []
        self.turn_count = 0
        self.is_active = True
        self.websocket = None
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY required for AI reasoning")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        
        # Chat history for context
        self.chat_history = []
        
        print(f"\n{'='*60}")
        print(f"  AI AGENT: {self.name}")
        print(f"{'='*60}\n")
        print(f"Role: {self.role}")
        print(f"AI Mode: ENABLED (no hardcoding, no NLP)")
        print(f"System prompt: {len(self.system_prompt)} characters of AI context")
        print(f"WebSocket: {self.websocket_url}")
        print(f"Model: {self.model_name}")
        print(f"\nWaiting for connection...\n")
    
    async def connect(self):
        """Connect to WebSocket server"""
        import websockets
        
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            
            await self.websocket.send(json.dumps({
                "type": "register",
                "role": self.role,
                "name": self.name
            }))
            
            print(f"[CONNECTED] {self.name} connected to relay server\n")
            await self.listen()
            
        except Exception as e:
            print(f"[CONNECTION ERROR] {e}")
            raise
    
    async def listen(self):
        """Listen for messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except Exception as e:
            print(f"[LISTEN ERROR] {e}")
        finally:
            if self.websocket:
                await self.websocket.close()
    
    async def handle_message(self, data: dict):
        """Handle incoming messages"""
        msg_type = data.get("type")
        
        if msg_type == "session_start":
            print(f"\n[SESSION STARTED] AI negotiation beginning...\n")
            
            # Company speaks first
            if self.role == "company":
                await asyncio.sleep(1)
                await self.ai_generate_response(is_first=True)
        
        elif msg_type == "message":
            sender = data.get("sender")
            text = data.get("text")
            
            if sender == self.name:
                return
            
            print(f"\n{'-'*60}")
            print(f"[{sender.upper()}]")
            print(f"{'-'*60}")
            print(f"{text}")
            print(f"{'-'*60}\n")
            
            self.conversation_history.append({
                "role": "other",
                "sender": sender,
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
            
            # AI thinking time
            thinking_delay = 1.5
            print(f"[AI REASONING] Analyzing message... ({thinking_delay}s)\n")
            await asyncio.sleep(thinking_delay)
            
            # AI generates response
            await self.ai_generate_response()
        
        elif msg_type == "conclusion":
            conclusion_text = data.get("text", "")
            print(f"\n{'='*60}")
            print(f"  NEGOTIATION CONCLUDED")
            print(f"{'='*60}\n")
            print(conclusion_text)
            print(f"\n{'='*60}\n")
            
            self.is_active = False
            if self.websocket:
                await self.websocket.close()
        
        elif msg_type == "end":
            print(f"\n[SESSION ENDED] {data.get('reason', 'Unknown')}\n")
            self.is_active = False
            if self.websocket:
                await self.websocket.close()
    
    async def ai_generate_response(self, is_first: bool = False):
        """
        Pure AI response generation
        No templates, no hardcoding - just AI reasoning
        
        Args:
            is_first: Whether this is first message
        """
        try:
            # Build AI reasoning prompt
            if is_first:
                prompt = self._ai_first_turn_prompt()
            else:
                prompt = self._ai_response_prompt()
            
            # Build message history for AI
            messages = self.chat_history.copy()
            messages.append(types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            ))
            
            print(f"[AI REASONING] Generating response using AI model...")
            
            # Let AI reason and generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=messages,
                config=types.GenerateContentConfig(
                    temperature=0.7,  # Balance creativity and focus
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2000,  # Allow full thoughts
                    stop_sequences=None,
                )
            )
            
            # Extract AI's response
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    response_text = candidate.content.parts[0].text.strip()
                else:
                    response_text = response.text.strip()
            else:
                response_text = response.text.strip()
            
            # Update chat history
            self.chat_history.append(types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            ))
            self.chat_history.append(types.Content(
                role="model",
                parts=[types.Part(text=response_text)]
            ))
            
            # Clean for speech
            response_text = self._clean_for_speech(response_text)
            
            # Store in conversation
            self.conversation_history.append({
                "role": "self",
                "sender": self.name,
                "text": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            self.turn_count += 1
            
            # Display
            print(f"\n{'-'*60}")
            print(f"[{self.name.upper()} - TURN {self.turn_count}] (AI Generated)")
            print(f"{'-'*60}")
            print(f"{response_text}")
            print(f"{'-'*60}\n")
            
            # Send via WebSocket
            await self.websocket.send(json.dumps({
                "type": "message",
                "text": response_text,
                "sender": self.name,
                "role": self.role,
                "turn": self.turn_count
            }))
            
        except Exception as e:
            print(f"[ERROR] AI generation failed: {e}")
            import traceback
            traceback.print_exc()
            
            await self.websocket.send(json.dumps({
                "type": "error",
                "error": str(e),
                "sender": self.name
            }))
    
    def _ai_first_turn_prompt(self) -> str:
        """
        AI prompt for first turn
        Emphasizes AI decision-making
        """
        return f"""{self.system_prompt}

=== FIRST TURN: OPENING STATEMENT ===

You are about to begin this negotiation. This is your opening statement.

AI TASK: Use the research data provided above to:
1. Analyze the current situation
2. Formulate your opening strategy
3. Decide what to propose
4. Generate your opening statement

REQUIREMENTS:
- 150-250 words
- Specific numbers (valuations, amounts, percentages)
- Based on research data above
- Natural conversational tone
- Complete thought (no truncation)

AI: Begin your negotiation now using your reasoning capabilities."""
    
    def _ai_response_prompt(self) -> str:
        """
        AI prompt for subsequent turns
        Pure reasoning, no templates
        """
        # Get recent conversation
        recent = self.conversation_history[-8:] if len(self.conversation_history) > 8 else self.conversation_history
        
        history_text = "\n\n".join([
            f"[{msg['sender']}]: {msg['text']}" 
            for msg in recent
        ])
        
        return f"""{self.system_prompt}

=== CONVERSATION SO FAR ===
{history_text}

=== TURN {self.turn_count + 1}: YOUR RESPONSE ===

AI TASK: Analyze the above conversation and:
1. Understand what the other party just said
2. Evaluate their arguments and position
3. Formulate your response strategy
4. Decide what to say next
5. Generate your response

Use your AI reasoning to:
- Address specific points raised
- Use data from your research
- Adapt your strategy based on their response
- Move negotiation forward
- Make strategic decisions

REQUIREMENTS:
- 100-200 words
- Direct response to their last message
- Specific and substantive
- Natural tone
- Complete thought

AI: Respond now using your reasoning capabilities."""
    
    def _clean_for_speech(self, text: str) -> str:
        """Clean text for speech output"""
        # Remove markdown
        text = text.replace('**', '').replace('__', '')
        text = text.replace('*', '').replace('_', '')
        text = text.replace('#', '').replace('`', '')
        
        # Remove bullets/numbers
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            line = line.lstrip('- •*1234567890.').lstrip()
            if line:
                cleaned.append(line)
        
        text = ' '.join(cleaned)
        
        # Remove extra spaces
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        return text.strip()
    
    def get_transcript(self) -> str:
        """Get full conversation transcript"""
        return "\n\n".join([
            f"[{msg['sender']}]: {msg['text']}"
            for msg in self.conversation_history
        ])
"""
Base agent class for negotiation agents
"""

import asyncio
import json
import os
import time
import sys
from typing import Optional, List, Dict
from datetime import datetime

import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

class BaseAgent:
    """
    Base class for negotiation agents (CEO and Investor)
    """
    
    def __init__(self, 
                 role: str,
                 name: str,
                 system_prompt: str,
                 websocket_url: str = "ws://localhost:9000"):
        """
        Initialize base agent
        
        Args:
            role: "company" or "investor"
            name: Agent name (e.g., "Tesla", "BlackRock")
            system_prompt: System prompt with context
            websocket_url: WebSocket server URL
        """
        self.role = role
        self.name = name
        self.system_prompt = system_prompt
        self.websocket_url = websocket_url
        
        # Negotiation state
        self.conversation_history: List[Dict] = []
        self.turn_count = 0
        self.is_active = True
        self.websocket = None
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Create Gemini client
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        
        # Chat history for Gemini (maintaining conversation context)
        self.chat_history = []
        
        # Initialize Brave Search
        try:
            from utils.brave_search import get_brave_search
            self.brave = get_brave_search()
        except:
            self.brave = None
            print("[INFO] Brave Search not available")
        
        print(f"\n{'='*60}")
        print(f"  {self.role.upper()} AGENT: {self.name}")
        print(f"{'='*60}\n")
        print(f"Role: {self.role}")
        print(f"System prompt loaded: {len(self.system_prompt)} characters")
        print(f"WebSocket target: {self.websocket_url}")
        print(f"Gemini model: {self.model_name}")
        if self.brave and self.brave.enabled:
            print(f"Brave Search: ENABLED")
        print(f"\nWaiting for connection...\n")
    
    async def connect(self):
        """
        Connect to WebSocket server
        """
        import websockets
        
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            
            # Send registration message
            await self.websocket.send(json.dumps({
                "type": "register",
                "role": self.role,
                "name": self.name
            }))
            
            print(f"[CONNECTED] {self.name} connected to relay server\n")
            
            # Wait for session start or listen for messages
            await self.listen()
            
        except Exception as e:
            print(f"[CONNECTION ERROR] {e}")
            raise
    
    async def listen(self):
        """
        Listen for messages from WebSocket server
        """
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
        """
        Handle incoming WebSocket messages
        
        Args:
            data: Message data
        """
        msg_type = data.get("type")
        
        if msg_type == "session_start":
            print(f"\n[SESSION STARTED] Negotiation beginning...\n")
            
            # Fetch real-time data if first message and Brave is enabled
            if self.role == "company" and self.brave and self.brave.enabled:
                print(f"[BRAVE SEARCH] Fetching latest data for {self.name}...")
                latest_info = self.brave.get_company_updates(self.name)
                if latest_info:
                    print(f"[REAL-TIME DATA] Latest updates:\n{latest_info}\n")
            
            # Company speaks first
            if self.role == "company":
                await asyncio.sleep(1)  # Brief pause for dramatic effect
                await self.generate_and_send_response(is_first=True)
        
        elif msg_type == "message":
            sender = data.get("sender")
            text = data.get("text")
            
            # Don't process our own messages
            if sender == self.name:
                return
            
            print(f"\n{'-'*60}")
            print(f"[{sender.upper()}]")
            print(f"{'-'*60}")
            print(f"{text}")
            print(f"{'-'*60}\n")
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "other",
                "sender": sender,
                "text": text,
                "timestamp": datetime.now().isoformat()
            })
            
            # Simulate thinking time (1-2 seconds)
            thinking_delay = 1.0 + (hash(text) % 10) / 10.0  # 1.0-2.0 seconds
            print(f"[THINKING] Analyzing response... ({thinking_delay:.1f}s)\n")
            await asyncio.sleep(thinking_delay)
            
            # Generate response
            await self.generate_and_send_response()
        
        elif msg_type == "conclusion":
            conclusion_text = data.get("text", "")
            print(f"\n{'='*60}")
            print(f"  NEGOTIATION CONCLUDED")
            print(f"{'='*60}\n")
            print(conclusion_text)
            print(f"\n{'='*60}\n")
            
            self.is_active = False
            
            # Close connection
            if self.websocket:
                await self.websocket.close()
        
        elif msg_type == "end":
            print(f"\n[SESSION ENDED] {data.get('reason', 'Unknown reason')}\n")
            self.is_active = False
            if self.websocket:
                await self.websocket.close()
    
    def _get_real_time_context(self) -> str:
        """
        Get real-time context using Brave Search
        
        Returns:
            Real-time context string or empty string
        """
        if not self.brave or not self.brave.enabled:
            return ""
        
        context_parts = []
        
        # Get company updates
        if self.role == "company":
            updates = self.brave.get_company_updates(self.name)
            if updates:
                context_parts.append(f"LATEST {self.name.upper()} UPDATES:\n{updates}")
        
        # Get market data for both roles
        if self.name == "Tesla":
            market = self.brave.get_market_data("electric vehicle market")
            if market:
                context_parts.append(f"EV MARKET TRENDS:\n{market}")
        elif self.name == "SpaceX":
            market = self.brave.get_market_data("space industry commercial satellites")
            if market:
                context_parts.append(f"SPACE MARKET TRENDS:\n{market}")
        elif self.name == "OpenAI":
            market = self.brave.get_market_data("AI artificial intelligence market")
            if market:
                context_parts.append(f"AI MARKET TRENDS:\n{market}")
        
        if context_parts:
            return "\n\n".join(context_parts)
        return ""
    
    async def generate_and_send_response(self, is_first: bool = False):
        """
        Generate response using Gemini and send via WebSocket
        
        Args:
            is_first: Whether this is the first message (company only)
        """
        try:
            # Get real-time context
            real_time_context = self._get_real_time_context()
            
            # Build prompt
            if is_first:
                prompt = self._build_first_prompt(real_time_context)
            else:
                prompt = self._build_response_prompt(real_time_context)
            
            # Build messages for Gemini API
            messages = self.chat_history.copy()
            messages.append(types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            ))
            
            # Generate response using Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=messages,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=300,
                )
            )
            
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
            
            # Clean up response (remove any markdown, etc.)
            response_text = self._clean_response(response_text)
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "self",
                "sender": self.name,
                "text": response_text,
                "timestamp": datetime.now().isoformat()
            })
            
            self.turn_count += 1
            
            # Display our response
            print(f"\n{'-'*60}")
            print(f"[{self.name.upper()} - TURN {self.turn_count}]")
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
            print(f"[ERROR] Failed to generate response: {e}")
            import traceback
            traceback.print_exc()
            # Send error message
            await self.websocket.send(json.dumps({
                "type": "error",
                "error": str(e),
                "sender": self.name
            }))
    
    def _build_first_prompt(self, real_time_context: str = "") -> str:
        """
        Build the first prompt (company only)
        """
        context_section = ""
        if real_time_context:
            context_section = f"\n\nREAL-TIME MARKET DATA:\n{real_time_context}\n\nUse this current information to enhance your pitch and demonstrate market momentum.\n"
        
        return f"""
{self.system_prompt}
{context_section}
SITUATION:
You are about to begin a negotiation with an institutional investor. This is your opening statement.

INSTRUCTIONS:
1. Present your funding proposal clearly
2. State the round type (Series X, Growth, etc.)
3. Mention pre-money valuation
4. Specify amount raising and equity offered
5. Explain use of funds
6. Create urgency and excitement
7. Keep it conversational and natural (20-45 seconds spoken)
8. Do NOT use bullet points or formatting

Begin the negotiation now with your opening pitch.
"""
    
    def _build_response_prompt(self, real_time_context: str = "") -> str:
        """
        Build response prompt based on conversation history
        """
        # Get last 3 exchanges for context
        recent_history = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
        
        history_text = "\n\n".join([
            f"[{msg['sender']}]: {msg['text']}" 
            for msg in recent_history
        ])
        
        context_section = ""
        if real_time_context:
            context_section = f"\n\nREAL-TIME MARKET DATA:\n{real_time_context}\n\nUse this current information to support your arguments.\n"
        
        return f"""
{self.system_prompt}
{context_section}
CONVERSATION SO FAR:
{history_text}

INSTRUCTIONS:
1. Respond directly to the last message
2. Address specific points raised
3. Use data and reasoning
4. Maintain your negotiation position
5. Keep response natural and conversational (20-45 seconds spoken)
6. Do NOT use bullet points or formatting
7. Move the negotiation forward

Your response:
"""
    
    def _clean_response(self, text: str) -> str:
        """
        Clean response text for TTS
        """
        # Remove markdown formatting
        text = text.replace('**', '').replace('__', '')
        text = text.replace('*', '').replace('_', '')
        text = text.replace('#', '').replace('`', '')
        
        # Remove bullet points and numbered lists
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            # Remove bullet points
            line = line.lstrip('- •*').lstrip()
            # Remove numbered list markers
            if line and line[0].isdigit() and '.' in line[:3]:
                line = line.split('.', 1)[1].lstrip()
            if line:
                cleaned_lines.append(line)
        
        # Join with spaces
        text = ' '.join(cleaned_lines)
        
        # Remove multiple spaces
        while '  ' in text:
            text = text.replace('  ', ' ')
        
        return text.strip()
    
    def get_conversation_transcript(self) -> str:
        """
        Get full conversation transcript
        """
        transcript = []
        for msg in self.conversation_history:
            transcript.append(f"[{msg['sender']}]: {msg['text']}")
        return "\n\n".join(transcript)
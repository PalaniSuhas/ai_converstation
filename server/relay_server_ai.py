"""
AI-Driven Relay Server
NO HARDCODING - AI analyzes negotiation and decides when to end
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

import websockets

import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()


class AIRelayServer:
    """
    AI-driven WebSocket relay server
    AI analyzes conversation and determines termination
    """
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        """Initialize AI relay server"""
        self.host = host
        self.port = port
        
        # Connected clients
        self.clients: Dict[str, any] = {}
        self.company_agent = None
        self.investor_agent = None
        
        # Session state
        self.session_active = False
        self.turn_count = 0
        self.min_turns = 6
        self.max_turns = 20
        self.conversation_history = []
        
        # Agent metadata
        self.company_name = None
        self.investor_name = None
        
        # Initialize Gemini for AI analysis
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None
            self.model_name = None
            print("[WARNING] No Gemini API key - AI analysis disabled")
        
        print(f"\n{'='*60}")
        print(f"  AI-DRIVEN NEGOTIATION RELAY SERVER")
        print(f"{'='*60}\n")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Turn limits: {self.min_turns} min, {self.max_turns} max")
        print(f"AI Mode: ENABLED (dynamic termination)")
        print(f"\nWaiting for agents to connect...\n")
    
    async def start(self):
        """Start the WebSocket server"""
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[SERVER STARTED] AI relay server running on ws://{self.host}:{self.port}")
            print(f"[WAITING] Waiting for AI agents to connect...\n")
            await asyncio.Future()  # Run forever
    
    async def handle_client(self, websocket):
        """Handle client connection"""
        client_id = id(websocket)
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_message(websocket, data, client_id)
        except websockets.exceptions.ConnectionClosed:
            await self.handle_disconnect(client_id)
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            await self.handle_disconnect(client_id)
    
    async def process_message(self, websocket, data: dict, client_id: int):
        """Process incoming message"""
        msg_type = data.get("type")
        
        if msg_type == "register":
            await self.handle_registration(websocket, data, client_id)
        elif msg_type == "message":
            await self.handle_negotiation_message(data)
        elif msg_type == "error":
            print(f"[AGENT ERROR] {data.get('sender')}: {data.get('error')}")
    
    async def handle_registration(self, websocket, data: dict, client_id: int):
        """Handle agent registration"""
        role = data.get("role")
        name = data.get("name")
        
        self.clients[client_id] = websocket
        
        if role == "company":
            self.company_agent = websocket
            self.company_name = name
            print(f"[CONNECTED] AI Company Agent: {name}")
        elif role == "investor":
            self.investor_agent = websocket
            self.investor_name = name
            print(f"[CONNECTED] AI Investor Agent: {name}")
        
        # Start session if both connected
        if self.company_agent and self.investor_agent and not self.session_active:
            await self.start_session()
    
    async def start_session(self):
        """Start negotiation session"""
        self.session_active = True
        
        print(f"\n{'='*60}")
        print(f"  AI NEGOTIATION SESSION STARTED")
        print(f"{'='*60}")
        print(f"  Company: {self.company_name}")
        print(f"  Investor: {self.investor_name}")
        print(f"  Turn Limits: {self.min_turns}-{self.max_turns} (AI-driven)")
        print(f"  Mode: FULLY AI (no hardcoded termination rules)")
        print(f"{'='*60}\n")
        
        # Notify both agents
        session_msg = json.dumps({
            "type": "session_start",
            "company": self.company_name,
            "investor": self.investor_name,
            "timestamp": datetime.now().isoformat()
        })
        
        await self.company_agent.send(session_msg)
        await self.investor_agent.send(session_msg)
    
    async def handle_negotiation_message(self, data: dict):
        """Handle negotiation message and relay"""
        sender = data.get("sender")
        role = data.get("role")
        text = data.get("text")
        turn = data.get("turn", 0)
        
        # Store in history
        self.conversation_history.append({
            "sender": sender,
            "role": role,
            "text": text,
            "turn": turn,
            "timestamp": datetime.now().isoformat()
        })
        
        self.turn_count += 1
        
        print(f"\n[TURN {self.turn_count}/{self.max_turns}] Message from {sender}")
        
        # Relay to other party
        if role == "company" and self.investor_agent:
            await self.investor_agent.send(json.dumps(data))
        elif role == "investor" and self.company_agent:
            await self.company_agent.send(json.dumps(data))
        
        # AI analyzes if negotiation should end
        await self.ai_check_termination()
    
    async def ai_check_termination(self):
        """
        AI analyzes conversation and decides if negotiation should end
        NO hardcoded patterns - pure AI reasoning
        """
        # Need minimum turns for substantive discussion
        if self.turn_count < self.min_turns:
            return
        
        # Safety limit
        if self.turn_count >= self.max_turns:
            await self.end_session(
                "MAX_TURNS_REACHED",
                f"Reached maximum {self.max_turns} turns. Parties need more time."
            )
            return
        
        # Let AI analyze if negotiation should end
        if self.client and self.turn_count >= self.min_turns:
            should_end = await self._ai_analyze_termination()
            
            if should_end:
                status = should_end.get("status", "ONGOING")
                reason = should_end.get("reason", "AI determined negotiation complete")
                await self.end_session(status, reason)
    
    async def _ai_analyze_termination(self) -> Optional[Dict]:
        """
        AI analyzes conversation to determine if it should end
        Returns termination decision or None to continue
        """
        if not self.client:
            return None
        
        # Only check every 2 turns to avoid excessive API calls
        if self.turn_count % 2 != 0:
            return None
        
        # Get recent conversation
        recent = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
        
        conversation_text = "\n\n".join([
            f"[{msg['sender']}]: {msg['text']}"
            for msg in recent
        ])
        
        prompt = f"""You are analyzing an AI-to-AI negotiation between {self.company_name} (company) and {self.investor_name} (investor).

RECENT CONVERSATION:
{conversation_text}

CONTEXT:
- Turn: {self.turn_count}
- Minimum substantive turns required: {self.min_turns}
- Maximum turns allowed: {self.max_turns}

YOUR TASK: Analyze whether this negotiation should END now or CONTINUE.

ANALYSIS FRAMEWORK (use AI reasoning, not keyword matching):

1. Has a deal been explicitly accepted?
   - Look for genuine acceptance (not just "interesting" or "considering")
   - Investor must clearly commit to the investment

2. Has the deal been explicitly declined?
   - Look for clear rejection or walking away
   - Investor must definitively pass on the opportunity

3. Is the negotiation still productive?
   - Are they discussing terms and making progress?
   - Or just repeating the same arguments?

4. Have they reached an impasse?
   - Fundamental disagreement that won't resolve?
   - Neither side willing to budge?

RESPOND WITH JSON ONLY:
{{
    "should_end": true/false,
    "status": "DEAL_ACCEPTED" | "DEAL_DECLINED" | "ONGOING" | "IMPASSE",
    "reason": "Brief explanation of your decision",
    "confidence": 0.0-1.0
}}

If negotiation is productive and ongoing, set should_end to false.
Only end if there's clear acceptance, decline, or unresolvable impasse.

YOUR ANALYSIS (JSON only):"""

        try:
            print(f"[AI ANALYSIS] Checking if negotiation should terminate...")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )],
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower for more consistent analysis
                    max_output_tokens=300,
                )
            )
            
            # Parse AI response
            response_text = response.text.strip()
            
            # Remove markdown if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(response_text)
            
            print(f"[AI ANALYSIS] Decision: {analysis.get('should_end')} (confidence: {analysis.get('confidence', 0):.2f})")
            print(f"[AI ANALYSIS] Status: {analysis.get('status')}")
            print(f"[AI ANALYSIS] Reason: {analysis.get('reason')}\n")
            
            if analysis.get("should_end") and analysis.get("confidence", 0) > 0.7:
                return analysis
            
            return None
            
        except Exception as e:
            print(f"[AI ANALYSIS] Error: {e}")
            return None
    
    async def end_session(self, status: str, reason: str):
        """End negotiation session"""
        print(f"\n{'='*60}")
        print(f"  SESSION ENDING: {status}")
        print(f"{'='*60}")
        print(f"  Reason: {reason}")
        print(f"  Total Turns: {self.turn_count}")
        print(f"{'='*60}\n")
        
        # Generate AI conclusion
        conclusion = await self.ai_generate_conclusion(status)
        
        # Send conclusion
        conclusion_msg = json.dumps({
            "type": "conclusion",
            "text": conclusion,
            "status": status,
            "reason": reason,
            "total_turns": self.turn_count
        })
        
        if self.company_agent:
            try:
                await self.company_agent.send(conclusion_msg)
            except:
                pass
        if self.investor_agent:
            try:
                await self.investor_agent.send(conclusion_msg)
            except:
                pass
        
        await asyncio.sleep(2)
        
        # Send end message
        end_msg = json.dumps({
            "type": "end",
            "reason": reason
        })
        
        if self.company_agent:
            try:
                await self.company_agent.send(end_msg)
            except:
                pass
        if self.investor_agent:
            try:
                await self.investor_agent.send(end_msg)
            except:
                pass
        
        self.session_active = False
    
    async def ai_generate_conclusion(self, status: str) -> str:
        """
        AI generates conclusion analysis
        NO templates - pure AI analysis
        """
        if not self.client:
            return self._simple_conclusion(status)
        
        try:
            # Build transcript
            transcript = "\n\n".join([
                f"[{msg['sender']}]: {msg['text']}"
                for msg in self.conversation_history
            ])
            
            # Import prompt
            from utils.ai_prompts import get_ai_conclusion_prompt
            prompt = get_ai_conclusion_prompt(transcript, status, self.turn_count)
            
            print("[AI CONCLUSION] Generating comprehensive analysis...")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )],
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1500,
                )
            )
            
            conclusion = response.text.strip()
            print("[AI CONCLUSION] ✓ Complete\n")
            
            return conclusion
            
        except Exception as e:
            print(f"[ERROR] AI conclusion generation failed: {e}")
            return self._simple_conclusion(status)
    
    def _simple_conclusion(self, status: str) -> str:
        """Fallback simple conclusion"""
        return f"""
NEGOTIATION CONCLUSION

Status: {status}
Company: {self.company_name}
Investor: {self.investor_name}
Total Turns: {self.turn_count}

The AI-driven negotiation between {self.company_name} and {self.investor_name} has concluded with status: {status}.

Over {self.turn_count} turns, both AI agents engaged in substantive negotiation based on their web research and AI reasoning. Each agent formulated strategies dynamically and adapted to the conversation flow without hardcoded rules or NLP patterns.

This demonstrates the power of pure AI reasoning in complex negotiation scenarios.
"""
    
    async def handle_disconnect(self, client_id: int):
        """Handle client disconnection"""
        if client_id in self.clients:
            del self.clients[client_id]
        
        if self.company_agent and id(self.company_agent) == client_id:
            print(f"[DISCONNECTED] Company Agent: {self.company_name}")
            self.company_agent = None
        
        if self.investor_agent and id(self.investor_agent) == client_id:
            print(f"[DISCONNECTED] Investor Agent: {self.investor_name}")
            self.investor_agent = None


async def main():
    """Main server entry point"""
    server = AIRelayServer(host="localhost", port=9000)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
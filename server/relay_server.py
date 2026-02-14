"""
WebSocket relay server for AI-to-AI negotiation
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Optional

import websockets

import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NegotiationServer:
    """
    WebSocket relay server for negotiation agents
    """
    
    def __init__(self, host: str = "localhost", port: int = 9000):
        """
        Initialize negotiation server
        
        Args:
            host: Server host
            port: Server port
        """
        self.host = host
        self.port = port
        
        # Connected clients
        self.clients: Dict[str, any] = {}
        self.company_agent = None
        self.investor_agent = None
        
        # Session state
        self.session_active = False
        self.turn_count = 0
        self.max_turns = 8
        self.conversation_history = []
        
        # Agent metadata
        self.company_name = None
        self.investor_name = None
        
        # Initialize Gemini for conclusion generation
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None
            self.model_name = None
            print("Warning: GEMINI_API_KEY not found. Conclusion generation disabled.")
        
        print(f"\n{'='*60}")
        print(f"  AI NEGOTIATION RELAY SERVER")
        print(f"{'='*60}\n")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Max turns: {self.max_turns}")
        print(f"\nWaiting for agents to connect...\n")
    
    async def start(self):
        """
        Start the WebSocket server
        """
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"[SERVER STARTED] WebSocket relay server running on ws://{self.host}:{self.port}")
            print(f"[WAITING] Waiting for CEO and Investor agents to connect...\n")
            await asyncio.Future()  # Run forever
    
    async def handle_client(self, websocket):
        """
        Handle client connection
        
        Args:
            websocket: WebSocket connection
        """
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
        """
        Process incoming message
        
        Args:
            websocket: WebSocket connection
            data: Message data
            client_id: Client identifier
        """
        msg_type = data.get("type")
        
        if msg_type == "register":
            await self.handle_registration(websocket, data, client_id)
        
        elif msg_type == "message":
            await self.handle_negotiation_message(data)
        
        elif msg_type == "error":
            print(f"[AGENT ERROR] {data.get('sender')}: {data.get('error')}")
    
    async def handle_registration(self, websocket, data: dict, client_id: int):
        """
        Handle agent registration
        
        Args:
            websocket: WebSocket connection
            data: Registration data
            client_id: Client identifier
        """
        role = data.get("role")
        name = data.get("name")
        
        self.clients[client_id] = websocket
        
        if role == "company":
            self.company_agent = websocket
            self.company_name = name
            print(f"[CONNECTED] Company Agent: {name}")
        
        elif role == "investor":
            self.investor_agent = websocket
            self.investor_name = name
            print(f"[CONNECTED] Investor Agent: {name}")
        
        # Start session if both connected
        if self.company_agent and self.investor_agent and not self.session_active:
            await self.start_session()
    
    async def start_session(self):
        """
        Start negotiation session
        """
        self.session_active = True
        
        print(f"\n{'='*60}")
        print(f"  NEGOTIATION SESSION STARTED")
        print(f"{'='*60}")
        print(f"  Company: {self.company_name}")
        print(f"  Investor: {self.investor_name}")
        print(f"  Max Turns: {self.max_turns}")
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
        """
        Handle negotiation message and relay to other party
        
        Args:
            data: Message data
        """
        sender = data.get("sender")
        role = data.get("role")
        text = data.get("text")
        turn = data.get("turn", 0)
        
        # Store in conversation history
        self.conversation_history.append({
            "sender": sender,
            "role": role,
            "text": text,
            "turn": turn,
            "timestamp": datetime.now().isoformat()
        })
        
        self.turn_count += 1
        
        # Relay to other party
        if role == "company" and self.investor_agent:
            await self.investor_agent.send(json.dumps(data))
        elif role == "investor" and self.company_agent:
            await self.company_agent.send(json.dumps(data))
        
        # Check for termination conditions
        await self.check_termination(text, role)
    
    async def check_termination(self, text: str, role: str):
        """
        Check if negotiation should terminate
        
        Args:
            text: Message text
            role: Sender role
        """
        text_lower = text.lower()
        
        # Deal accepted
        if role == "investor" and any(phrase in text_lower for phrase in [
            "we will proceed",
            "we'll proceed",
            "deal is acceptable",
            "we accept",
            "we're in",
            "let's move forward"
        ]):
            await self.end_session("DEAL ACCEPTED", "The investor has accepted the proposal.")
            return
        
        # Deal declined
        if role == "investor" and any(phrase in text_lower for phrase in [
            "we are declining",
            "we're declining",
            "we pass",
            "not interested",
            "walking away",
            "cannot proceed"
        ]):
            await self.end_session("DEAL DECLINED", "The investor has declined the proposal.")
            return
        
        # Max turns reached
        if self.turn_count >= self.max_turns:
            await self.end_session("MAX TURNS REACHED", f"Negotiation reached maximum {self.max_turns} turns without conclusion.")
            return
    
    async def end_session(self, status: str, reason: str):
        """
        End negotiation session and generate conclusion
        
        Args:
            status: Session end status
            reason: Reason for ending
        """
        print(f"\n{'='*60}")
        print(f"  SESSION ENDING: {status}")
        print(f"{'='*60}")
        print(f"  Reason: {reason}")
        print(f"  Total Turns: {self.turn_count}")
        print(f"{'='*60}\n")
        
        # Generate AI conclusion
        conclusion = await self.generate_conclusion(status)
        
        # Send conclusion to both agents
        conclusion_msg = json.dumps({
            "type": "conclusion",
            "text": conclusion,
            "status": status,
            "reason": reason,
            "total_turns": self.turn_count
        })
        
        if self.company_agent:
            await self.company_agent.send(conclusion_msg)
        if self.investor_agent:
            await self.investor_agent.send(conclusion_msg)
        
        # Brief pause before ending
        await asyncio.sleep(2)
        
        # Send end message
        end_msg = json.dumps({
            "type": "end",
            "reason": reason
        })
        
        if self.company_agent:
            await self.company_agent.send(end_msg)
        if self.investor_agent:
            await self.investor_agent.send(end_msg)
        
        self.session_active = False
    
    async def generate_conclusion(self, status: str) -> str:
        """
        Generate AI-powered conclusion
        
        Args:
            status: Negotiation status
        
        Returns:
            Conclusion text
        """
        if not self.client:
            return self._generate_simple_conclusion(status)
        
        try:
            # Build transcript
            transcript = "\n\n".join([
                f"[{msg['sender']}]: {msg['text']}"
                for msg in self.conversation_history
            ])
            
            # Build prompt
            from utils.prompts import get_conclusion_prompt
            prompt = get_conclusion_prompt(transcript, status)
            
            # Generate conclusion
            print("[GENERATING AI CONCLUSION] Please wait...\n")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )],
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    top_p=0.95,
                    max_output_tokens=800,
                )
            )
            
            conclusion = response.text.strip()
            
            return conclusion
            
        except Exception as e:
            print(f"[ERROR] Could not generate AI conclusion: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_simple_conclusion(status)
    
    def _generate_simple_conclusion(self, status: str) -> str:
        """
        Generate simple conclusion fallback
        
        Args:
            status: Negotiation status
        
        Returns:
            Simple conclusion text
        """
        return f"""
NEGOTIATION CONCLUSION

Status: {status}
Company: {self.company_name}
Investor: {self.investor_name}
Total Turns: {self.turn_count}

The negotiation between {self.company_name} and {self.investor_name} has concluded with status: {status}.

Over {self.turn_count} turns of discussion, both parties presented their positions and engaged in strategic negotiation. The company advocated for their valuation and growth story, while the investor analyzed the opportunity through their investment framework.

This negotiation demonstrates the complex dynamics of institutional investment decisions, where both parties must balance competing interests and find mutually beneficial terms.

Thank you for participating in this AI-powered negotiation simulation.
"""
    
    async def handle_disconnect(self, client_id: int):
        """
        Handle client disconnection
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.clients:
            del self.clients[client_id]
        
        if self.company_agent and id(self.company_agent) == client_id:
            print(f"[DISCONNECTED] Company Agent: {self.company_name}")
            self.company_agent = None
        
        if self.investor_agent and id(self.investor_agent) == client_id:
            print(f"[DISCONNECTED] Investor Agent: {self.investor_name}")
            self.investor_agent = None

async def main():
    """
    Main server entry point
    """
    server = NegotiationServer(host="localhost", port=9000)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
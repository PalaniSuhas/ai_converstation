#!/usr/bin/env python3
"""
Main entry point for AI negotiation agents
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents import CompanyAgent, InvestorAgent
from utils import get_tts_engine

def parse_args():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description="AI-to-AI Voice Negotiation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --company Tesla
  python run.py --investor BlackRock
  python run.py --company SpaceX --server ws://localhost:9000
  
Available Companies:
  - Tesla
  - SpaceX
  - OpenAI
  
Available Investors:
  - BlackRock
  - Sequoia Capital
  - Andreessen Horowitz
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--company",
        type=str,
        help="Run as company agent (e.g., Tesla, SpaceX, OpenAI)"
    )
    group.add_argument(
        "--investor",
        type=str,
        help="Run as investor agent (e.g., BlackRock, Sequoia Capital)"
    )
    
    parser.add_argument(
        "--server",
        type=str,
        default="ws://localhost:9000",
        help="WebSocket server URL (default: ws://localhost:9000)"
    )
    
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio output (text only)"
    )
    
    return parser.parse_args()

async def run_company_agent(company_name: str, server_url: str, enable_audio: bool):
    """
    Run company agent
    
    Args:
        company_name: Company name
        server_url: WebSocket server URL
        enable_audio: Whether to enable audio
    """
    print(f"\n{'#'*60}")
    print(f"#  STARTING COMPANY AGENT")
    print(f"{'#'*60}\n")
    
    # Initialize TTS if enabled
    if enable_audio:
        tts = get_tts_engine(personality="confident")
        print("[AUDIO] Text-to-Speech enabled with confident personality\n")
    
    # Create and connect agent
    agent = CompanyAgent(company_name=company_name, websocket_url=server_url)
    
    try:
        await agent.connect()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Shutting down agent...\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)

async def run_investor_agent(investor_name: str, server_url: str, enable_audio: bool):
    """
    Run investor agent
    
    Args:
        investor_name: Investor name
        server_url: WebSocket server URL
        enable_audio: Whether to enable audio
    """
    print(f"\n{'#'*60}")
    print(f"#  STARTING INVESTOR AGENT")
    print(f"{'#'*60}\n")
    
    # Initialize TTS if enabled
    if enable_audio:
        tts = get_tts_engine(personality="analytical")
        print("[AUDIO] Text-to-Speech enabled with analytical personality\n")
    
    # Create and connect agent
    agent = InvestorAgent(investor_name=investor_name, websocket_url=server_url)
    
    try:
        await agent.connect()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Shutting down agent...\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)

def main():
    """
    Main entry point
    """
    args = parse_args()
    
    # Determine if audio is enabled
    enable_audio = not args.no_audio
    
    try:
        if args.company:
            asyncio.run(run_company_agent(args.company, args.server, enable_audio))
        elif args.investor:
            asyncio.run(run_investor_agent(args.investor, args.server, enable_audio))
    except KeyboardInterrupt:
        print("\n\nShutdown complete.\n")
    except Exception as e:
        print(f"\nFatal error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Main entry point for AI-driven negotiation agents
100% AI - NO HARDCODING - NO NLP
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents import AICompanyAgent, AIInvestorAgent


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AI-to-AI Negotiation System - Fully AI-Driven",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🤖 FULLY AI-DRIVEN SYSTEM 🤖

This system uses:
- AI web research (NO hardcoded data)
- AI reasoning (NO NLP rules)
- AI strategy (NO templates)

Examples:
  python run.py --company Tesla
  python run.py --investor BlackRock
  python run.py --company SpaceX --server ws://localhost:9000
  
Works with ANY company/investor - AI researches from web!

Examples:
  - Tesla, SpaceX, OpenAI, Apple, Google, Microsoft
  - BlackRock, Sequoia, a16z, SoftBank, Berkshire Hathaway
  - Or ANY other company/investor you can think of!

AI will research them via web search and negotiate intelligently.
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--company",
        type=str,
        help="Run as company agent (e.g., Tesla, Apple, any company)"
    )
    group.add_argument(
        "--investor",
        type=str,
        help="Run as investor agent (e.g., BlackRock, any investor)"
    )
    
    parser.add_argument(
        "--server",
        type=str,
        default="ws://localhost:9000",
        help="WebSocket server URL (default: ws://localhost:9000)"
    )
    
    return parser.parse_args()


async def run_company_agent(company_name: str, server_url: str):
    """
    Run AI-driven company agent
    
    Args:
        company_name: Company name (ANY company - AI researches it)
        server_url: WebSocket server URL
    """
    print(f"\n{'#'*60}")
    print(f"#  STARTING AI-DRIVEN COMPANY AGENT")
    print(f"{'#'*60}\n")
    print(f"Company: {company_name}")
    print(f"Mode: FULLY AI (no hardcoding, no NLP)")
    print(f"Research: AI will search web for current data")
    print(f"Strategy: AI reasoning from research")
    print(f"Responses: AI-generated dynamically\n")
    
    # Create AI agent (it will research company via web)
    agent = AICompanyAgent(company_name=company_name, websocket_url=server_url)
    
    try:
        await agent.connect()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Shutting down AI agent...\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)


async def run_investor_agent(investor_name: str, server_url: str):
    """
    Run AI-driven investor agent
    
    Args:
        investor_name: Investor name (ANY investor - AI researches it)
        server_url: WebSocket server URL
    """
    print(f"\n{'#'*60}")
    print(f"#  STARTING AI-DRIVEN INVESTOR AGENT")
    print(f"{'#'*60}\n")
    print(f"Investor: {investor_name}")
    print(f"Mode: FULLY AI (no hardcoding, no NLP)")
    print(f"Research: AI will search web for current data")
    print(f"Strategy: AI reasoning from research")
    print(f"Responses: AI-generated dynamically\n")
    
    # Create AI agent (it will research investor via web)
    agent = AIInvestorAgent(investor_name=investor_name, websocket_url=server_url)
    
    try:
        await agent.connect()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Shutting down AI agent...\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)


def main():
    """Main entry point"""
    args = parse_args()
    
    print("\n" + "="*60)
    print("  AI-TO-AI NEGOTIATION SYSTEM")
    print("  100% AI | 0% Hardcoding | 0% NLP")
    print("="*60 + "\n")
    
    try:
        if args.company:
            asyncio.run(run_company_agent(args.company, args.server))
        elif args.investor:
            asyncio.run(run_investor_agent(args.investor, args.server))
    except KeyboardInterrupt:
        print("\n\nShutdown complete.\n")
    except Exception as e:
        print(f"\nFatal error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
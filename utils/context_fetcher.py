"""
Context fetcher for company and investor data
"""

import json

# Simulated company data (in production, this would fetch from APIs or databases)
COMPANY_DATA = {
    "Tesla": {
        "market_cap": "800B",
        "annual_revenue": "96.8B",
        "revenue_growth": "42%",
        "gross_margin": "25.6%",
        "operating_margin": "9.2%",
        "net_income": "8.9B",
        "cash_position": "16.4B",
        "total_debt": "2.9B",
        "employees": "140,000",
        "industry": "Electric Vehicles & Clean Energy",
        "key_products": [
            "Model 3/Y/S/X vehicles",
            "Energy storage (Powerwall, Megapack)",
            "Solar panels and solar roof",
            "Full Self-Driving software"
        ],
        "competitive_advantages": [
            "Vertical integration (battery to sales)",
            "Supercharger network infrastructure",
            "Over-the-air software updates",
            "Brand strength and customer loyalty",
            "Manufacturing scale and efficiency"
        ],
        "recent_achievements": [
            "Produced 1.8M vehicles in 2023",
            "Cybertruck production launch",
            "4680 battery cell production scaling",
            "Energy storage deployment doubled YoY"
        ],
        "growth_drivers": [
            "New Gigafactory openings",
            "Model 2 affordable vehicle platform",
            "FSD licensing to other automakers",
            "Energy storage business expansion",
            "Robotaxi network launch planned"
        ],
        "risks": [
            "Intense competition in EV market",
            "Regulatory challenges globally",
            "Supply chain dependencies",
            "Key person risk (CEO dependency)"
        ]
    },
    "SpaceX": {
        "valuation": "180B",
        "annual_revenue": "9B",
        "revenue_growth": "65%",
        "gross_margin": "35%",
        "customers": "Government agencies, commercial satellites, Starlink subscribers",
        "industry": "Aerospace & Satellite Internet",
        "key_products": [
            "Falcon 9 reusable rockets",
            "Starship next-gen spacecraft",
            "Starlink satellite internet",
            "Dragon crew/cargo spacecraft"
        ],
        "competitive_advantages": [
            "Reusable rocket technology",
            "Lowest cost per kg to orbit",
            "Vertical integration",
            "Starlink constellation (5,000+ satellites)"
        ],
        "recent_achievements": [
            "100+ successful Falcon 9 launches annually",
            "Starlink reaches 2.3M subscribers",
            "Starship development milestones",
            "NASA Artemis moon landing contract"
        ]
    },
    "OpenAI": {
        "valuation": "86B",
        "annual_revenue": "2B",
        "revenue_growth": "200%+",
        "users": "100M+ ChatGPT users",
        "industry": "Artificial Intelligence",
        "key_products": [
            "ChatGPT consumer product",
            "GPT-4 API for developers",
            "DALL-E image generation",
            "Enterprise AI solutions"
        ],
        "competitive_advantages": [
            "First-mover in consumer AI",
            "Microsoft partnership ($13B invested)",
            "Top AI research talent",
            "Massive training compute infrastructure"
        ]
    }
}

INVESTOR_DATA = {
    "BlackRock": {
        "aum": "10 Trillion",
        "type": "Asset Management",
        "investment_focus": [
            "Public equities",
            "Fixed income",
            "Multi-asset strategies",
            "Alternatives (private equity, infrastructure)"
        ],
        "tech_exposure": [
            "Large positions in FAANG stocks",
            "Growth equity in late-stage tech",
            "Infrastructure for digital economy"
        ],
        "investment_style": "Diversified with risk management focus",
        "typical_check_size": "100M - 5B",
        "board_involvement": "Active governance, ESG focus",
        "value_add": [
            "Global distribution network",
            "Risk analytics platform (Aladdin)",
            "ESG integration expertise",
            "Government and institutional relationships"
        ],
        "recent_tech_investments": [
            "Increased AI infrastructure exposure",
            "Clean energy and EV charging networks",
            "Digital infrastructure REITs"
        ],
        "investment_criteria": [
            "Strong unit economics",
            "Defensible competitive moats",
            "Experienced management teams",
            "Clear path to profitability or already profitable",
            "ESG compatibility"
        ]
    },
    "Sequoia Capital": {
        "aum": "85B",
        "type": "Venture Capital",
        "investment_focus": [
            "Early to growth stage tech",
            "AI and machine learning",
            "Enterprise SaaS",
            "Consumer technology",
            "Fintech and crypto"
        ],
        "portfolio_highlights": [
            "Apple, Google, Oracle (historical)",
            "Airbnb, DoorDash, Stripe (current)",
            "OpenAI, Databricks, Figma"
        ],
        "investment_style": "Long-term partnership, hands-on support",
        "typical_check_size": "1M - 500M",
        "board_involvement": "Deep operational support, board seats",
        "value_add": [
            "Network of founders and executives",
            "Talent recruitment support",
            "Go-to-market strategy",
            "Follow-on funding capability"
        ]
    },
    "Andreessen Horowitz": {
        "aum": "35B",
        "type": "Venture Capital",
        "investment_focus": [
            "Software and AI",
            "Crypto and Web3",
            "Bio and healthcare tech",
            "Consumer technology"
        ],
        "investment_style": "Thesis-driven, contrarian bets",
        "typical_check_size": "500K - 400M",
        "value_add": [
            "Dedicated operational teams (marketing, recruiting, etc.)",
            "Media and content creation",
            "Regulatory navigation",
            "Network effects in portfolio"
        ]
    }
}

def get_company_context(company_name: str) -> str:
    """
    Get formatted context data for a company
    """
    if company_name not in COMPANY_DATA:
        return f"No detailed data available for {company_name}. Operating as high-growth technology company."
    
    data = COMPANY_DATA[company_name]
    
    # Format as natural text for LLM injection
    context = f"""
Company: {company_name}
Market Position: {data.get('market_cap', data.get('valuation', 'Private'))} valuation/market cap
Annual Revenue: {data.get('annual_revenue', 'Not disclosed')}
Revenue Growth Rate: {data.get('revenue_growth', 'Strong growth')}
Gross Margin: {data.get('gross_margin', 'N/A')}
Industry: {data.get('industry', 'Technology')}

Key Products/Services:
{chr(10).join(f"- {p}" for p in data.get('key_products', []))}

Competitive Advantages:
{chr(10).join(f"- {a}" for a in data.get('competitive_advantages', []))}

Recent Achievements:
{chr(10).join(f"- {a}" for a in data.get('recent_achievements', []))}

Growth Drivers:
{chr(10).join(f"- {d}" for d in data.get('growth_drivers', []))}

Key Risks:
{chr(10).join(f"- {r}" for r in data.get('risks', []))}

Use this data to inform your negotiation strategy, justify valuation, and address investor concerns.
"""
    return context.strip()

def get_investor_context(investor_name: str) -> str:
    """
    Get formatted context data for an investor
    """
    if investor_name not in INVESTOR_DATA:
        return f"No detailed data available for {investor_name}. Operating as institutional investor."
    
    data = INVESTOR_DATA[investor_name]
    
    # Format as natural text for LLM injection
    context = f"""
Investor: {investor_name}
Assets Under Management: {data.get('aum', 'Multi-billion')}
Type: {data.get('type', 'Institutional Investor')}
Typical Check Size: {data.get('typical_check_size', 'Flexible')}

Investment Focus:
{chr(10).join(f"- {f}" for f in data.get('investment_focus', []))}

Investment Style: {data.get('investment_style', 'Value-focused')}

Value-Add Capabilities:
{chr(10).join(f"- {v}" for v in data.get('value_add', []))}

Investment Criteria:
{chr(10).join(f"- {c}" for c in data.get('investment_criteria', []))}

Recent Tech Activity:
{chr(10).join(f"- {r}" for r in data.get('recent_tech_investments', data.get('portfolio_highlights', []))[:3])}

Use this profile to evaluate the company's proposal, ask relevant questions, and negotiate appropriate terms.
"""
    return context.strip()

def add_company_data(company_name: str, data: dict):
    """
    Add new company data (for extensibility)
    """
    COMPANY_DATA[company_name] = data

def add_investor_data(investor_name: str, data: dict):
    """
    Add new investor data (for extensibility)
    """
    INVESTOR_DATA[investor_name] = data
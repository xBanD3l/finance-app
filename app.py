import os
from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client
from openai import OpenAI

client = OpenAI()


def generate_recommendations(goal: str, risk: str, custom_goal: str | None = None, 
                             investment_amount: str | None = None, time_horizon: str | None = None):
    """
    Generate personalized stock/ETF recommendations using OpenAI API.
    The prompt is enhanced to provide detailed, actionable, beginner-friendly explanations.
    """
    try:
        # Convert investment amount to number for calculations later
        investment_amount_num = float(investment_amount) if investment_amount else 0

        # Build the improved prompt
        prompt = f"""
You are a professional financial advisor. Recommend exactly 3 stocks or ETFs for an investor. 
Use the investor profile below to generate your recommendations.

INVESTOR PROFILE:
- Primary Goal: {goal.replace('_', ' ').title()}
- Risk Tolerance: {risk.title()}
- Investment Amount: ${investment_amount if investment_amount else 'Not specified'}
- Time Horizon: {time_horizon.replace('_', ' ').title() if time_horizon else 'Not specified'}
- Custom Goal: {custom_goal if custom_goal else 'None specified'}

INSTRUCTIONS:
1. Recommend exactly 3 stocks or ETFs.
2. Each recommendation must include:
   - Ticker symbol (e.g., AAPL, VTI)
   - Full company or fund name
   - Detailed explanation ("why") including:
       * How it fits the investor's goal and risk tolerance
       * Expected growth over their time horizon
       * Key fundamentals or market trends
       * Pros and cons
       * Simple, beginner-friendly language
   - Risk level (Low/Medium/High)
   - Expected return timeframe
   - Suggested portfolio allocation (percentage)
3. Provide actionable advice where possible, e.g., how to include it in a diversified portfolio or what to monitor while holding it.
4. Consider investment amount and time horizon in your recommendations.
5. Include a mix of individual stocks and ETFs when appropriate.
6. Format your response as JSON exactly like this:

{{
    "recommendations": [
        {{
            "ticker": "TICKER",
            "name": "Full Name",
            "why": "Detailed beginner-friendly explanation with actionable advice",
            "risk_level": "Low/Medium/High",
            "timeframe": "Expected return timeframe",
            "allocation": "Suggested percentage of portfolio"
        }}
    ]
}}
        """

        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional financial advisor providing clear, actionable investment advice. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        # Parse JSON response
        import json
        result = json.loads(response.choices[0].message.content)

        # Convert to expected template format
        picks = []
        for rec in result["recommendations"]:
            allocation_str = rec.get("allocation", "33%")
            allocation_percent = float(allocation_str.replace('%', '')) / 100
            dollar_amount = investment_amount_num * allocation_percent if investment_amount_num > 0 else 0

            picks.append({
                "ticker": rec["ticker"],
                "name": rec["name"],
                "why": rec["why"],
                "risk_level": rec.get("risk_level", "Medium"),
                "timeframe": rec.get("timeframe", "Long-term"),
                "allocation": allocation_str,
                "dollar_amount": dollar_amount
            })

        return picks

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return get_fallback_recommendations(goal, risk, custom_goal, investment_amount, time_horizon)


def get_fallback_recommendations(goal: str, risk: str, custom_goal: str | None = None, 
                               investment_amount: str | None = None, time_horizon: str | None = None):
    """
    Fallback recommendations when OpenAI API is unavailable.
    """
    investment_amount_num = float(investment_amount) if investment_amount else 0
    
    base_recommendations = {
        "build_wealth": [
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "why": "Broad market exposure for long-term wealth building", "risk_level": "Medium", "timeframe": "Long-term", "allocation": "40%"},
            {"ticker": "AAPL", "name": "Apple Inc.", "why": "Blue-chip stock with strong fundamentals and growth potential", "risk_level": "Medium", "timeframe": "Long-term", "allocation": "30%"},
            {"ticker": "VXUS", "name": "Vanguard Total International Stock ETF", "why": "International diversification for global growth", "risk_level": "Medium", "timeframe": "Long-term", "allocation": "30%"}
        ],
        "save_for_college": [
            {"ticker": "529", "name": "529 College Savings Plan", "why": "Tax-advantaged education savings with age-based allocation", "risk_level": "Low-Medium", "timeframe": "Medium-term", "allocation": "50%"},
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "why": "Growth potential for college fund with moderate risk", "risk_level": "Medium", "timeframe": "Medium-term", "allocation": "30%"},
            {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "why": "Stability and income for education savings", "risk_level": "Low", "timeframe": "Medium-term", "allocation": "20%"}
        ],
        "short_term": [
            {"ticker": "SGOV", "name": "iShares 0-3 Month Treasury Bond ETF", "why": "Ultra-short duration for capital preservation", "risk_level": "Low", "timeframe": "Short-term", "allocation": "40%"},
            {"ticker": "VGSH", "name": "Vanguard Short-Term Treasury ETF", "why": "Short-term government bonds for stability", "risk_level": "Low", "timeframe": "Short-term", "allocation": "35%"},
            {"ticker": "SHY", "name": "iShares 1-3 Year Treasury Bond ETF", "why": "Short-term treasury exposure with minimal risk", "risk_level": "Low", "timeframe": "Short-term", "allocation": "25%"}
        ],
        "retirement": [
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "why": "Broad market exposure for retirement growth", "risk_level": "Medium", "timeframe": "Long-term", "allocation": "50%"},
            {"ticker": "VXUS", "name": "Vanguard Total International Stock ETF", "why": "International diversification for retirement portfolio", "risk_level": "Medium", "timeframe": "Long-term", "allocation": "30%"},
            {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "why": "Bond allocation for retirement stability", "risk_level": "Low", "timeframe": "Long-term", "allocation": "20%"}
        ],
        "emergency_fund": [
            {"ticker": "SGOV", "name": "iShares 0-3 Month Treasury Bond ETF", "why": "Ultra-short duration for emergency liquidity", "risk_level": "Low", "timeframe": "Immediate", "allocation": "50%"},
            {"ticker": "SHY", "name": "iShares 1-3 Year Treasury Bond ETF", "why": "Short-term treasury bonds for emergency fund", "risk_level": "Low", "timeframe": "Short-term", "allocation": "30%"},
            {"ticker": "BIL", "name": "SPDR Bloomberg 1-3 Month T-Bill ETF", "why": "Treasury bills for emergency fund stability", "risk_level": "Low", "timeframe": "Short-term", "allocation": "20%"}
        ]
    }
    
    # Get base recommendations for the goal
    picks = base_recommendations.get(goal, base_recommendations["build_wealth"])
    
    # Adjust based on risk tolerance
    if risk == "low":
        # More conservative picks
        picks = [
            {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "why": "Conservative bond allocation for low risk tolerance", "risk_level": "Low", "timeframe": "Medium-term", "allocation": "40%"},
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "why": "Broad market exposure with lower risk", "risk_level": "Low-Medium", "timeframe": "Long-term", "allocation": "35%"},
            {"ticker": "VTEB", "name": "Vanguard Tax-Exempt Bond ETF", "why": "Tax-free municipal bonds for conservative investors", "risk_level": "Low", "timeframe": "Medium-term", "allocation": "25%"}
        ]
    elif risk == "high":
        # More aggressive picks
        picks = [
            {"ticker": "QQQ", "name": "Invesco QQQ Trust", "why": "Technology-heavy ETF for aggressive growth", "risk_level": "High", "timeframe": "Long-term", "allocation": "40%"},
            {"ticker": "ARKK", "name": "ARK Innovation ETF", "why": "Innovation-focused ETF for high growth potential", "risk_level": "High", "timeframe": "Long-term", "allocation": "30%"},
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "why": "Broad market exposure for aggressive investors", "risk_level": "Medium-High", "timeframe": "Long-term", "allocation": "30%"}
        ]
    
    # Add dollar amounts to each recommendation
    for pick in picks:
        allocation_str = pick["allocation"]
        allocation_percent = float(allocation_str.replace('%', '')) / 100
        dollar_amount = investment_amount_num * allocation_percent if investment_amount_num > 0 else 0
        pick["dollar_amount"] = dollar_amount
    
    return picks

@app.route("/")
def index():
    return render_template("index.html")

def parse_investment_amount(amount_str):
    """Parse investment amount string, handling commas and periods."""
    if not amount_str:
        return None
    
    # Remove commas and convert to float
    try:
        numeric_value = float(amount_str.replace(',', ''))
        # Validate range
        if 100 <= numeric_value <= 10000000:
            return str(int(numeric_value))  # Return as string for consistency
    except (ValueError, TypeError):
        pass
    
    return None

@app.route("/goals", methods=["GET", "POST"])
def goals():
    if request.method == "POST":
        goal = request.form.get("goal")
        risk = request.form.get("risk", "medium")
        custom_goal = request.form.get("custom_goal", "").strip() or None
        investment_amount_raw = request.form.get("investment_amount")
        time_horizon = request.form.get("time_horizon")
        
        # Parse and validate investment amount
        investment_amount = parse_investment_amount(investment_amount_raw)
        
        # Build query parameters
        params = {
            "goal": goal,
            "risk": risk,
            "custom_goal": custom_goal or "",
            "investment_amount": investment_amount or "",
            "time_horizon": time_horizon or ""
        }
        
        return redirect(url_for("results", **params))
    return render_template("goals.html")

@app.route("/results")
def results():
    goal = request.args.get("goal", "build_wealth")
    risk = request.args.get("risk", "medium")
    custom_goal = request.args.get("custom_goal") or None
    investment_amount = request.args.get("investment_amount")
    time_horizon = request.args.get("time_horizon")
    
    picks = generate_recommendations(goal, risk, custom_goal, investment_amount, time_horizon)
    return render_template("results.html", 
                         picks=picks, 
                         goal=goal, 
                         risk=risk, 
                         custom_goal=custom_goal,
                         investment_amount=investment_amount,
                         time_horizon=time_horizon)

if __name__ == "__main__":
    app.run(debug=True)

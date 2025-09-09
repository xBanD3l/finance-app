import os
import json
import csv
import io
import yfinance as yf
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
# from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize OpenAI client
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Portfolio data storage (in-memory for now)
PORTFOLIO_FILE = "portfolio_data.json"
NOTIFICATIONS_FILE = "notifications_data.json"
NOTIFICATION_PREFERENCES_FILE = "notification_preferences.json"

def load_portfolio_data():
    """Load portfolio data from JSON file or return empty dict."""
    try:
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading portfolio data: {e}")
    return {}

def save_portfolio_data(data):
    """Save portfolio data to JSON file."""
    try:
        with open(PORTFOLIO_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving portfolio data: {e}")

def load_notifications_data():
    """Load notifications data from JSON file or return empty list."""
    try:
        if os.path.exists(NOTIFICATIONS_FILE):
            with open(NOTIFICATIONS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading notifications data: {e}")
    return []

def save_notifications_data(data):
    """Save notifications data to JSON file."""
    try:
        with open(NOTIFICATIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving notifications data: {e}")

def load_notification_preferences():
    """Load notification preferences from JSON file or return default."""
    try:
        if os.path.exists(NOTIFICATION_PREFERENCES_FILE):
            with open(NOTIFICATION_PREFERENCES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading notification preferences: {e}")
    return {
        "price_change_threshold": 5.0,  # 5% price change
        "big_news_enabled": True,
        "earnings_alerts": True,
        "watchlist_stocks": [],
        "email_notifications": False,
        "push_notifications": True
    }

def save_notification_preferences(data):
    """Save notification preferences to JSON file."""
    try:
        with open(NOTIFICATION_PREFERENCES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving notification preferences: {e}")

def get_stock_price(ticker):
    """Fetch current stock price using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
    return None

def generate_sample_notifications():
    """Generate sample notifications for demonstration purposes."""
    sample_notifications = [
        {
            "id": "notif_1",
            "type": "price_change",
            "ticker": "AAPL",
            "title": "Price Alert: AAPL",
            "message": "AAPL rose 5.2% today, reaching $175.43",
            "timestamp": datetime.now().isoformat(),
            "read": False,
            "priority": "medium"
        },
        {
            "id": "notif_2", 
            "type": "earnings",
            "ticker": "TSLA",
            "title": "Earnings Report Released",
            "message": "Tesla Q4 earnings beat expectations with strong delivery numbers",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "read": False,
            "priority": "high"
        },
        {
            "id": "notif_3",
            "type": "news",
            "ticker": "NVDA",
            "title": "Big News Alert",
            "message": "NVIDIA announces new AI chip partnership with major cloud providers",
            "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
            "read": True,
            "priority": "high"
        },
        {
            "id": "notif_4",
            "type": "price_change",
            "ticker": "MSFT",
            "title": "Price Alert: MSFT", 
            "message": "MSFT dropped 3.1% today, now at $378.92",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "read": False,
            "priority": "medium"
        }
    ]
    return sample_notifications

def check_price_alerts():
    """Check for price alerts based on user preferences (placeholder function)."""
    preferences = load_notification_preferences()
    portfolio_data = load_portfolio_data()
    notifications = load_notifications_data()
    
    # This is a placeholder - in a real implementation, you'd compare current prices
    # with previous prices and check against thresholds
    print("Checking price alerts... (placeholder function)")
    
    # For demo purposes, we'll just return the existing notifications
    return notifications

def add_notification(notification_data):
    """Add a new notification to the system."""
    notifications = load_notifications_data()
    notification_data["id"] = f"notif_{len(notifications) + 1}"
    notification_data["timestamp"] = datetime.now().isoformat()
    notification_data["read"] = False
    notifications.insert(0, notification_data)  # Add to beginning
    
    # Keep only last 50 notifications
    if len(notifications) > 50:
        notifications = notifications[:50]
    
    save_notifications_data(notifications)
    return notification_data

def get_portfolio_performance_data():
    """Get current portfolio performance data for AI analysis."""
    portfolio_data = load_portfolio_data()
    if not portfolio_data:
        return None
    
    performance_data = {
        "timestamp": datetime.now().isoformat(),
        "stocks": [],
        "total_value": 0,
        "total_cost": 0,
        "total_gain_loss": 0,
        "total_gain_loss_pct": 0
    }
    
    total_value = 0
    total_cost = 0
    
    for ticker, data in portfolio_data.items():
        current_price = get_stock_price(ticker)
        if current_price:
            shares = data['shares']
            cost_per_share = data['purchase_price']
            
            current_value = shares * current_price
            cost_basis = shares * cost_per_share
            gain_loss = current_value - cost_basis
            gain_loss_pct = ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
            
            total_value += current_value
            total_cost += cost_basis
            
            performance_data["stocks"].append({
                "ticker": ticker,
                "shares": shares,
                "current_price": current_price,
                "purchase_price": cost_per_share,
                "current_value": current_value,
                "cost_basis": cost_basis,
                "gain_loss": gain_loss,
                "gain_loss_pct": gain_loss_pct
            })
    
    performance_data["total_value"] = total_value
    performance_data["total_cost"] = total_cost
    performance_data["total_gain_loss"] = total_value - total_cost
    performance_data["total_gain_loss_pct"] = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
    
    return performance_data

def generate_performance_insights(performance_data):
    """Generate AI-powered performance insights using OpenAI."""
    try:
        # Prepare the data for AI analysis
        stocks_summary = []
        for stock in performance_data["stocks"]:
            stocks_summary.append({
                "ticker": stock["ticker"],
                "current_price": f"${stock['current_price']:.2f}",
                "purchase_price": f"${stock['purchase_price']:.2f}",
                "gain_loss_pct": f"{stock['gain_loss_pct']:.1f}%",
                "gain_loss": f"${stock['gain_loss']:.2f}"
            })
        
        prompt = f"""
You are a financial advisor providing simple, beginner-friendly explanations of portfolio performance. 

PORTFOLIO PERFORMANCE DATA:
- Total Portfolio Value: ${performance_data['total_value']:.2f}
- Total Cost Basis: ${performance_data['total_cost']:.2f}
- Total Gain/Loss: ${performance_data['total_gain_loss']:.2f} ({performance_data['total_gain_loss_pct']:.1f}%)
- Analysis Date: {performance_data['timestamp'][:10]}

INDIVIDUAL STOCKS:
{json.dumps(stocks_summary, indent=2)}

INSTRUCTIONS:
1. Explain in simple, beginner-friendly terms why this portfolio has changed in value
2. Focus on the main drivers of performance (which stocks helped/hurt most)
3. Provide context about market conditions if relevant
4. Keep explanations under 200 words
5. Use encouraging, educational tone
6. Avoid financial jargon - explain terms when needed
7. Format as a clear, readable explanation

RESPONSE FORMAT:
Provide a clear explanation in 2-3 paragraphs covering:
- Overall portfolio performance summary
- Key stock movements and their impact
- Simple takeaway or lesson for the investor
        """
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a friendly financial advisor who explains complex investment concepts in simple, beginner-friendly terms. Always be encouraging and educational."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating AI insights: {e}")
        return get_fallback_insights(performance_data)

def get_fallback_insights(performance_data):
    """Fallback insights when OpenAI API is unavailable."""
    total_gain_loss_pct = performance_data['total_gain_loss_pct']
    
    if total_gain_loss_pct > 2:
        sentiment = "positive"
        explanation = f"Your portfolio is up {total_gain_loss_pct:.1f}% today! This is a strong performance."
    elif total_gain_loss_pct < -2:
        sentiment = "negative"
        explanation = f"Your portfolio is down {abs(total_gain_loss_pct):.1f}% today. This is normal market volatility."
    else:
        sentiment = "neutral"
        explanation = f"Your portfolio is relatively stable today with a {total_gain_loss_pct:.1f}% change."
    
    # Find the biggest movers
    biggest_gainer = max(performance_data['stocks'], key=lambda x: x['gain_loss_pct'])
    biggest_loser = min(performance_data['stocks'], key=lambda x: x['gain_loss_pct'])
    
    insights = f"""
{explanation}

Your biggest gainer today was {biggest_gainer['ticker']} with a {biggest_gainer['gain_loss_pct']:.1f}% increase, while {biggest_loser['ticker']} was your biggest decliner at {biggest_loser['gain_loss_pct']:.1f}%.

Remember, short-term fluctuations are normal in investing. Focus on your long-term goals and maintain a diversified portfolio.
    """.strip()
    
    return insights

def generate_pdf_report(portfolio_data, performance_data, recommendations=None):
    """Generate a PDF report of the portfolio."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4f8cff')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#4f8cff')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )
    
    # Build the story
    story = []
    
    # Title
    story.append(Paragraph("Stockly Portfolio Report", title_style))
    story.append(Spacer(1, 12))
    
    # Date
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Portfolio Summary
    story.append(Paragraph("Portfolio Summary", heading_style))
    
    if performance_data:
        summary_data = [
            ['Metric', 'Value'],
            ['Total Portfolio Value', f"${performance_data['total_value']:.2f}"],
            ['Total Cost Basis', f"${performance_data['total_cost']:.2f}"],
            ['Total Gain/Loss', f"${performance_data['total_gain_loss']:.2f}"],
            ['Total Return %', f"{performance_data['total_gain_loss_pct']:.2f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f8cff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
    
    # Individual Holdings
    story.append(Paragraph("Individual Holdings", heading_style))
    
    if performance_data and performance_data['stocks']:
        holdings_data = [['Ticker', 'Shares', 'Current Price', 'Purchase Price', 'Current Value', 'Gain/Loss', 'Return %']]
        
        for stock in performance_data['stocks']:
            holdings_data.append([
                stock['ticker'],
                str(stock['shares']),
                f"${stock['current_price']:.2f}",
                f"${stock['purchase_price']:.2f}",
                f"${stock['current_value']:.2f}",
                f"${stock['gain_loss']:.2f}",
                f"{stock['gain_loss_pct']:.2f}%"
            ])
        
        holdings_table = Table(holdings_data, colWidths=[0.8*inch, 0.6*inch, 1*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
        holdings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f8cff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(holdings_table)
        story.append(Spacer(1, 20))
    
    # Recommendations Section (if available)
    if recommendations:
        story.append(Paragraph("Investment Recommendations", heading_style))
        
        for i, rec in enumerate(recommendations[:3], 1):  # Show top 3 recommendations
            story.append(Paragraph(f"{i}. {rec['ticker']} - {rec['name']}", normal_style))
            story.append(Paragraph(f"   Allocation: {rec['allocation']}", normal_style))
            story.append(Paragraph(f"   Reason: {rec['why'][:100]}...", normal_style))
            story.append(Spacer(1, 8))
    
    # Disclaimer
    story.append(Spacer(1, 20))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("This report is for educational purposes only and should not be considered as financial advice.", disclaimer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_csv_report(portfolio_data, performance_data):
    """Generate a CSV report of the portfolio."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Ticker', 'Shares', 'Purchase Price', 'Current Price', 'Current Value', 'Cost Basis', 'Gain/Loss', 'Gain/Loss %', 'Date Added'])
    
    # Write portfolio data
    if performance_data and performance_data['stocks']:
        for stock in performance_data['stocks']:
            # Get original portfolio data for date_added
            original_data = portfolio_data.get(stock['ticker'], {})
            date_added = original_data.get('date_added', 'Unknown')
            
            writer.writerow([
                stock['ticker'],
                stock['shares'],
                f"{stock['purchase_price']:.2f}",
                f"{stock['current_price']:.2f}",
                f"{stock['current_value']:.2f}",
                f"{stock['cost_basis']:.2f}",
                f"{stock['gain_loss']:.2f}",
                f"{stock['gain_loss_pct']:.2f}",
                date_added[:10] if date_added != 'Unknown' else 'Unknown'
            ])
    
    # Add summary row
    if performance_data:
        writer.writerow([])  # Empty row
        writer.writerow(['SUMMARY', '', '', '', '', '', '', '', ''])
        writer.writerow(['Total Portfolio Value', '', '', '', f"{performance_data['total_value']:.2f}", '', '', '', ''])
        writer.writerow(['Total Cost Basis', '', '', '', '', f"{performance_data['total_cost']:.2f}", '', '', ''])
        writer.writerow(['Total Gain/Loss', '', '', '', '', '', f"{performance_data['total_gain_loss']:.2f}", '', ''])
        writer.writerow(['Total Return %', '', '', '', '', '', '', f"{performance_data['total_gain_loss_pct']:.2f}", ''])
    
    output.seek(0)
    return output.getvalue()

def calculate_portfolio_metrics(holdings):
    """Calculate portfolio metrics."""
    total_value = 0
    total_cost = 0
    stock_values = {}
    
    for ticker, data in holdings.items():
        current_price = get_stock_price(ticker)
        if current_price:
            shares = data['shares']
            cost_per_share = data['purchase_price']
            
            current_value = shares * current_price
            cost_basis = shares * cost_per_share
            
            total_value += current_value
            total_cost += cost_basis
            
            stock_values[ticker] = {
                'current_price': current_price,
                'current_value': current_value,
                'cost_basis': cost_basis,
                'gain_loss': current_value - cost_basis,
                'gain_loss_pct': ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0,
                'shares': shares,
                'purchase_price': cost_per_share
            }
    
    total_gain_loss = total_value - total_cost
    total_gain_loss_pct = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    return {
        'total_value': total_value,
        'total_cost': total_cost,
        'total_gain_loss': total_gain_loss,
        'total_gain_loss_pct': total_gain_loss_pct,
        'stock_values': stock_values
    }

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

@app.route("/portfolio")
def portfolio():
    """Display portfolio overview."""
    portfolio_data = load_portfolio_data()
    if not portfolio_data:
        return render_template("portfolio.html", holdings={}, metrics=None, empty=True)
    
    metrics = calculate_portfolio_metrics(portfolio_data)
    return render_template("portfolio.html", holdings=portfolio_data, metrics=metrics, empty=False)

@app.route("/portfolio/add", methods=["GET", "POST"])
def add_holding():
    """Add a new stock holding to portfolio."""
    if request.method == "POST":
        ticker = request.form.get("ticker", "").upper().strip()
        shares = float(request.form.get("shares", 0))
        purchase_price = float(request.form.get("purchase_price", 0))
        
        if ticker and shares > 0 and purchase_price > 0:
            portfolio_data = load_portfolio_data()
            portfolio_data[ticker] = {
                "shares": shares,
                "purchase_price": purchase_price,
                "date_added": datetime.now().isoformat()
            }
            save_portfolio_data(portfolio_data)
            return redirect(url_for("portfolio"))
    
    return render_template("add_holding.html")

@app.route("/portfolio/edit/<ticker>", methods=["GET", "POST"])
def edit_holding(ticker):
    """Edit an existing stock holding."""
    portfolio_data = load_portfolio_data()
    
    if request.method == "POST":
        shares = float(request.form.get("shares", 0))
        purchase_price = float(request.form.get("purchase_price", 0))
        
        if shares > 0 and purchase_price > 0:
            portfolio_data[ticker] = {
                "shares": shares,
                "purchase_price": purchase_price,
                "date_added": portfolio_data[ticker].get("date_added", datetime.now().isoformat())
            }
            save_portfolio_data(portfolio_data)
            return redirect(url_for("portfolio"))
    
    if ticker not in portfolio_data:
        return redirect(url_for("portfolio"))
    
    holding = portfolio_data[ticker]
    return render_template("edit_holding.html", ticker=ticker, holding=holding)

@app.route("/portfolio/delete/<ticker>", methods=["POST"])
def delete_holding(ticker):
    """Delete a stock holding from portfolio."""
    portfolio_data = load_portfolio_data()
    if ticker in portfolio_data:
        del portfolio_data[ticker]
        save_portfolio_data(portfolio_data)
    return redirect(url_for("portfolio"))

@app.route("/portfolio/api/prices")
def portfolio_api_prices():
    """API endpoint to get current prices for all holdings."""
    portfolio_data = load_portfolio_data()
    prices = {}
    
    for ticker in portfolio_data.keys():
        price = get_stock_price(ticker)
        if price:
            prices[ticker] = price
    
    return jsonify(prices)

@app.route("/portfolio/api/history/<ticker>")
def portfolio_api_history(ticker):
    """API endpoint to get historical data for a stock."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")  # Last month
        if not hist.empty:
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'price': float(row['Close'])
                })
            return jsonify(data)
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
    
    return jsonify([])

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

@app.route("/notifications")
def notifications():
    """Display notifications page."""
    notifications_data = load_notifications_data()
    preferences = load_notification_preferences()
    
    # If no notifications exist, generate sample ones
    if not notifications_data:
        notifications_data = generate_sample_notifications()
        save_notifications_data(notifications_data)
    
    return render_template("notifications.html", 
                         notifications=notifications_data,
                         preferences=preferences)

@app.route("/notifications/preferences", methods=["GET", "POST"])
def notification_preferences():
    """Manage notification preferences."""
    if request.method == "POST":
        preferences = {
            "price_change_threshold": float(request.form.get("price_change_threshold", 5.0)),
            "big_news_enabled": request.form.get("big_news_enabled") == "on",
            "earnings_alerts": request.form.get("earnings_alerts") == "on",
            "watchlist_stocks": request.form.getlist("watchlist_stocks"),
            "email_notifications": request.form.get("email_notifications") == "on",
            "push_notifications": request.form.get("push_notifications") == "on"
        }
        save_notification_preferences(preferences)
        return redirect(url_for("notifications"))
    
    preferences = load_notification_preferences()
    portfolio_data = load_portfolio_data()
    return render_template("notification_preferences.html", 
                         preferences=preferences,
                         portfolio_stocks=list(portfolio_data.keys()))

@app.route("/notifications/mark_read/<notification_id>", methods=["POST"])
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notifications_data = load_notifications_data()
    for notification in notifications_data:
        if notification["id"] == notification_id:
            notification["read"] = True
            break
    save_notifications_data(notifications_data)
    return jsonify({"success": True})

@app.route("/notifications/clear_all", methods=["POST"])
def clear_all_notifications():
    """Clear all notifications."""
    save_notifications_data([])
    return jsonify({"success": True})

@app.route("/notifications/api/check")
def check_notifications_api():
    """API endpoint to check for new notifications (placeholder)."""
    notifications_data = check_price_alerts()
    unread_count = sum(1 for n in notifications_data if not n.get("read", False))
    return jsonify({
        "notifications": notifications_data[:5],  # Return last 5
        "unread_count": unread_count
    })

@app.route("/insights")
def insights():
    """Display AI Performance Insights page."""
    portfolio_data = load_portfolio_data()
    
    if not portfolio_data:
        return render_template("insights.html", 
                             has_portfolio=False,
                             performance_data=None,
                             insights=None)
    
    # Get performance data
    performance_data = get_portfolio_performance_data()
    
    # Generate AI insights
    insights = None
    if performance_data:
        insights = generate_performance_insights(performance_data)
    
    return render_template("insights.html", 
                         has_portfolio=True,
                         performance_data=performance_data,
                         insights=insights)

@app.route("/insights/generate", methods=["POST"])
def generate_insights():
    """Generate new AI insights (AJAX endpoint)."""
    portfolio_data = load_portfolio_data()
    
    if not portfolio_data:
        return jsonify({"error": "No portfolio data available"}), 400
    
    performance_data = get_portfolio_performance_data()
    
    if not performance_data:
        return jsonify({"error": "Unable to fetch portfolio performance data"}), 500
    
    insights = generate_performance_insights(performance_data)
    
    return jsonify({
        "success": True,
        "insights": insights,
        "performance_data": performance_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/insights/api/performance")
def insights_api_performance():
    """API endpoint to get current portfolio performance data."""
    portfolio_data = load_portfolio_data()
    
    if not portfolio_data:
        return jsonify({"error": "No portfolio data available"}), 400
    
    performance_data = get_portfolio_performance_data()
    
    if not performance_data:
        return jsonify({"error": "Unable to fetch performance data"}), 500
    
    return jsonify(performance_data)

@app.route("/export/pdf")
def export_pdf():
    """Export portfolio as PDF report."""
    portfolio_data = load_portfolio_data()
    
    if not portfolio_data:
        return jsonify({"error": "No portfolio data available"}), 400
    
    # Get performance data
    performance_data = get_portfolio_performance_data()
    
    if not performance_data:
        return jsonify({"error": "Unable to fetch performance data"}), 500
    
    # Get sample recommendations for the report
    recommendations = get_fallback_recommendations("build_wealth", "medium")
    
    # Generate PDF
    pdf_buffer = generate_pdf_report(portfolio_data, performance_data, recommendations)
    
    # Create response
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=stockly_portfolio_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    return response

@app.route("/export/csv")
def export_csv():
    """Export portfolio as CSV report."""
    portfolio_data = load_portfolio_data()
    
    if not portfolio_data:
        return jsonify({"error": "No portfolio data available"}), 400
    
    # Get performance data
    performance_data = get_portfolio_performance_data()
    
    if not performance_data:
        return jsonify({"error": "Unable to fetch performance data"}), 500
    
    # Generate CSV
    csv_data = generate_csv_report(portfolio_data, performance_data)
    
    # Create response
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=stockly_portfolio_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response

@app.route("/export/preview")
def export_preview():
    """Preview export options (placeholder for Coming Soon functionality)."""
    portfolio_data = load_portfolio_data()
    
    if not portfolio_data:
        return render_template("export_preview.html", has_portfolio=False)
    
    performance_data = get_portfolio_performance_data()
    
    return render_template("export_preview.html", 
                         has_portfolio=True,
                         performance_data=performance_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

    
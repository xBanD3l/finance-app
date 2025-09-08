# Finance App - AI-Powered Investment Recommendations

A Flask web application that provides personalized stock and ETF recommendations using OpenAI's GPT-4 API.

## Features

- **Interactive Goals Form**: Users can specify their investment goals, risk tolerance, investment amount, and time horizon
- **AI-Powered Recommendations**: Uses OpenAI GPT-4 to generate personalized investment recommendations based on user profile
- **Comprehensive Results**: Displays detailed recommendations with risk levels, timeframes, and allocation suggestions
- **Fallback System**: Includes robust fallback recommendations when OpenAI API is unavailable
- **Modern UI**: Clean, responsive design with dark theme

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure OpenAI API Key

1. Copy the environment template:
   ```bash
   copy .env.example .env
   ```

2. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

3. Edit `.env` file and replace `your_openai_api_key_here` with your actual API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## How It Works

1. **Goals Page**: Users fill out a comprehensive form with:
   - Primary investment goal (build wealth, save for college, etc.)
   - Risk tolerance (Conservative, Moderate, Aggressive)
   - Investment amount (optional)
   - Time horizon (optional)
   - Custom goal description (optional)

2. **AI Processing**: The form data is sent to OpenAI GPT-4 with a detailed prompt that includes:
   - User's investment profile
   - Risk tolerance
   - Investment amount
   - Time horizon
   - Custom goals

3. **Results Page**: Displays personalized recommendations with:
   - Ticker symbol and company/fund name
   - Detailed explanation of why each investment fits the user's profile
   - Risk level assessment
   - Expected timeframe
   - Suggested portfolio allocation
   - Research links for each recommendation

## API Integration

The app uses OpenAI's Chat Completions API with GPT-4 model. The prompt is structured to ensure consistent JSON responses with all required fields.

### Fallback System

If the OpenAI API is unavailable or returns an error, the app automatically falls back to predefined recommendations based on the user's goals and risk tolerance.

## File Structure

```
finance-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── static/
│   ├── style.css         # CSS styles
│   └── script.js        # JavaScript functionality
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── goals.html        # Investment goals form
    └── results.html      # Results display
```

## Customization

### Adding New Investment Goals

To add new investment goals, update the `base_recommendations` dictionary in the `get_fallback_recommendations()` function in `app.py`.

### Modifying AI Prompts

The AI prompt can be customized in the `generate_recommendations()` function to change the style or focus of recommendations.

### Styling

The application uses CSS custom properties for easy theming. Modify the `:root` variables in `static/style.css` to change colors and styling.

## Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already included in `.gitignore`
- API keys should be kept secure and not shared

## Disclaimer

This application is for educational purposes only. The recommendations generated are not financial advice and should not be used as the sole basis for investment decisions. Always consult with qualified financial advisors before making investment choices.

GO THOUGH SEO AI AGENT PLAN .PDF
# AI Keyword Agent

This project is an AI-powered keyword research tool that combines Google Gemini (for keyword expansion) and SerpApi (for Google autocomplete suggestions) to generate and score SEO keyword ideas. It outputs the top 50 keywords to a CSV file.

## Features
- Enter a seed keyword and get a broad list of related queries.
- Uses Gemini AI to generate semantically similar keywords.
- Uses SerpApi to fetch Google autocomplete suggestions.
- Fetches real search volume and competition if you have access to Google Ads API with a developer token.
- Scores and ranks keywords using a customizable formula.
- Outputs results to a CSV file.

## Setup
1. Clone this repository:
   ```sh
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your API keys:
   ```env
   SERPAPI_KEY=your_serpapi_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## Usage
Run the script and follow the prompts:
```sh
python serpapi_keyword_suggestions.py
```
- Enter your seed keyword when prompted.
- The script will generate and score keywords, then save the top 50 to `top_keywords.csv`.

## How It Works
1. **User Input:** Enter a seed keyword.
2. **Gemini AI:** Generates a list of related keywords.
3. **SerpApi:** Fetches Google autocomplete suggestions for each keyword.
4. **(BEST ONE) Google Ads API:** If you have a Google Ads developer token and access, you can modify the script to fetch real search volume and competition for each keyword. This requires setting up a Google Ads API project and using your developer token.
5. **Scoring:** Each keyword is scored using the formula `(search_volume * sv_weight) - (competition * comp_weight)`.
6. **Output:** The top 50 keywords are saved to `top_keywords.csv`.

## Using Google Ads API for Real Data
- If you have a Google Ads developer token (with Basic or Standard access), you can modify the script to fetch real search volume and competition data for each keyword using the Google Ads API.
- This requires setting up OAuth2 credentials and updating the script to call the Keyword Plan Idea Service.
- When enabled, the script will use real metrics instead of simulated ones for scoring and ranking.

## Requirements
- Python 3.7+
- `requests`, `pandas`, `google-generativeai`, `python-dotenv`


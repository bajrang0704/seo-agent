# works when we have a google ads account in real account
import os
import argparse
import pandas as pd
from dotenv import load_dotenv
import random
import google.generativeai as genai
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from pytrends.request import TrendReq
import requests

# Load environment variables
try:
    load_dotenv()
    print("[INFO] Loaded .env file.")
except Exception as e:
    print(f"[ERROR] Failed to load .env file: {e}")

GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GEMINI_API_KEY:
    print("[ERROR] GOOGLE_API_KEY not found in environment variables.")
    exit(1)
try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("[INFO] Configured Gemini API.")
except Exception as e:
    print(f"[ERROR] Failed to configure Gemini API: {e}")
    exit(1)

# --- AI Keyword Expansion ---
def generate_keywords(seed, n=100):
    prompt = f"Generate a list of {n} SEO keywords related to '{seed}'. Return only the keywords, comma-separated."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("[INFO] Generating keywords using Gemini...")
        response = model.generate_content(prompt)
        keywords = response.text
        # Split and clean
        keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        print(f"[INFO] Gemini returned {len(keywords)} keywords.")
        return list(set(keywords))  # Remove duplicates
    except Exception as e:
        print(f"[ERROR] Failed to generate keywords: {e}")
        return []

# --- Google Ads API: Fetch Real SEO Metrics ---
def fetch_seo_metrics(keywords, customer_id):
    # Load Google Ads API config
    try:
        google_ads_client = GoogleAdsClient.load_from_storage('google-ads.yml')
        print("[INFO] Loaded Google Ads client.")
    except Exception as e:
        print(f"[ERROR] Failed to load Google Ads config: {e}")
        return pd.DataFrame(columns=['keyword', 'search_volume', 'competition'])
    try:
        service = google_ads_client.get_service("KeywordPlanIdeaService")
        location_ids = [2840]  # 2840 = United States
        language_id = 1000     # 1000 = English
        keyword_plan_network = (
            google_ads_client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
        )
        request = {
            "customer_id": customer_id,
            "language": "languageConstants/1000",
            "geo_target_constants": [f"geoTargetConstants/{location_ids[0]}"],
            "keyword_plan_network": keyword_plan_network,
            "keyword_seed": {"keywords": keywords},
        }
        response = service.generate_keyword_ideas(request=request)
        data = []
        for idea in response:
            try:
                comp = float(idea.keyword_idea_metrics.competition)
            except Exception as ce:
                print(f"[WARN] Could not convert competition for {idea.text}: {ce}")
                comp = 0.0
            data.append({
                'keyword': idea.text,
                'search_volume': idea.keyword_idea_metrics.avg_monthly_searches,
                'competition': comp,
            })
        print(f"[INFO] Retrieved {len(data)} keyword ideas from Google Ads.")
        return pd.DataFrame(data)
    except GoogleAdsException as ex:
        print(f"[ERROR] Google Ads API error: {ex}")
        return pd.DataFrame(columns=['keyword', 'search_volume', 'competition'])
    except Exception as e:
        print(f"[ERROR] Unexpected error during Google Ads API call: {e}")
        return pd.DataFrame(columns=['keyword', 'search_volume', 'competition'])

# --- Scoring ---
def score_keywords(df, sv_weight=1.0, comp_weight=1000.0):
    df['score'] = df['search_volume'] * sv_weight - df['competition'] * comp_weight
    return df.sort_values(by='score', ascending=False)

def get_serpapi_suggestions(seed_keyword, serpapi_key):
    params = {
        "engine": "google_autocomplete",
        "q": seed_keyword,
        "api_key": serpapi_key
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    suggestions = []
    if "suggestions" in data:
        for item in data["suggestions"]:
            suggestions.append(item["value"])
    return suggestions

# --- CLI ---
def main():
    parser = argparse.ArgumentParser(description='AI SEO Keyword Research Agent')
    parser.add_argument('seed', type=str, help='Seed keyword')
    parser.add_argument('--output', type=str, default='keywords.csv', help='Output CSV file')
    parser.add_argument('--customer_id', type=str, required=True, help='Google Ads customer ID (digits only)')
    args = parser.parse_args()

    print(f"Generating keywords for: {args.seed}")
    keywords = generate_keywords(args.seed)
    if not keywords:
        print("[ERROR] No keywords generated. Exiting.")
        return
    print(f"Generated {len(keywords)} keywords. Fetching SEO metrics from Google Ads...")

    df = fetch_seo_metrics(keywords, args.customer_id)
    if df.empty:
        print("[WARN] No keyword metrics found from Google Ads. Saving only Gemini-generated keywords.")
        pd.DataFrame({'keyword': keywords}).to_csv(args.output, index=False)
        print(f"[INFO] All generated keywords saved to {args.output}")
        return
    df = score_keywords(df)
    top50 = df.head(50)
    try:
        top50.to_csv(args.output, index=False)
        print(f"[INFO] Top 50 keywords saved to {args.output}")
    except Exception as e:
        print(f"[ERROR] Failed to save CSV: {e}")

if __name__ == '__main__':
    main() 
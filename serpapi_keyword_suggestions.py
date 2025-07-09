import requests
import pandas as pd
import random
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 1. User Input
seed = input("Enter a seed keyword: ").strip()
serpapi_key = os.getenv('SERPAPI_KEY')
if not serpapi_key:
    serpapi_key = input("Enter your SerpApi API key: ").strip()
gemini_api_key = os.getenv('GOOGLE_API_KEY')
if not gemini_api_key:
    gemini_api_key = input("Enter your Gemini API key: ").strip()
genai.configure(api_key=gemini_api_key)

# 2. AI Model (Gemini) - Real API call

def generate_keywords_gemini(seed):
    prompt = f"Generate a list of 20 SEO keywords related to '{seed}'. Return only the keywords, comma-separated."
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    keywords = response.text
    # Split and clean
    keywords = [k.strip() for k in keywords.split(',') if k.strip()]
    return list(set(keywords))  # Remove duplicates

# 3. Fetch API Data (SerpApi for autocomplete suggestions)
def get_serpapi_suggestions(keyword, serpapi_key):
    params = {
        "engine": "google_autocomplete",
        "q": keyword,
        "api_key": serpapi_key
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    suggestions = []
    if "suggestions" in data:
        for item in data["suggestions"]:
            suggestions.append(item["value"])
    return suggestions

# --- Main Process ---
# Step 1: Get Gemini-generated keywords
keywords_gemini = generate_keywords_gemini(seed)

# Step 2: For each Gemini keyword, get SerpApi suggestions
all_keywords = set(keywords_gemini)
for kw in keywords_gemini:
    suggestions = get_serpapi_suggestions(kw, serpapi_key)
    all_keywords.update(suggestions)

# Step 3: Assign simulated search volume and competition
results = []
for kw in all_keywords:
    # Simulate search volume and competition (replace with real API if available)
    search_volume = random.randint(100, 10000)
    competition = round(random.uniform(0, 1), 2)
    results.append({
        "keyword": kw,
        "search_volume": search_volume,
        "competition": competition
    })

# Step 4: Score and sort
sv_weight = 1.0
comp_weight = 1000.0
for r in results:
    r["score"] = r["search_volume"] * sv_weight - r["competition"] * comp_weight

df = pd.DataFrame(results)
df = df.sort_values(by="score", ascending=False)
top50 = df.head(50)
top50.to_csv("top_keywords.csv", index=False)
print("Top 50 keywords saved to top_keywords.csv")
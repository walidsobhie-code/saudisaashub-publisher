#!/usr/bin/env python3
"""
SaudiSaaSHub AI Automation
Uses OpenRouter (free AI models) for:
1. Content Writer
2. Social Media Writer
3. SEO Analyzer
4. Competitor Analyzer
"""

import os
import requests
import feedparser
import json
import re
from datetime import datetime

# Configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

SITE_URL = "https://saudisaashub.pages.dev"

# Use free models from OpenRouter
MODELS = [
    "openchat/openchat-7b:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free"
]

def call_ai(prompt, model="openchat/openchat-7b:free"):
    """Call OpenRouter AI"""
    if not OPENROUTER_API_KEY:
        return None
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,
        "X-Title": "SaudiSaaSHub"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None

def send_telegram(message):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

# ============ AI FEATURES ============

def ai_content_writer(topic, category):
    """Generate article content using AI"""
    prompt = f"""Write a professional Arabic article about: {topic}
Category: {category}
Requirements:
- 800+ words
- Professional tone
- Include introduction, body sections, conclusion
- Use Arabic headings (## )
- Include statistics if relevant to Saudi market
- Bilingual hashtags at the end
Write in Arabic."""
    
    content = call_ai(prompt)
    return content if content else "AI content generation failed"

def ai_social_writer(article_title, article_summary):
    """Generate social media posts using AI"""
    prompt = f"""Generate social media posts for this article:
Title: {article_title}
Summary: {article_summary}

Write:
1. Twitter (short, punchy with hook in Saudi Arabic dialect)
2. LinkedIn (professional, story-style)
3. Instagram (emotional, hashtags)

Include Saudi Arabic hooks like: وش رايك؟ - هل سمعت - والله تستاهل

Write in Arabic with some English hashtags."""
    
    posts = call_ai(prompt)
    return posts if posts else "AI post generation failed"

def ai_seo_analyzer():
    """Analyze site SEO using AI"""
    # Get site data
    try:
        r = requests.get(SITE_URL, timeout=10)
        site_status = "UP" if r.status_code == 200 else f"ERROR {r.status_code}"
    except:
        site_status = "DOWN"
    
    # Get article count
    feed = feedparser.parse(f"{SITE_URL}/feed.xml")
    article_count = len(feed.entries)
    
    prompt = f"""Analyze this Saudi SaaS website and provide SEO recommendations:

Site Status: {site_status}
Articles: {article_count}
URL: {SITE_URL}

Provide:
1. SEO score (0-100)
2. Top 5 recommendations
3. Keyword opportunities for Saudi market
4. Content gaps

Write in Arabic."""
    
    analysis = call_ai(prompt)
    return analysis if analysis else "SEO analysis failed"

def ai_competitor_analyzer():
    """Analyze competitors using AI"""
    competitors = ["salla.sa", "zid.sa", "tamara.co", "lucidya.com"]
    
    prompt = f"""Analyze these Saudi SaaS/FinTech competitors:
{', '.join(competitors)}

Provide:
1. Their content strategies
2. Keywords they likely target
3. Content gaps we can exploit
4. Backlink opportunities
5. Topics we should cover

Focus on Saudi market. Write in Arabic."""
    
    analysis = call_ai(prompt)
    return analysis if analysis else "Competitor analysis failed"

# ============ MAIN FUNCTIONS ============

def weekly_report():
    """Generate comprehensive weekly report"""
    report = "📊 *AI-Powered Weekly Report*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # Site Status
    try:
        r = requests.get(SITE_URL, timeout=10)
        status = "✅ UP" if r.status_code == 200 else f"❌ {r.status_code}"
    except:
        status = "❌ DOWN"
    
    feed = feedparser.parse(f"{SITE_URL}/feed.xml")
    articles = len(feed.entries)
    
    report += f"🏠 *Site Status:* {status}\n"
    report += f"📄 *Articles:* {articles}\n\n"
    
    # Run AI Analysis
    report += "🔍 *Running AI SEO Analysis...*\n"
    seo = ai_seo_analyzer()
    if seo:
        report += f"\n{seo}\n"
    
    report += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    report += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n"
    report += "#SaudiSaaS"
    
    return report

def generate_social_posts():
    """Generate social posts for latest articles"""
    feed = feedparser.parse(f"{SITE_URL}/feed.xml")
    
    if not feed.entries:
        return "No articles found!"
    
    latest = feed.entries[0]
    title = latest.get('title', '')
    summary = re.sub('<[^<]+?>', '', latest.get('summary', ''))[:200]
    
    posts = f"📰 *AI-Generated Posts*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    posts += f"Article: {title}\n\n"
    
    ai_posts = ai_social_writer(title, summary)
    if ai_posts:
        posts += ai_posts
    else:
        posts += "❌ AI generation failed"
    
    return posts

# ============ MAIN ============

def main():
    mode = os.environ.get("MODE", "report")
    
    print(f"Running mode: {mode}")
    
    if mode == "report":
        result = weekly_report()
    elif mode == "social":
        result = generate_social_posts()
    elif mode == "seo":
        result = ai_seo_analyzer()
    elif mode == "competitor":
        result = ai_competitor_analyzer()
    else:
        result = "Unknown mode"
    
    print(result)
    send_telegram(result)

if __name__ == "__main__":
    main()

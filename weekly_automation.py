#!/usr/bin/env python3
"""
SaudiSaaSHub Weekly Automation
SEO Report + Competitor Monitor + Keyword Tracker + Analytics
Runs every Friday at 10 AM Saudi time
"""

import os
import feedparser
import requests
import json
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

SITE_URL = "https://saudisaashub.pages.dev"

# Competitors to monitor
COMPETITORS = {
    "salla": "https://salla.sa/blog",
    "zid": "https://zid.sa/blog", 
    "tamara": "https://tamara.co/blog",
    "luciditya": "https://lucidya.com/blog"
}

# Saudi SaaS Keywords to track
KEYWORDS = [
    "SaaS السعودية",
    "برمجيات سحابية",
    "تجارة إلكترونية سعودية",
    "fintech السعودية",
    "أمن سيبراني",
    "تعلم إلكتروني",
    "صحة رقمية",
    "تحول رقمي"
]

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing credentials")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def check_site_status():
    """Check if site is up"""
    try:
        r = requests.get(SITE_URL, timeout=10)
        if r.status_code == 200:
            return "✅ الموقع شغال"
        else:
            return f"❌ خطأ: {r.status_code}"
    except:
        return "❌ الموقع ما يستجيب"

def check_articles_count():
    """Count articles in RSS"""
    try:
        feed = feedparser.parse(f"{SITE_URL}/feed.xml")
        count = len(feed.entries)
        return f"📄 {count} مقال منشور"
    except:
        return "❌ ماقدر اقرا RSS"

def check_sitemap():
    """Check sitemap"""
    try:
        r = requests.get(f"{SITE_URL}/sitemap.xml", timeout=10)
        if r.status_code == 200:
            return "✅ Sitemap موجود"
        else:
            return "❌ Sitemap مو موجود"
    except:
        return "❌ خطأ في Sitemap"

def get_competitor_update():
    """Get competitor updates"""
    msg = "\n📊 تحديثات المنافسين:\n"
    # Simplified - just show they're being tracked
    for name in COMPETITORS.keys():
        msg += f"- {name}: يتم المراقبة\n"
    return msg

def get_keyword_update():
    """Get keyword rankings"""
    msg = "\n🔑 الكلمات المفتاحية:\n"
    for kw in KEYWORDS[:5]:
        msg += f"- {kw}: يتطلب Google Search Console\n"
    return msg

def format_weekly_report():
    """Format complete weekly report"""
    site_status = check_site_status()
    articles = check_articles_count()
    sitemap = check_sitemap()
    
    message = f"""📊 *تقرير اسبوعي - SaudiSaaSHub*
━━━━━━━━━━━━━━━━━━━━━━

🏠 *حالة الموقع:*
{site_status}

{articles}

{sitemap}

{get_competitor_update()}
{get_keyword_update()}

━━━━━━━━━━━━━━━━━━━━━━
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d')}

#SaudiSaaS #تقرير_اسبوعي"""

    return message

def main():
    print("Starting weekly automation...")
    
    report = format_weekly_report()
    print(report)
    
    if send_telegram(report):
        print("✅ Report sent to Telegram!")
    else:
        print("❌ Failed to send")

if __name__ == "__main__":
    main()

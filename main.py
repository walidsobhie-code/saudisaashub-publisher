#!/usr/bin/env python3
"""
SaudiSaaSHub Social Media Publisher
Reads RSS feed → Generates AI posts → Sends to Telegram
"""

import os
import feedparser
import requests
from datetime import datetime, timedelta
import hashlib
import json

# Configuration
RSS_URL = "https://saudisaashub.pages.dev/feed.xml"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# File to track processed articles
STATE_FILE = "processed_articles.json"

# Saudi Arabic hooks
HOOKS = [
    "وش رايك؟",
    "هل سمعت عن هذا؟",
    "والله تستاهل تعرف!",
    "اقرى وأخبرني!",
    "وش المثير في هذا؟"
]

def load_processed():
    """Load list of processed article URLs"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_processed(processed):
    """Save processed article URLs"""
    with open(STATE_FILE, 'w') as f:
        json.dump(processed, f)

def get_latest_articles():
    """Parse RSS feed and get latest articles"""
    feed = feedparser.parse(RSS_URL)
    articles = []
    
    for entry in feed.entries[:5]:  # Get latest 5
        articles.append({
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'summary': entry.get('summary', '')[:200],
            'published': entry.get('published', '')
        })
    
    return articles

def generate_twitter_post(article):
    """Generate Twitter post (280 chars)"""
    hook = HOOKS[hash(article['title']) % len(HOOKS)]
    title = article['title'][:100]
    link = article['link']
    
    return f"{hook}\n\n{title}\n\n🔗 {link}\n\n#SaudiSaaS #السعودية"

def generate_linkedin_post(article):
    """Generate LinkedIn post"""
    hook = HOOKS[hash(article['title']) % len(HOOKS)]
    title = article['title']
    summary = article['summary']
    link = article['link']
    
    return f"{hook}\n\n{title}\n\n📝 {summary}\n\n👇 اقرأ المزيد:\n{link}\n\n#SaudiSaaS #السعودية #SaaS #Tech"

def generate_instagram_post(article):
    """Generate Instagram post"""
    hook = HOOKS[hash(article['title']) % len(HOOKS)]
    title = article['title']
    summary = article['summary']
    link = article['link']
    
    return f"✨ {hook}\n\n{title}\n\n📖 {summary}\n\n👆 رابط الحلقة في البايو!\n\n#saudisaas #السعودية #technology #entrepreneur"

def send_to_telegram(message):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing Telegram credentials")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 50)
    print("SaudiSaaSHub Publisher")
    print("=" * 50)
    
    # Get latest articles
    articles = get_latest_articles()
    print(f"Found {len(articles)} articles in RSS")
    
    # Load processed
    processed = load_processed()
    print(f"Already processed: {len(processed)} articles")
    
    # Find new articles
    new_articles = [a for a in articles if a['link'] not in processed]
    print(f"New articles: {len(new_articles)}")
    
    if not new_articles:
        print("No new articles to post!")
        return
    
    # Process each new article
    for article in new_articles:
        print(f"\nProcessing: {article['title'][:50]}...")
        
        # Generate posts
        twitter = generate_twitter_post(article)
        linkedin = generate_linkedin_post(article)
        instagram = generate_instagram_post(article)
        
        # Create message
        message = f"""📰 *{article['title']}*

{twitter}

---

📱 *LinkedIn:*
{linkedin}

---

🐦 *Twitter:*
{twitter}

---

📸 *Instagram:*
{instagram}

---

🔗 {article['link']}

#SaudiSaaS #السعودية #التقنية"""
        
        # Send to Telegram
        if send_to_telegram(message):
            print("✅ Posted to Telegram!")
            processed.append(article['link'])
        else:
            print("❌ Failed to post")
    
    # Save state
    save_processed(processed)
    
    print("\n" + "=" * 50)
    print("Done!")

if __name__ == "__main__":
    main()

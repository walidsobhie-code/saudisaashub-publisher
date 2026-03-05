#!/usr/bin/env python3
"""
SaudiSaaSHub Social Media Publisher
"""

import os
import feedparser
import requests
import json
import re
import random

RSS_URL = "https://saudisaashub.pages.dev/feed.xml"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
STATE_FILE = "processed_articles.json"

# Saudi hooks - question style
HOOKS = [
    "وش رايك في؟ 🤔",
    "هل سمعت عن هذا؟ 🤨",
    "والله تستاهل تعرف! 🙌",
    "اقرى واخبرني! 😱",
    "وش المثير بهالموضوع؟ 🔥",
    "تعرفون شنو الجديد؟ 🎯"
]

def load_processed():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_processed(processed):
    with open(STATE_FILE, 'w') as f:
        json.dump(processed, f)

def get_latest_articles():
    feed = feedparser.parse(RSS_URL)
    articles = []
    for entry in feed.entries[:3]:
        summary = re.sub('<[^<]+?>', '', entry.get('summary', ''))
        articles.append({
            'title': entry.get('title', '').strip(),
            'link': entry.get('link', '').strip(),
            'summary': summary[:120].strip(),
        })
    return articles

def get_hashtags(title):
    tags = ["#SaudiSaaS", "#السعودية", "#التقنية"]
    if any(x in title.lower() for x in ['saas', 'سحابية', 'برمجيات']):
        tags.extend(["#SaaS", "#البرمجيات_السحابية"])
    if any(x in title.lower() for x in ['fintech', 'مالية']):
        tags.extend(["#FinTech"])
    if any(x in title.lower() for x in ['تجارة', 'متجر']):
        tags.extend(["#تجارة_إلكترونية"])
    return " ".join(tags[:8])

def generate_twitter(article):
    hook = random.choice(HOOKS)
    title = article['title'][:70]
    link = article['link']
    tags = get_hashtags(article['title'])
    return f"{hook}\n\n{title}\n\n{link}\n\n{tags}"

def generate_linkedin(article):
    hook = random.choice(HOOKS)
    title = article['title']
    summary = article['summary']
    link = article['link']
    tags = get_hashtags(article['title'])
    return f"{hook}\n\n{title}\n\n{summary}\n\n{link}\n\n{tags}\n\n#ريادة_الأعمال"

def generate_instagram(article):
    hook = random.choice(HOOKS).replace("؟", "!").replace("🤔", "💫")
    title = article['title']
    link = article['link']
    return f"{hook}\n\n{title}\n\n👆 رابط الحلقة في البايو!\n\n#saudisaas #السعودية #technology #entrepreneur"

def format_message(article):
    twitter = generate_twitter(article)
    linkedin = generate_linkedin(article)
    instagram = generate_instagram(article)
    tags = get_hashtags(article['title'])
    
    return f"""مقال جديد من SaudiSaaSHub
━━━━━━━━━━━━━━━━━━━━━━

Twitter:
{twitter}

LinkedIn:
{linkedin}

Instagram:
{instagram}

الرابط: {article['link']}

{tags}"""

def send_to_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing credentials")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("SaudiSaaSHub Publisher")
    
    articles = get_latest_articles()
    print(f"Found {len(articles)} articles")
    
    processed = load_processed()
    new_articles = [a for a in articles if a['link'] not in processed]
    print(f"New: {len(new_articles)}")
    
    if not new_articles:
        print("No new articles!")
        return
    
    for article in new_articles:
        print(f"Processing: {article['title'][:30]}...")
        message = format_message(article)
        if send_to_telegram(message):
            print("✅ Posted!")
            processed.append(article['link'])
    
    save_processed(processed)
    print("Done!")

if __name__ == "__main__":
    main()

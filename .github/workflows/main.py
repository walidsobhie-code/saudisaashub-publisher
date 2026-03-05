#!/usr/bin/env python3
"""
SaudiSaaSHub Social Media Publisher
Reads RSS feed → Generates platform-specific posts → Sends to Telegram
"""

import os
import feedparser
import requests
from datetime import datetime
import json
import re

# Configuration
RSS_URL = "https://saudisaashub.pages.dev/feed.xml"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

STATE_FILE = "processed_articles.json"

# Saudi Arabic accent hooks - question style
HOOKS = [
    "وش رايك في؟ 🤔",
    "هل سمعت عن هذا؟ 🤨",
    "والله تستاهل تعرف! 🙌",
    "اقرى وأخبرني! 😱",
    "وش المثير بهالموضوع؟ 🔥",
    "هل تعرف شنو يعني هذا؟ 🧐",
    "والله موضوع مهم! 💡",
    "شفت مثل هذا من قبل؟ 👀",
    "وش رئيك؟ 🤔",
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
    """Parse RSS feed and get latest articles"""
    feed = feedparser.parse(RSS_URL)
    articles = []
    
    for entry in feed.entries[:3]:  # Get latest 3
        # Clean HTML from summary
        summary = re.sub('<[^<]+?>', '', entry.get('summary', ''))
        
        articles.append({
            'title': entry.get('title', '').strip(),
            'link': entry.get('link', '').strip(),
            'summary': summary[:150].strip(),
            'published': entry.get('published', '')
        })
    
    return articles

def get_hashtags(title, categories=[]):
    """Generate relevant hashtags"""
    base_tags = ["#SaudiSaaS", "#السعودية", "#التقنية", "#Startups"]
    
    # Add category-specific tags
    if any(x in title.lower() for x in ['saas', 'سحابية', 'برمجيات']):
        base_tags.extend(["#SaaS", "#البرمجيات_السحابية"])
    if any(x in title.lower() for x in ['fintech', 'مالية', 'دفع']):
        base_tags.extend(["#FinTech", "#التقنية_المالية"])
    if any(x in title.lower() for x in ['أمن', 'سيبراني']):
        base_tags.extend(["#الأمن_السيبراني", "#CyberSecurity"])
    if any(x in title.lower() for x in ['تجارة', 'متجر']):
        base_tags.extend(["#تجارة_إلكترونية", "#ECommerce"])
    if any(x in title.lower() for x in ['صحة', 'طبي']):
        base_tags.extend(["#الصحة_الرقمية", "#Healthcare"])
    if any(x in title.lower() for x in ['تعليم', 'تعلم']):
        base_tags.extend(["#EdTech", "#التعليم"])
    
    return " ".join(base_tags[:10])

def generate_twitter_post(article):
    """Twitter: Short + punchy + hook"""
    import random
    random.seed(hash(article['title']))
    hook = random.choice(HOOKS)
    
    title = article['title'][:80]
    link = article['link']
    tags = get_hashtags(article['title'])
    
    return f"""{hook}

{title}

🔗 {link}

{tags}"""

def generate_linkedin_post(article):
    """LinkedIn: Story + stats + professional"""
    import random
    random.seed(hash(article['title']))
    hook = random.choice(HOOKS)
    
    title = article['title']
    summary = article['summary']
    link = article['link']
    tags = get_hashtags(article['title'])
    
    return f"""{hook}

{title}

📝 {summary}

👇 اقرأ المزيد:
{link}

{tags}

#ريادة_الأعمال #السعودية #Tech"""

def generate_instagram_post(article):
    """Instagram: Emotional + hashtags + call to action"""
    import random
    random.seed(hash(article['title']))
    hook = random.choice(HOOKS).replace("؟", "!").replace("🤔", "💫")
    
    title = article['title']
    summary = article['summary']
    link = article['link']
    tags = " ".join(["#saudisaas", "#السعودية", "#technology", "#entrepreneur", "#startup", "#ريادة_الأعمال"])
    
    return f"""{hook}

{title}

📖 {summary}

👆 طالع الرابط في البايو!

{tags}

#saudiasaas #السعودية_السعودة"""

def format_telegram_message(article):
    """Format complete message for Telegram"""
    twitter = generate_twitter_post(article)
    linkedin = generate_linkedin_post(article)
    instagram = generate_instagram_post(article)
    tags = get_hashtags(article['title'])
    
    message = f"""📰 *مقال جديد من SaudiSaaSHub*

━━━━━━━━━━━━━━━━━━━━━━

🐦 *Twitter:*
{twitter}

━━━━━━━━━━━━━━━━━━━━━━

📱 *LinkedIn:*
{linkedin}

━━━━━━━━━━━━━━━━━━━━━━

📸 *Instagram:*
{instagram}

━━━━━━━━━━━━━━━━━━━━━━

🔗 *الرابط:*
{article['link']}

{tags}

#SaudiSaaS"""

    return message

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
    
    if not articles:
        print("No articles found!")
        return
    
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
        print(f"\nProcessing: {article['title'][:40]}...")
        
        # Format message
        message = format_telegram_message(article)
        
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

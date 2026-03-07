#!/usr/bin/env python3
"""
SaudiSaaSHub Enhanced Social Media Publisher
Features:
- Multi-platform posting (Telegram, Twitter, LinkedIn)
- AI-generated posts
- Auto-scheduling
- Better tracking
"""

import os
import feedparser
import requests
import json
import re
import random
from datetime import datetime
from urllib.parse import urlparse

# Configuration
RSS_URL = "https://saudisaashub.pages.dev/feed.xml"
STATE_FILE = "processed_articles.json"

# Environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
LINKEDIN_TOKEN = os.environ.get("LINKEDIN_TOKEN", "")

# Saudi hooks - question style (Engaging)
HOOKS = [
    "وش رايك في هذا؟ 🤔",
    "هل سمعت عن هالأمر؟ 🤨",
    "والله تستاهل تعرف! 🙌",
    "اقرى وحكم بنفسك! 😱",
    "هالموضوع مهم لك! 🔥",
    "جديد في السوق! 🎯",
    "موضوع يستحق اهتمامك! 💡",
    "هل تعرف هذا؟ 🤯"
]

# Emoji for variety
EMOJI_SETS = [
    "🔥💡🎯",
    "🤔💭✨",
    "🙌📈🚀",
    "😱💎🔔"
]

def load_processed():
    """Load processed articles"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_processed(processed):
    """Save processed articles"""
    with open(STATE_FILE, 'w') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

def get_latest_articles():
    """Get latest articles from RSS"""
    feed = feedparser.parse(RSS_URL)
    articles = []
    for entry in feed.entries[:5]:  # Get top 5
        summary = re.sub('<[^<]+?>', '', entry.get('summary', ''))
        articles.append({
            'title': entry.get('title', '').strip(),
            'link': entry.get('link', '').strip(),
            'summary': summary[:150].strip(),
            'published': entry.get('published', '')
        })
    return articles

def get_category_tags(title):
    """Extract category-specific hashtags"""
    title_lower = title.lower()
    tags = ["#SaudiSaaS", "#السعودية", "#التقنية"]

    # Category mapping
    category_map = {
        'saas': ["#SaaS", "#البرمجيات_السحابية", "#ريادة_الأعمال"],
        'fintech': ["#FinTech", "#المالية", "#التقنية_المالية"],
        'تجارة': ["#تجارة_إلكترونية", "#متاجر", "#تجارة"],
        'أمن': ["#الأمن_السيبراني", "#CyberSecurity", "#حماية"],
        'صحة': ["#الصحة_الرقمية", "#HealthTech", "#رعاية"],
        'تعليم': ["#التعليم_الإلكتروني", "#EdTech", "#تعلم"],
        'طعام': ["#FoodTech", "#توصيل", "#خدمات"],
        'مدفوعات': ["#الدفع_الإلكتروني", "#BNPL", "#تمارا"]
    }

    for key, values in category_map.items():
        if key in title_lower:
            tags.extend(values)
            break

    return " ".join(tags[:6])

def generate_twitter_post(article):
    """Generate Twitter/X post"""
    hook = random.choice(HOOKS)
    emoji = random.choice(EMOJI_SETS)

    title = article['title'][:80]
    link = article['link']
    tags = get_category_tags(article['title'])

    return f"""{hook} {emoji}

{title}

🔗 {link}

{tags}"""

def generate_linkedin_post(article):
    """Generate LinkedIn post"""
    hook = random.choice(HOOKS)

    title = article['title']
    summary = article['summary']
    link = article['link']
    tags = get_category_tags(article['title'])

    return f"""{hook}

📌 {title}

{summary}

تعرف أكثر من خلال الرابط أدناه 👇

🔗 {link}

{tags}

#ريادة_الأعمال #السعودية #تقنية"""

def generate_facebook_post(article):
    """Generate Facebook post"""
    hook = random.choice(HOOKS)

    title = article['title']
    summary = article['summary']
    link = article['link']
    tags = get_category_tags(article['title'])

    return f"""{hook}

📰 {title}

{summary}

👆 اضغط للقراءة الكاملة

{tags}

#السعودية #أخبار_التقنية #SaaS"""

def generate_threads_post(article):
    """Generate Meta Threads post"""
    hook = random.choice(HOOKS).replace("؟", "!")

    title = article['title'][:100]
    link = article['link']

    return f"""{hook}

📱 {title}

👆 رابط الحلقة في البايو!

#saudisaas #السعودية #tech #entrepreneur"""

def generate_whatsapp_status(article):
    """Generate WhatsApp Status format"""
    title = article['title'][:50]
    link = article['link']

    return f"""📱 {title}

🔗 {link}

#SaudiSaaS"""

# ============ PLATFORM POSTING ============

def post_to_telegram(message):
    """Send to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Missing Telegram credentials")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=data, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def post_to_twitter(post):
    """Post to Twitter/X (v2 API)"""
    if not TWITTER_ACCESS_TOKEN:
        print("⚠️ Missing Twitter credentials")
        return False

    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {TWITTER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json={"text": post}, headers=headers, timeout=15)
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Twitter error: {e}")
        return False

def post_to_linkedin(post):
    """Post to LinkedIn"""
    if not LINKEDIN_TOKEN:
        print("⚠️ Missing LinkedIn credentials")
        return False

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    try:
        response = requests.post(url, json={
            "author": "urn:li:person:YOUR_PERSON_URN",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post},
                    "shareMediaCategory": "ARTICLE"
                }
            }
        }, headers=headers, timeout=15)
        return response.status_code == 201
    except Exception as e:
        print(f"❌ LinkedIn error: {e}")
        return False

# ============ REPORTING ============

def generate_platform_report(platforms):
    """Generate multi-platform post report"""
    report = "📱 **تقرير النشر المتعدد**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for platform, status in platforms.items():
        icon = "✅" if status else "❌"
        report += f"{icon} *{platform}:* {'نشر' if status else 'فشل'}\n"

    report += "\n━━━━━━━━━━━━━━━━━━━━━━"
    return report

def format_social_media_package(article):
    """Format complete social media package"""
    package = {
        'telegram': generate_telegram_post(article),
        'twitter': generate_twitter_post(article),
        'linkedin': generate_linkedin_post(article),
        'facebook': generate_facebook_post(article),
        'threads': generate_threads_post(article),
        'whatsapp': generate_whatsapp_status(article)
    }

    # Main Telegram message with all platforms
    telegram_msg = f"""📢 **مقال جديد من SaudiSaaSHub**
━━━━━━━━━━━━━━━━━━━━━━

🔵 **Twitter/X:**
{package['telegram']}

━━━━━━━━━━━━━━━━━━━━━━

💼 **LinkedIn:**
{package['linkedin']}

━━━━━━━━━━━━━━━━━━━━━━

📘 **Facebook:**
{package['facebook']}

━━━━━━━━━━━━━━━━━━━━━━

🔗 **الرابط:** {article['link']}

#SaudiSaaS #التقنية_السعودية"""

    package['telegram_full'] = telegram_msg
    return package

# ============ MAIN FUNCTION ============

def main():
    """Main function"""
    print("🚀 SaudiSaaSHub Social Publisher")
    print("=" * 40)

    # Get articles
    articles = get_latest_articles()
    print(f"📰 Found {len(articles)} articles")

    # Load processed
    processed = load_processed()
    new_articles = [a for a in articles if a['link'] not in processed]

    if not new_articles:
        print("✅ No new articles!")
        return

    print(f"🆕 New articles: {len(new_articles)}")

    # Process each article
    for article in new_articles:
        print(f"\n📝 Processing: {article['title'][:40]}...")

        # Generate social media package
        package = format_social_media_package(article)

        # Send to Telegram
        if post_to_telegram(package['telegram_full']):
            print("   ✅ Telegram: Posted")
        else:
            print("   ❌ Telegram: Failed")

        # Post to Twitter
        if post_to_twitter(package['twitter']):
            print("   ✅ Twitter: Posted")

        # Post to LinkedIn
        if post_to_linkedin(package['linkedin']):
            print("   ✅ LinkedIn: Posted")

        # Mark as processed
        processed.append(article['link'])

    # Save state
    save_processed(processed)

    print("\n✅ All done!")

if __name__ == "__main__":
    main()

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

# Environment variables (Telegram only for manual posting)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

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

def generate_telegram_post(article):
    """Generate Telegram post"""
    hook = random.choice(HOOKS)
    emoji = random.choice(EMOJI_SETS)

    title = article['title'][:80]
    link = article['link']
    tags = get_category_tags(article['title'])

    return f"""{hook} {emoji}

{title}

🔗 {link}

{tags}"""

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
    """Format social media package for manual posting"""
    # Generate content for manual posting
    telegram_content = generate_telegram_post(article)
    whatsapp_content = generate_whatsapp_status(article)

    # Main Telegram message with ready-to-post content
    telegram_msg = f"""📢 **مقال جديد من SaudiSaaSHub**
━━━━━━━━━━━━━━━━━━━━━━

📰 *{article['title']}*

{article['summary']}

━━━━━━━━━━━━━━━━━━━━━━

📝 *جاهز للنشر:*

🔵 **Twitter/X:**
{telegram_content}

━━━━━━━━━━━━━━━━━━━━━━

💼 **LinkedIn:**
{generate_linkedin_post(article)}

━━━━━━━━━━━━━━━━━━━━━━

📘 **Facebook:**
{generate_facebook_post(article)}

━━━━━━━━━━━━━━━━━━━━━━

🔗 **الرابط:** {article['link']}

#SaudiSaaS #التقنية_السعودية"""

    return {
        'telegram_full': telegram_msg,
        'twitter': telegram_content,
        'whatsapp': whatsapp_content
    }

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

        # Send to Telegram only (free)
        if post_to_telegram(package['telegram_full']):
            print("   ✅ Telegram: Posted")
        else:
            print("   ❌ Telegram: Failed")

        # Mark as processed
        processed.append(article['link'])

    # Save state
    save_processed(processed)

    print("\n✅ All done!")

if __name__ == "__main__":
    main()

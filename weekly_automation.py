#!/usr/bin/env python3
"""
SaudiSaaSHub Enhanced Weekly Automation
Features:
- Comprehensive site health checks
- SEO reporting
- Social media analytics
- Competitor monitoring
- Keyword tracking
- Performance metrics
"""

import os
import feedparser
import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
SITE_URL = "https://saudisaashub.pages.dev"
STATE_FILE = "analytics_data.json"

# Competitors to monitor
COMPETITORS = {
    "salla": {"name": "Salla", "url": "https://salla.sa", "type": "ecommerce"},
    "zid": {"name": "Zid", "url": "https://zid.sa", "type": "ecommerce"},
    "tamara": {"name": "Tamara", "url": "https://tamara.co", "type": "fintech"},
    "lucidya": {"name": "Lucidya", "url": "https://lucidya.com", "type": "ai"},
    "lean": {"name": "Lean", "url": "https://leantech.me", "type": "fintech"},
    "matar": {"name": "Matar", "url": "https://matar.sa", "type": "logistics"}
}

# Keywords to track
KEYWORDS = [
    "SaaS السعودية",
    "برمجيات سحابية",
    "تجارة إلكترونية سعودية",
    "fintech السعودية",
    "أمن سيبراني",
    "تعلم إلكتروني",
    "صحة رقمية",
    "تحول رقمي",
    "الفوترة الإلكترونية زاتكا",
    "PDPL السعودية"
]

def load_analytics():
    """Load previous analytics data"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"posts": 0, "articles": 0, "last_week": {}}

def save_analytics(data):
    """Save analytics data"""
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_telegram(message):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Missing credentials")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=data, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============ SITE HEALTH CHECKS ============

def check_site_status():
    """Check if site is up"""
    try:
        r = requests.get(SITE_URL, timeout=10)
        if r.status_code == 200:
            return {"status": "UP", "code": r.status_code, "time": r.elapsed.total_seconds()}
        return {"status": "DOWN", "code": r.status_code}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

def check_sitemap():
    """Check sitemap"""
    try:
        r = requests.get(f"{SITE_URL}/sitemap.xml", timeout=10)
        if r.status_code == 200:
            # Count URLs in sitemap
            import re
            urls = re.findall(r'<loc>(.*?)</loc>', r.text)
            return {"status": "OK", "urls": len(urls)}
        return {"status": "MISSING", "code": r.status_code}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

def check_robots():
    """Check robots.txt"""
    try:
        r = requests.get(f"{SITE_URL}/robots.txt", timeout=10)
        return {"status": "OK" if r.status_code == 200 else "MISSING"}
    except:
        return {"status": "ERROR"}

def check_feed():
    """Check RSS feed"""
    try:
        feed = feedparser.parse(f"{SITE_URL}/feed.xml")
        articles = len(feed.entries)
        return {"status": "OK", "articles": articles}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# ============ SEO CHECKS ============

def check_seo_meta():
    """Check SEO meta tags"""
    try:
        r = requests.get(SITE_URL, timeout=10)
        html = r.text

        checks = {
            "title": "<title>" in html,
            "meta_desc": 'name="description"' in html,
            "og_title": 'property="og:title"' in html,
            "og_image": 'property="og:image"' in html,
            "canonical": 'rel="canonical"' in html,
            "robots": 'name="robots"' in html
        }

        score = sum(checks.values()) * 100 // len(checks)
        return {"status": "OK", "score": score, "checks": checks}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# ============ SOCIAL MEDIA CHECKS ============

def check_social_meta():
    """Check social media meta tags"""
    try:
        r = requests.get(SITE_URL, timeout=10)
        html = r.text

        checks = {
            "og:type": 'property="og:type"' in html,
            "og:url": 'property="og:url"' in html,
            "twitter:card": 'name="twitter:card"' in html,
            "twitter:title": 'name="twitter:title"' in html
        }

        score = sum(checks.values()) * 100 // len(checks)
        return {"status": "OK", "score": score, "checks": checks}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# ============ PERFORMANCE CHECKS ============

def check_performance_headers():
    """Check caching headers"""
    try:
        r = requests.get(SITE_URL, timeout=10)
        headers = r.headers

        checks = {
            "cache-control": "cache-control" in headers,
            "etag": "etag" in headers,
            "x-cache": "x-cache" in headers
        }

        return {"status": "OK", "checks": checks}
    except:
        return {"status": "ERROR"}

# ============ COMPETITOR MONITORING ============

def check_competitor(competitor_key, competitor_info):
    """Check competitor status"""
    try:
        r = requests.get(competitor_info["url"], timeout=5)
        return {
            "name": competitor_info["name"],
            "status": "UP" if r.status_code == 200 else f"ERROR {r.status_code}",
            "type": competitor_info["type"]
        }
    except:
        return {
            "name": competitor_info["name"],
            "status": "DOWN",
            "type": competitor_info["type"]
        }

def check_all_competitors():
    """Check all competitors"""
    results = []
    for key, info in COMPETITORS.items():
        result = check_competitor(key, info)
        results.append(result)
        time.sleep(0.5)  # Rate limiting
    return results

# ============ CONTENT ANALYSIS ============

def analyze_content():
    """Analyze RSS content"""
    try:
        feed = feedparser.parse(f"{SITE_URL}/feed.xml")

        if not feed.entries:
            return {"status": "ERROR", "message": "No articles"}

        # Get recent articles
        recent = feed.entries[:5]

        categories = {}
        for entry in feed.entries:
            # Extract categories from entry
            if hasattr(entry, 'tags'):
                for tag in entry.tags:
                    cat = tag.term
                    categories[cat] = categories.get(cat, 0) + 1

        return {
            "status": "OK",
            "total": len(feed.entries),
            "recent": [{"title": e.title[:50], "link": e.link} for e in recent],
            "categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# ============ FORMATTING ============

def format_health_report(health, seo, social, performance):
    """Format health report"""
    report = "📊 *تقرير صحة الموقع الأسبوعي*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"

    # Site Status
    report += "🏠 *حالة الموقع:*\n"
    site_icon = "✅" if health.get("site", {}).get("status") == "UP" else "❌"
    report += f"{site_icon} الحالة: {health.get('site', {}).get('status', 'N/A')}\n"

    if "time" in health.get("site", {}):
        report += f"⏱️_response time: {health['site']['time']:.2f}s\n"

    # SEO Score
    seo_score = seo.get("meta", {}).get("score", 0)
    report += f"\n🔍 *SEO Score:* {seo_score}%\n"
    if seo_score >= 80:
        report += "✅ ممتاز!\n"
    elif seo_score >= 60:
        report += "⚠️ يمكن تحسينه\n"
    else:
        report += "❌ يحتاج تحسين\n"

    # Social Score
    social_score = social.get("meta", {}).get("score", 0)
    report += f"\n📱 *Social Score:* {social_score}%\n"

    # Performance
    perf = performance.get("headers", {})
    report += "\n⚡ *الأداء:*\n"
    if perf.get("checks", {}).get("etag"):
        report += "✅ ETag مفعل\n"
    if perf.get("checks", {}).get("cache-control"):
        report += "✅ Caching مفعل\n"

    return report

def format_content_report(content):
    """Format content report"""
    report = "\n📄 *المحتوى:*\n"
    report += f"✅ {content.get('total', 0)} مقال منشور\n"

    # Categories
    if content.get("categories"):
        report += "\n📂 *التصنيفات:*\n"
        for cat, count in content.get("categories", {}).items():
            report += f"- {cat}: {count}\n"

    # Recent articles
    if content.get("recent"):
        report += "\n🆕 *أحدث المقالات:*\n"
        for art in content.get("recent", [])[:3]:
            report += f"- {art['title']}...\n"

    return report

def format_competitor_report(competitors):
    """Format competitor report"""
    report = "\n🏢 *المنافسون:*\n"

    up_count = sum(1 for c in competitors if c.get("status") == "UP")

    for comp in competitors:
        icon = "✅" if comp.get("status") == "UP" else "❌"
        report += f"{icon} {comp.get('name')}: {comp.get('status')}\n"

    return report

def format_summary(sitemap, feed):
    """Format technical summary"""
    report = "\n🔧 *ملخص تقني:*\n"

    # Sitemap
    if sitemap.get("status") == "OK":
        report += f"✅ Sitemap: {sitemap.get('urls', 0)} رابط\n"
    else:
        report += "❌ Sitemap\n"

    # Feed
    if feed.get("status") == "OK":
        report += f"✅ RSS Feed: {feed.get('articles', 0)} مقال\n"
    else:
        report += "❌ RSS Feed\n"

    return report

# ============ MAIN ============

def main():
    """Main function"""
    print("🚀 Starting Weekly Analytics...")

    # Run all checks
    print("📡 Checking site...")
    site_status = check_site_status()

    print("🗺️ Checking sitemap...")
    sitemap_status = check_sitemap()

    print("📡 Checking feed...")
    feed_status = check_feed()

    print("🔍 Checking SEO...")
    seo_status = check_seo_meta()

    print("📱 Checking social...")
    social_status = check_social_meta()

    print("⚡ Checking performance...")
    perf_status = check_performance_headers()

    print("🏢 Checking competitors...")
    competitor_status = check_all_competitors()

    print("📄 Analyzing content...")
    content_status = analyze_content()

    # Compile report
    health = {"site": site_status}
    seo = {"meta": seo_status}
    social = {"meta": social_status}
    performance = {"headers": perf_status}

    report = "📊 *SaudiSaaSHub - تقرير أسبوعي شامل*\n━━━━━━━━━━━━━━━━━━━━━━\n"
    report += f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"

    # Add all sections
    report += format_health_report(health, seo, social, performance)
    report += format_content_report(content_status)
    report += format_competitor_report(competitor_status)
    report += format_summary(sitemap_status, feed_status)

    report += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    report += "#SaudiSaaS #تقرير_اسبوعي"

    # Send to Telegram
    print("\n📤 Sending to Telegram...")
    if send_telegram(report):
        print("✅ Report sent!")
    else:
        print("❌ Failed to send")

    print("✅ Done!")

if __name__ == "__main__":
    main()

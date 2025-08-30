#!/usr/bin/env python3
"""
Apple Deal Alert - Hannaford Web Scraper
Searches Hannaford.com for apple deals and alerts when prices are below threshold
"""
import re
import sys
import datetime as dt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
import time
import random
import os

# Configuration
MIN_PRICE_PER_LB = 1.50  # alert threshold
EMAIL_TO = "sean@carolan.io"
EMAIL_FROM = "sean@carolan.io"  # Using your domain for Google SMTP relay
EMAIL_PASSWORD = os.getenv("SMTP_PASSWORD")  # Get from environment variable
SMTP_SERVER = "smtp-relay.gmail.com"  # Google SMTP relay
SMTP_PORT = 587  # Standard port for SMTP with STARTTLS
ONLY_IN_SEASON = True
SEASON_MONTHS = {8, 9, 10}  # Aug–Oct
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def in_season():
    """Check if we're in apple season"""
    now = dt.datetime.now()
    return now.month in SEASON_MONTHS

def search_hannaford_apples():
    """Search Hannaford.com for apple products"""
    search_url = "https://www.hannaford.com/search/product"
    params = {
        "form_state": "searchForm",
        "keyword": "apples",
        "ieDummyTextField": "",
        "productTypeId": "P"
    }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Exponential backoff with jitter
            if attempt > 0:
                delay = (2 ** attempt) + random.uniform(0, 1)
                print(f"[info] Retry {attempt + 1}/{max_retries} after {delay:.1f}s delay...")
                time.sleep(delay)
            
            # Random delay to seem more human-like
            time.sleep(random.uniform(1, 3))
            
            # Use session for cookie persistence
            session = requests.Session()
            session.headers.update(headers)
            
            response = session.get(search_url, params=params, timeout=45)
            response.raise_for_status()
            return response.text
            
        except requests.Timeout:
            print(f"[warn] Attempt {attempt + 1} timed out")
            if attempt == max_retries - 1:
                print("[error] All retry attempts failed due to timeout")
        except requests.RequestException as e:
            print(f"[warn] Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print(f"[error] All retry attempts failed: {e}")
    
    return None

def parse_apple_deals(html_content):
    """Parse the search results for apple deals"""
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    deals = []

    # Look for product containers with data attributes
    products = soup.find_all('div', {'data-price': True, 'data-name': True})

    for product in products:
        try:
            # Extract product data from attributes
            name = product.get('data-name', '').replace('+', ' ')
            price_str = product.get('data-price', '')
            variant = product.get('data-variant', '')
            category = product.get('data-category', '')

            # Skip if not apple-related
            if 'apple' not in name.lower() and 'apple' not in category.lower():
                continue

            # Parse price
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                continue

            # Determine if it's per lb or per unit
            is_per_lb = 'lb' in variant.lower() or 'pound' in variant.lower()

            # For per-lb items, the price IS the unit price
            # For bags/units, we'd need to calculate (but most apples are sold per lb)
            unit_price = price if is_per_lb else None

            deal = {
                'name': name,
                'price': price,
                'variant': variant,
                'category': category,
                'is_per_lb': is_per_lb,
                'unit_price': unit_price
            }
            deals.append(deal)

        except Exception as e:
            continue

    return deals

def filter_qualifying_deals(deals):
    """Filter deals that meet our criteria"""
    qualifying = []

    for deal in deals:
        # Skip if we can't determine unit price
        if deal['unit_price'] is None:
            continue

        # Check if price is at or below threshold
        if deal['unit_price'] <= MIN_PRICE_PER_LB:
            qualifying.append(deal)

    return qualifying

def send_alert_email(deals):
    """Send email alert for apple deals"""
    if not EMAIL_PASSWORD:
        print("[error] SMTP_PASSWORD environment variable not set")
        return False
        
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"🍎 Apple Deal Alert - {len(deals)} deal(s) found!"

        # Create email body
        body = "Great news! We found some apple deals under $1.50/lb:\n\n"
        for deal in sorted(deals, key=lambda x: x['unit_price']):
            body += f"• ${deal['unit_price']:.2f}/lb - {deal['name']} ({deal['variant']})\n"

        body += f"\nHappy shopping!\n\nSent at: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        msg.attach(MIMEText(body, 'plain'))

        # Send email via Google SMTP relay with authentication
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Required TLS encryption for Google SMTP relay
        server.login(EMAIL_FROM, EMAIL_PASSWORD)  # SMTP authentication
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, EMAIL_TO, text)
        server.quit()

        print(f"[info] Alert email sent to {EMAIL_TO}")
        return True

    except Exception as e:
        print(f"[error] Failed to send email: {e}")
        return False

def main():
    if ONLY_IN_SEASON and not in_season():
        sys.exit(0)

    # Search for apples
    html_content = search_hannaford_apples()
    if not html_content:
        print("[error] Could not fetch search results")
        sys.exit(1)

    # Parse the results
    deals = parse_apple_deals(html_content)

    if not deals:
        print("[warn] No apple products found - the website structure may have changed")
        sys.exit(1)

    # Filter for good deals
    qualifying = filter_qualifying_deals(deals)

    if not qualifying:
        print(f"[result] No apple deals ≤ ${MIN_PRICE_PER_LB:.2f}/lb found")
        sys.exit(0)

    print(f"🔥 Apple deal(s) at or below ${MIN_PRICE_PER_LB:.2f}/lb detected:")
    for deal in sorted(qualifying, key=lambda x: x['unit_price']):
        print(f"- ${deal['unit_price']:.2f}/lb :: {deal['name']} ({deal['variant']})")

    # Send email alert
    send_alert_email(qualifying)

if __name__ == "__main__":
    main()

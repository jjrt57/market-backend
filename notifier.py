import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import logging

logger = logging.getLogger(__name__)

def send_alert(new_discoveries):
    """Sends an email ONLY if high-conviction 'Elite' stocks (Score 80+) are found."""
    email_data_raw = os.environ.get("EMAIL_DATA")
    if not email_data_raw:
        logger.warning("⚠️ EMAIL_DATA secret not found. Skipping email.")
        return

    try:
        creds = json.loads(email_data_raw)
        sender_email = creds.get("SENDER_EMAIL")
        receiver_email = creds.get("RECEIVER_EMAIL")
        password = creds.get("PASSWORD")

        # --- 1. Elite Filter (Power Score Calculation) ---
        elite_picks = []
        for s in new_discoveries:
            score = 0
            if s.get('sentiment_label') == "High Sentiment": score += 40
            if s.get('whale_alert') != "None" and "🚨" in s.get('whale_alert', ''): score += 40
            if s.get('status') == "Undervalued Gem": score += 20
            
            if score >= 80:
                s['power_score'] = score
                elite_picks.append(s)

        # Exit early if no top-tier picks are found
        if not elite_picks:
            logger.info("ℹ️ No 'Elite' (80+ score) stocks found. Skipping email notification.")
            return

        # --- 2. Dynamic Subject Line for Elite Picks ---
        whale_hits = [s for s in elite_picks if "🚨" in s.get('whale_alert', '')]
        
        if len(whale_hits) > 0:
            subject = f"🔥 URGENT: {len(elite_picks)} Elite Whale-Backed Picks Found!"
        else:
            subject = f"🌟 Opportunity: {len(elite_picks)} High Sentiment Elite Stocks"

        # --- 3. Build the Email Body ---
        body = f"<h2>🎯 Elite Market Intelligence Discovery ({len(elite_picks)})</h2>"
        body += "<p>The following stocks have hit a Power Score of 80+ across our engines:</p><br>"

        for stock in elite_picks:
            sentiment_color = "#28a745" # High Sentiment is always green here
            
            body += f"""
            <div style="border: 2px solid #28a745; padding: 15px; margin-bottom: 10px; border-radius: 8px; background-color: #f8fff9;">
                <h3 style="margin-top: 0;">{stock['symbol']} - ₹{stock['price']} (Score: {stock['power_score']})</h3>
                <p><b>Sentiment:</b> <span style="color: {sentiment_color}; font-weight: bold;">{stock.get('sentiment_label')} ({stock.get('sentiment_score')})</span></p>
                <p><b>Whale Status:</b> {stock.get('whale_alert')}</p>
                <p><b>Strategy:</b> {stock.get('status')}</p>
                <p><b>Metrics:</b> Growth: {stock.get('growth')} | ICR: {stock.get('icr')}</p>
            </div>
            """

        # --- 4. SMTP Configuration ---
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)

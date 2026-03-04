import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
import logging

logger = logging.getLogger(__name__)

def send_alert(new_discoveries):
    """Sends a professional email alert for new stock discoveries."""
    email_data_raw = os.environ.get("EMAIL_DATA")
    if not email_data_raw:
        logger.warning("⚠️ EMAIL_DATA secret not found. Skipping email.")
        return

    try:
        creds = json.loads(email_data_raw)
        sender_email = creds.get("SENDER_EMAIL")
        receiver_email = creds.get("RECEIVER_EMAIL")
        password = creds.get("PASSWORD")

        # --- 1. Dynamic Subject Line Logic ---
        high_conviction = [s for s in new_discoveries if s.get('sentiment_label') == "High Sentiment"]
        whale_hits = [s for s in new_discoveries if s.get('whale_alert') != "None"]
        
        subject = f"🚀 Market Update: {len(new_discoveries)} New Gems Found"
        if whale_hits and high_conviction:
            subject = f"🔥 URGENT: {len(whale_hits)} Whale-Backed High Sentiment Picks!"
        elif whale_hits:
            subject = f"🐋 Whale Alert: {len(whale_hits)} Major Accumulations Detected"
        elif high_conviction:
            subject = f"🌟 Opportunity: {len(high_conviction)} High Sentiment Stocks"

        # --- 2. Build the Email Body ---
        body = "<h2>🎯 New Market Intelligence Discoveries</h2>"
        body += "<p>The following stocks have passed our multi-engine filters:</p><br>"

        for stock in new_discoveries:
            sentiment_color = "#28a745" if stock.get('sentiment_label') == "High Sentiment" else "#dc3545" if stock.get('sentiment_label') == "Low Sentiment" else "#6c757d"
            
            body += f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 8px;">
                <h3 style="margin-top: 0;">{stock['symbol']} - ₹{stock['price']}</h3>
                <p><b>Sentiment:</b> <span style="color: {sentiment_color}; font-weight: bold;">{stock.get('sentiment_label', 'Neutral')} ({stock.get('sentiment_score', 0.0)})</span></p>
                <p><b>Whale Status:</b> {stock.get('whale_alert', 'No recent block deals')}</p>
                <p><b>Source:</b> {stock.get('status', 'System Pick')}</p>
                <p><b>Metrics:</b> Growth: {stock.get('growth', 'N/A')} | ICR: {stock.get('icr', 'N/A')}</p>
            </div>
            """

        # --- 3. SMTP Configuration ---
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
        
        logger.info(f"📩 Email alert sent successfully: {subject}")

    except Exception as e:
        logger.error(f"❌ Failed to send email alert: {e}")

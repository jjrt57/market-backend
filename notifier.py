import smtplib
from email.mime.text import MIMEText
import os

def send_alert(new_stocks):
    sender = os.environ.get('EMAIL_SENDER')
    password = os.environ.get('EMAIL_PASSWORD')
    receiver = os.environ.get('EMAIL_RECEIVER')

    if not sender or not password or not receiver:
        print("⚠️ Email credentials not found. Skipping email alert.")
        return

    # Create the email content
    subject = f"🚀 AI Market Alert: {len(new_stocks)} New Gems Discovered!"
    
    body = "Your AI Backend just discovered these new stocks that meet your strict 2026 criteria:\n\n"
    
    for stock in new_stocks:
        body += f"🔹 {stock['symbol']}\n"
        body += f"   - Price: ₹{stock['price']}\n"
        body += f"   - Tag: {stock.get('status', stock.get('potential_tag', 'Value Pick'))}\n\n"
        
    body += "Happy Investing!\n- Your AI Backend"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "AI Market Engine <" + sender + ">"
    msg['To'] = receiver

    try:
        # Connect to Gmail and send
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("✅ Email alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
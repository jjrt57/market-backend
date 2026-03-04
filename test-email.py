import notifier

# Fake stock data to test the email format
fake_discoveries = [
    {
        "symbol": "OLECTRA.NS",
        "price": 412.50,
        "status": "🔥 TEST: PRO APPROVED"
    }
]

print("🧪 Starting local email test...")
notifier.send_alert(fake_discoveries)
print("🏁 Test finished.")
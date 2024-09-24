from flask import Flask, render_template, request, redirect, url_for
import websocket
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import threading

app = Flask(__name__)

# Deriv WebSocket URL
DERIV_API_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"  # Replace 1089 with your app_id

# Email Config
EMAIL_ADDRESS = 'mirasplendid2017@gmail.com'  # Your email address
EMAIL_PASSWORD = 'xmjwflomfceowbeg'  # Email password or app password
TO_EMAIL = 'miraculus2017@gmail.com'  # Recipient email

# Telegram Config
TELEGRAM_BOT_TOKEN = '7374323759:AAEuwSKA6P3-X1xzJWfYAZvHZHV_NaLgQww'  # Your Telegram bot token
TELEGRAM_CHAT_ID = '657073225'  # Your Telegram chat ID

# Global variable to store alert prices
alert_prices = {}

# Function to send email
def send_email(subject, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"Email sent to {TO_EMAIL}")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

# Function to send message to Telegram
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Message sent to Telegram.")
        else:
            print(f"Failed to send message to Telegram. Response: {response.text}")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# WebSocket message handler
def on_message(ws, message):
    data = json.loads(message)
    if 'tick' in data:
        symbol = data['tick']['symbol']
        price = data['tick']['quote']
        if symbol in alert_prices:
            target_price = alert_prices[symbol]['target_price']
            custom_message = alert_prices[symbol]['custom_message']
            tolerance = 0.1
            if abs(price - target_price) <= tolerance:
                alert_message = f"ALERT: {symbol} reached the desired price of {target_price}! Current price: {price}\n{custom_message}"
                send_email(f"Price Alert for {symbol}", alert_message)
                send_telegram_message(alert_message)
                del alert_prices[symbol]
                if not alert_prices:
                    ws.close()

# WebSocket functions
def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    for instrument in alert_prices.keys():
        subscribe_message = json.dumps({"ticks": instrument})
        ws.send(subscribe_message)

def run_websocket():
    ws = websocket.WebSocketApp(DERIV_API_URL, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_alert', methods=['POST'])
def set_alert():
    instrument = request.form['instrument']
    target_price = float(request.form['target_price'])
    custom_message = request.form['custom_message']
    
    # Add to alert list
    alert_prices[instrument] = {'target_price': target_price, 'custom_message': custom_message}
    
    # Run WebSocket in a separate thread to not block Flask
    websocket_thread = threading.Thread(target=run_websocket)
    websocket_thread.start()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

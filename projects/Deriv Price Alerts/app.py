import websocket
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get secrets from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
TO_EMAIL = os.getenv('TO_EMAIL')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Define WebSocket URL for Deriv API
DERIV_API_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"  # Replace 1089 with your app_id

def send_email(subject, message):
    """Function to send email using SSL."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))
    try:
        # Connect to the SMTP server using SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"Email sent to {TO_EMAIL}")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def send_telegram_message(message):
    """Function to send a message to Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Message sent to Telegram.")
        else:
            print(f"Failed to send message to Telegram. Response: {response.text}")
    except Exception as e:
        print(f"Error sending message to Telegram: {e}")

# Function to take user input for instrument, desired alert price, and custom message
def get_user_input():
    alert_prices = {}  # Initialize an empty dictionary to store alerts
    while True:
        instrument = input("Enter the instrument/pair you want to track (e.g., frxEURUSD, R_50, CRASH500 etc.) or type 'done' to finish: ")
        if instrument.lower() == 'done':
            break
        try:
            target_price = float(input(f"Enter the desired price for {instrument}: "))
            custom_message = input(f"Please enter a message for when {instrument} reaches the desired price: ")
            alert_prices[instrument] = {
                'target_price': target_price,
                'custom_message': custom_message
            }
        except ValueError:
            print("Invalid input. Please enter a valid number for the price.")
    return alert_prices

# Function to handle incoming WebSocket messages
def on_message(ws, message):
    data = json.loads(message)
    if 'tick' in data:
        symbol = data['tick']['symbol']
        price = data['tick']['quote']
        timestamp = data['tick']['epoch']
        print(f"Instrument: {symbol}, Price: {price}, Timestamp: {timestamp}")

        # Define a small tolerance for price comparison
        tolerance = 0.1  # Adjust this value as needed for your use case

        # Check if the price is within the tolerance range of the alert threshold
        if symbol in alert_prices:
            target_price = alert_prices[symbol]['target_price']
            custom_message = alert_prices[symbol]['custom_message']
            if abs(price - target_price) <= tolerance:  # Use tolerance for comparison
                alert_message = f"ALERT: {symbol} has reached the desired price of {target_price}! The current price is: {price}\n{custom_message}"
                print(f"*** {alert_message} ***")

                # Send an email alert
                send_email(subject=f"Price Alert for {symbol}", message=alert_message)

                # Send a Telegram alert
                send_telegram_message(alert_message)

                # Remove the instrument from the alert list
                del alert_prices[symbol]

                # Check if all alerts are done, then close WebSocket
                if not alert_prices:
                    print("All price alerts have been triggered. Closing WebSocket connection.")
                    ws.close()

# Function to handle WebSocket errors
def on_error(ws, error):
    print(f"Error: {error}")

# Function to handle WebSocket closure
def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

# Function to handle WebSocket connection opening
def on_open(ws):
    print("WebSocket connection opened")
    # Subscribe to tick updates for each instrument
    for instrument in alert_prices.keys():
        subscribe_message = json.dumps({"ticks": instrument})
        ws.send(subscribe_message)

# Main function to run the bot
if __name__ == "__main__":
    # Get user input for instruments, alert prices, and custom messages
    alert_prices = get_user_input()

    if not alert_prices:
        print("No instruments were provided. Exiting.")
    else:
        # Create WebSocket App instance
        ws = websocket.WebSocketApp(DERIV_API_URL,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

        # Run the WebSocket connection
        ws.run_forever()

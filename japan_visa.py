from requests_html import HTMLSession
import requests
import smtplib
from email.mime.text import MIMEText
import time
from datetime import datetime
import schedule
import signal
import sys

# Check if an argument is passed
if len(sys.argv) < 2:
    print("Usage: python convert_argument.py <number>")
    sys.exit(1)

# Get the argument from the command line
arg = sys.argv[1]

try:
    # Convert the argument to a number
    duration = int(arg)
    print(f"Script will run every: {duration} seconds")
except ValueError:
    print(f"Error: '{arg}' is not a valid number.")
    sys.exit(1)


# Handle graceful shutdown
def handle_exit_signal(signum, frame):
    print(f"\nReceived signal {signum}, exiting gracefully...")
    sys.exit(0)

# Register the signal handlers
signal.signal(signal.SIGINT, handle_exit_signal)  # Handle Ctrl+C (SIGINT)
signal.signal(signal.SIGTERM, handle_exit_signal)  # Handle termination signal (SIGTERM)

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'  # Replace with your SMTP server
SMTP_PORT = 587  # Replace with your SMTP port
EMAIL_ADDRESS = 'emmettyoung92@gmail.com'  # Replace with your email
EMAIL_PASSWORD = 'idgj trub wjjj mhmj'  # Replace with your email password
TO_EMAIL = 'mail@mettyoung.com'

# URL to scrape
PEM = 'japan_visa.pem'
URL = 'https://coubic.com/Embassy-of-Japan/widget/calendar/914977?from_pc=listMonth&from_sp=listMonth'

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = TO_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Use TLS for secure email communication
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_appointments():
  # Get the current time
  now = datetime.now()
  current_hour = now.time().hour
  current_minute = now.time().minute
  print("Running script on", now)

  # Create an HTML session
  session = HTMLSession()

  # Make a GET request to the target URL
  response = session.get(URL, verify=PEM)

  # Render the JavaScript
  # Adjust sleep time as necessary
  response.html.render(sleep=3)
  content = response.html.text

  heartbeat_email_content = ""
  if content.find("2025年2月") > -1:
    heartbeat_email_content += "2025年2月 found\r\n"

  if content.find("3日日予定リスト") > -1:
    heartbeat_email_content += "3日日予定リスト found\r\n"

  # Send heartbeat every 4 hours
  send_heartbeat = current_hour %4 == 0 and current_minute == 0

  if content.find("No events to display") == -1:
    send_email("Slots available!", "Please visit " + URL)
  elif send_heartbeat:
    send_email("Script is running...\r\n", heartbeat_email_content)

  # Close the session
  session.close()

schedule.every(duration).seconds.do(check_appointments)

while True:
  schedule.run_pending()
  time.sleep(1)



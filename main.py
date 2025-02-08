import logging
import logging.handlers
import os
from requests_html import HTMLSession
import smtplib
from email.mime.text import MIMEText
import time
from datetime import datetime
import signal
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)


# Handle graceful shutdown
def handle_exit_signal(signum, frame):
    logger.info(f"Received signal {signum}, exiting gracefully...")
    sys.exit(0)

# Register the signal handlers
signal.signal(signal.SIGINT, handle_exit_signal)  # Handle Ctrl+C (SIGINT)
signal.signal(signal.SIGTERM, handle_exit_signal)  # Handle termination signal (SIGTERM)

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'  # Replace with your SMTP server
SMTP_PORT = 587  # Replace with your SMTP port

# URL to scrape
PEM = 'japan_visa.pem'
URL = 'https://coubic.com/Embassy-of-Japan/widget/calendar/914977?from_pc=listMonth&from_sp=listMonth'

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Use TLS for secure email communication
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, TO_EMAIL, msg.as_string())
        logger.info("Email sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def check_appointments():
  # Get the current time
  now = datetime.now()
  current_hour = now.time().hour
  current_minute = now.time().minute
  logger.info(f"Running script on ${now}")

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

if __name__ == "__main__":
  try:
    EMAIL_ADDRESS = os.environ["EMAIL"]
  except KeyError:
    logger.info("EMAIL not available!")
    raise

  try:
    EMAIL_PASSWORD = os.environ["PASSWORD"]
  except KeyError:
    logger.info("PASSWORD not available!")
    raise
  
  check_appointments()



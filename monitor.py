import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, date

def is_monitoring_active():
    today = date.today()
    start_date = date(2025, 3, 13)  # 2 days before event
    end_date = date(2025, 3, 25)
    return start_date <= today <= end_date

def get_page_content():
    url = "https://www.worldsurfleague.com/events/2025/ct/322/meo-rip-curl-pro-portugal/results"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text

def send_notification(message):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.environ['EMAIL_USER']
    sender_password = os.environ['EMAIL_PASSWORD']
    recipient_email = os.environ['NOTIFICATION_EMAIL']

    msg = MIMEText(message)
    msg['Subject'] = 'WSL Heat Draw Update Alert'
    msg['From'] = sender_email
    msg['To'] = recipient_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

def main():
    if not is_monitoring_active():
        print("Outside monitoring window")
        return

    try:
        content = get_page_content()
        current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Store hash in GitHub Actions artifact
        with open('last_hash.txt', 'a+') as f:
            f.seek(0)
            last_hash = f.read().strip()
            if last_hash and last_hash != current_hash:
                message = f"WSL page update detected at {datetime.now()}"
                send_notification(message)
            f.seek(0)
            f.truncate()
            f.write(current_hash)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise e

if __name__ == "__main__":
    main()

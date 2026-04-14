import imapclient
import email
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def fetch_latest_email():
    try:
        print("Step 1: Connecting to Gmail...")
        with imapclient.IMAPClient("imap.gmail.com", ssl=True) as client:

            print("Step 2: Logging in...")
            client.login(EMAIL, APP_PASSWORD)
            print(" Login successful")

            print("Step 3: Selecting INBOX...")
            client.select_folder("INBOX")

            print("Step 4: Searching emails...")
            messages = client.search(["UNSEEN"])
            print(f" Found {len(messages)} emails")

            if not messages:
                print(" No emails found")
                return None

            latest = messages[-1]
            client.add_flags([latest], [imapclient.SEEN])
            print(f"Step 5: Fetching email ID {latest}...")
            raw = client.fetch([latest], ["RFC822"])

            print("Step 6: Parsing email...")
            msg = email.message_from_bytes(raw[latest][b"RFC822"])
            subject = msg["subject"]
            sender = msg["from"]
            print(f" Subject: {subject}")
            print(f" Sender: {sender}")

            body = ""
            if msg.is_multipart():
                print("Step 7: Multipart email, extracting text...")
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        print(f" Body extracted: {body[:50]}...")
                        break
            else:
                print("Step 7: Single part email, extracting text...")
                body = msg.get_payload(decode=True).decode()
                print(f" Body extracted: {body[:50]}...")

            # Extract just the email address from sender
            if "<" in sender:
                sender_email = sender.split("<")[1].replace(">", "").strip()
            else:
                sender_email = sender.strip()

            return {
                "subject": subject,
                "sender": sender_email,
                "body": f"Subject: {subject}\n\n{body}"
            }

    except Exception as e:
        print(f" Error: {e}")
        return None


def send_reply(to_email, subject, body):
    try:
        print(f"Sending reply to {to_email}...")
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Re: " + subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.sendmail(EMAIL, to_email, msg.as_string())

        print(f" Reply sent to {to_email}")
        return True

    except Exception as e:
        print(f" Failed to send email: {e}")
        return False
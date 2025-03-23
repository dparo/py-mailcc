import imaplib
import email
import subprocess
import notify2
from email.header import decode_header
import base64
import time
import re

# Define IMAP server
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# List of accounts to check
EMAIL_ACCOUNTS = [
    {
        "email": "email1@gmail.com",
        "password": "password1",  # Leave blank if using XOAUTH2
        "xoauth2_token": "",  # Leave blank if using plain authentication
        "auth_method": "plain"  # Change to "xoauth2" for OAuth2 authentication
    },
    {
        "email": "email2@gmail.com",
        "password": "password2",
        "xoauth2_token": "",
        "auth_method": "plain"
    }
]

# Command to run when new email is received
COMMAND_TO_RUN = 'echo "New email received!"'


def authenticate_imap(email, password, xoauth2_token, auth_method):
    """Authenticate with either PLAIN (username/password) or XOAUTH2"""
    connection = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    
    if auth_method.lower() == 'plain':
        try:
            connection.login(email, password)
            print(f"Authenticated using PLAIN login for {email}.")
        except imaplib.IMAP4.error:
            print(f"Failed to authenticate with PLAIN login for {email}.")
            return None
    elif auth_method.lower() == 'xoauth2':
        auth_string = f"user={email}\x01auth=Bearer {xoauth2_token}\x01\x01"
        auth_string = base64.b64encode(auth_string.encode()).decode()
        try:
            connection.authenticate('XOAUTH2', lambda _: auth_string)
            print(f"Authenticated using XOAUTH2 for {email}.")
        except imaplib.IMAP4.error:
            print(f"Failed to authenticate with XOAUTH2 for {email}.")
            return None
    else:
        print(f"Invalid authentication method for {email}. Use 'plain' or 'xoauth2'.")
        return None

    return connection


def extract_sender_info(from_field):
    """Extracts sender's name and email address from the From field"""
    name, email_address = from_field, ""
    
    # Decode if necessary
    if isinstance(from_field, tuple):
        from_field = decode_header(from_field)[0]
        if isinstance(from_field[0], bytes):
            from_field = from_field[0].decode(from_field[1] or 'utf-8')

    # Extract email using regex
    match = re.search(r'(?P<name>.*?)\s*<(?P<email>[^>]+)>', from_field)
    if match:
        name = match.group("name").strip()
        email_address = match.group("email").strip()
    else:
        email_address = from_field  # If no name, assume the whole field is an email

    return name or email_address, email_address


def check_for_new_mail(connection, email_account):
    """Checks for new unread emails for a given email account"""
    connection.select('inbox')  # Select the INBOX
    result, data = connection.search(None, 'UNSEEN')  # Search for new emails

    if result == 'OK' and data != [b'']:
        for num in data[0].split():
            result, message_data = connection.fetch(num, '(RFC822)')
            for response_part in message_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extract Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or 'utf-8')

                    # Extract From
                    from_field = msg["From"]
                    sender_name, sender_email = extract_sender_info(from_field)

                    print(f"New email for {email_account} from: {sender_name} <{sender_email}>")
                    print(f"Subject: {subject}")

                    # Run command when a new email is received
                    subprocess.run(COMMAND_TO_RUN, shell=True)

                    # Show a notification with sender name, email, and subject
                    show_notification(email_account, sender_name, sender_email, subject)

                    return True  # Exit after processing the first new email
    return False


def show_notification(email_account, sender_name, sender_email, subject):
    """Displays a desktop notification"""
    notify2.init("Email Client")
    message = f"Account: {email_account}\nFrom: {sender_name} <{sender_email}>\nSubject: {subject}"
    notification = notify2.Notification("New Email", message)
    notification.show()


def main():
    """Main function to authenticate and check emails for multiple accounts"""
    connections = {}

    # Authenticate all email accounts
    for account in EMAIL_ACCOUNTS:
        connection = authenticate_imap(account["email"], account["password"], account["xoauth2_token"], account["auth_method"])
        if connection:
            connections[account["email"]] = connection

    if not connections:
        print("No successful IMAP connections.")
        return

    try:
        while True:
            for email_account, connection in connections.items():
                if check_for_new_mail(connection, email_account):
                    break  # Stop checking once a new email is found

            # Sleep for 5 seconds before checking again
            time.sleep(5)
    finally:
        for connection in connections.values():
            connection.logout()


if __name__ == '__main__':
    main()

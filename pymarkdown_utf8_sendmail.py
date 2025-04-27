import sys
import subprocess
import smtplib
import base64
import requests
import argparse
from email import message_from_file
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.generator import BytesGenerator
from io import BytesIO

# OAuth2 app credentials
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
TENANT_ID = 'your_tenant_id'
USERNAME = 'your_email@example.com'

TOKEN_ENDPOINT = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'

def get_access_token():
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://outlook.office365.com/.default',
        'grant_type': 'client_credentials'
    }
    response = requests.post(TOKEN_ENDPOINT, data=data)
    response.raise_for_status()
    return response.json()['access_token']

def generate_oauth2_string(username, access_token):
    auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()

def pandoc_convert(input_text, to_format):
    """Convert markdown text to specified format using pandoc."""
    process = subprocess.run(
        ['pandoc', '-f', 'markdown', '-t', to_format],
        input=input_text.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode != 0:
        raise Exception(f"Pandoc conversion error: {process.stderr.decode()}")
    return process.stdout.decode()

def create_alternative_part(markdown_text):
    """Create a multipart/alternative containing plain and HTML versions."""
    plain_text = pandoc_convert(markdown_text, 'plain')
    html_text = pandoc_convert(markdown_text, 'html')

    alt_part = MIMEMultipart('alternative')
    alt_part.attach(MIMEText(plain_text, 'plain'))
    alt_part.attach(MIMEText(html_text, 'html'))
    return alt_part

def rebuild_email(input_email):
    """Rebuilds the email: preserves headers, rebuilds body."""
    output_email = MIMEMultipart('mixed')

    # Copy all original headers
    for header, value in input_email.items():
        output_email[header] = value

    if input_email.is_multipart():
        for part in input_email.walk():
            if part.get_content_maintype() == 'multipart':
                continue  # Skip containers

            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)
            filename = part.get_filename()

            if content_type == 'text/markdown' and filename is None:
                # Convert main body markdown
                markdown_text = payload.decode(part.get_content_charset() or 'utf-8')
                alt_part = create_alternative_part(markdown_text)
                output_email.attach(alt_part)
            else:
                # Preserve attachments or other types
                new_part = MIMEBase(part.get_content_maintype(), part.get_content_subtype())
                new_part.set_payload(payload)
                encoders.encode_base64(new_part)

                for key, value in part.items():
                    new_part.add_header(key, value)

                output_email.attach(new_part)
    else:
        # If input email is not multipart, assume whole body is markdown
        markdown_text = input_email.get_payload(decode=True).decode(input_email.get_content_charset() or 'utf-8')
        alt_part = create_alternative_part(markdown_text)
        output_email.attach(alt_part)

    return output_email

def output_email_to_stdout(email_obj):
    """Writes the MIME email to stdout."""
    buffer = BytesIO()
    generator = BytesGenerator(buffer)
    generator.flatten(email_obj)
    sys.stdout.buffer.write(buffer.getvalue())

def send_email(email_obj):
    """Sends the MIME email over SMTP with OAuth2 authentication."""
    access_token = get_access_token()
    auth_string = generate_oauth2_string(USERNAME, access_token)

    with smtplib.SMTP('smtp.office365.com', 587) as smtp_conn:
        smtp_conn.ehlo()
        smtp_conn.starttls()
        smtp_conn.ehlo()

        smtp_conn.docmd('AUTH', 'XOAUTH2 ' + auth_string)
        smtp_conn.send_message(email_obj)

def main():
    parser = argparse.ArgumentParser(description="Send or output an email transformed from markdown body.")
    parser.add_argument('--stdout', action='store_true', help="Output the resulting email to stdout instead of sending")
    args = parser.parse_args()

    # Read the email from stdin
    input_email = message_from_file(sys.stdin)

    # Rebuild email structure
    output_email = rebuild_email(input_email)

    if args.stdout:
        output_email_to_stdout(output_email)
    else:
        send_email(output_email)

if __name__ == '__main__':
    main()


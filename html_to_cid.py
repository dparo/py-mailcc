#!/usr/bin/env python3

import os
import re
import base64
import uuid
import argparse
from bs4 import BeautifulSoup
from pathlib import Path
import mimetypes

def extract_and_replace_data_urls(html_content, output_dir):
    """
    Extract data URLs from HTML and replace them with CID references.
    Save the extracted images to the filesystem.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all <img> tags with src attribute
    img_tags = soup.find_all('img', src=True)

    # Dictionary to store CID to filename mapping
    cid_map = {}

    for img in img_tags:
        src = img['src']

        # Check if it's a data URL
        if src.startswith('data:'):
            # Extract mime type and base64 content
            match = re.match(r'data:([^;]+);base64,(.+)', src)
            if match:
                mime_type, base64_data = match.groups()

                # Generate a CID
                content_id = f"{uuid.uuid4()}@example.com"

                # Determine file extension based on MIME type
                extension = mimetypes.guess_extension(mime_type) or '.bin'
                if extension == '.jpe':  # Fix common MIME type issue
                    extension = '.jpg'

                # Generate filename
                filename = f"image_{len(cid_map)}{extension}"
                filepath = os.path.join(output_dir, filename)

                # Save image to filesystem
                try:
                    image_data = base64.b64decode(base64_data)
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    print(f"Saved image to {filepath}")

                    # Replace data URL with CID reference
                    img['src'] = f"cid:{content_id}"

                    # Store mapping
                    cid_map[content_id] = filename

                except Exception as e:
                    print(f"Error processing image: {e}")

    # Return the modified HTML and CID mapping
    return str(soup), cid_map

def main():
    parser = argparse.ArgumentParser(description='Convert inline images to CID references')
    parser.add_argument('html_file', help='Path to the HTML file')
    parser.add_argument('--output-dir', '-o', default='extracted_images',
                        help='Directory to save extracted images (default: ./extracted_images)')
    args = parser.parse_args()

    # Read the HTML file
    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"Error: File '{args.html_file}' not found")
        return

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Process the HTML
    new_html, cid_map = extract_and_replace_data_urls(html_content, args.output_dir)

    # Write the modified HTML file
    output_html_path = html_path.with_name(f"{html_path.stem}_with_cid{html_path.suffix}")
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"\nModified HTML saved to: {output_html_path}")
    print(f"\nCID to filename mappings:")
    for cid, filename in cid_map.items():
        print(f"cid:{cid} -> {filename}")

if __name__ == "__main__":
    main()

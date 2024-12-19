import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from typing import Dict
import requests  # To download the image from the URL

# Load environment variables from .env file
load_dotenv()

def send_email(report_details: Dict) -> Dict:
    """
    Send an email with report details and attach an image.

    :param report_details: Dictionary containing email details.
    :return: Dictionary with success status and message.
    """
    # Load credentials from environment variables
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = report_details.get("recipient_email")
    image_url = report_details.get("image_url")  # URL of the image on Cloudinary

    if not sender_email or not sender_password:
        return {"success": False, "message": "Sender email or password not configured."}

    if not recipient_email:
        return {"success": False, "message": "Recipient email is missing."}

    # Email content
    subject = "Laporan Kecelakaan Baru"
    body = f"""
    Laporan Baru:
    Provinsi: {report_details.get("province", "N/A")}
    Kota: {report_details.get("city", "N/A")}
    Kecamatan: {report_details.get("district", "N/A")}
    Deskripsi: {report_details.get("description", "N/A")}
    """

    try:
        # Construct the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Download the image from the URL
        if image_url:
            response = requests.get(image_url)
            response.raise_for_status()  # Raise an error for HTTP issues
            filename = os.path.basename(image_url)

            # Attach the downloaded image
            part = MIMEBase("application", "octet-stream")
            part.set_payload(response.content)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={filename}",
            )
            message.attach(part)

        # Send email via SMTP server
        print("Connecting to the SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        print("Sending email...")
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        print("Email sent successfully.")
        return {"success": True, "message": "Email sent successfully."}

    except Exception as e:
        print(f"Failed to send email: {e}")
        return {"success": False, "message": f"Failed to send email: {e}"}

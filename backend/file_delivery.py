"""
Automated File Delivery System
Handles file delivery after purchase with email notifications
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
import zipfile
from typing import List, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileDeliveryManager:
    """Manage file delivery and package creation"""
    
    def __init__(self):
        self.delivery_log_path = 'logs/deliveries.json'
        self.files_directory = os.getenv('FILES_DIRECTORY', 'files/products')
        self.s3_enabled = os.getenv('USE_S3', False)
        
        if self.s3_enabled:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.s3_bucket = os.getenv('S3_BUCKET_NAME')
    
    def create_delivery_package(self, product_id: str, product_data: Dict) -> str:
        """Create downloadable package for product"""
        try:
            package_path = f"{self.files_directory}/{product_id}/package.zip"
            os.makedirs(os.path.dirname(package_path), exist_ok=True)
            
            # Create ZIP with product files
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add product metadata
                zipf.writestr('README.txt', self._generate_readme(product_data))
                
                # Add product files
                product_files_dir = f"{self.files_directory}/{product_id}/files"
                if os.path.exists(product_files_dir):
                    for root, dirs, files in os.walk(product_files_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, product_files_dir)
                            zipf.write(file_path, arcname)
                
                logger.info(f"Package created: {package_path}")
            
            # Upload to S3 if enabled
            if self.s3_enabled:
                self._upload_to_s3(package_path, f"products/{product_id}/package.zip")
            
            return package_path
        
        except Exception as e:
            logger.error(f"Error creating package: {e}")
            raise
    
    def generate_download_link(self, sale_id: str, product_id: str, expiration_hours: int = 24) -> str:
        """Generate secure download link for purchased file"""
        try:
            if self.s3_enabled:
                # Generate S3 presigned URL
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': self.s3_bucket,
                        'Key': f"products/{product_id}/package.zip"
                    },
                    ExpiresIn=expiration_hours * 3600
                )
            else:
                # Generate local download URL
                url = f"/api/fiilthy/downloads/{sale_id}?token={self._generate_token(sale_id)}"
            
            logger.info(f"Download link generated for sale: {sale_id}")
            return url
        
        except Exception as e:
            logger.error(f"Error generating download link: {e}")
            raise
    
    def _generate_readme(self, product_data: Dict) -> str:
        """Generate README file for package"""
        readme = f"""
THANK YOU FOR YOUR PURCHASE!

Product: {product_data.get('title', 'Product')}
Purchase Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONTENTS:
{chr(10).join(f"- {item}" for item in product_data.get('includes', ['Files included']))}

SUPPORT:
Email: support@fiilthy.com
Website: https://fiilthy.com

USAGE:
Please refer to the included documentation for usage instructions.
"""
        return readme.strip()
    
    def _upload_to_s3(self, file_path: str, s3_key: str) -> str:
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(
                file_path,
                self.s3_bucket,
                s3_key,
                ExtraArgs={'ContentType': 'application/zip'}
            )
            logger.info(f"File uploaded to S3: {s3_key}")
            return f"s3://{self.s3_bucket}/{s3_key}"
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise
    
    def _generate_token(self, sale_id: str) -> str:
        """Generate secure download token"""
        import hashlib
        token = hashlib.sha256(f"{sale_id}{datetime.now().timestamp()}".encode()).hexdigest()
        return token
    
    def log_delivery(self, sale_id: str, product_id: str, email: str, status: str):
        """Log delivery event"""
        try:
            delivery_log = []
            if os.path.exists(self.delivery_log_path):
                with open(self.delivery_log_path, 'r') as f:
                    delivery_log = json.load(f)
            
            delivery_log.append({
                'sale_id': sale_id,
                'product_id': product_id,
                'email': email,
                'status': status,
                'timestamp': datetime.now().isoformat()
            })
            
            os.makedirs(os.path.dirname(self.delivery_log_path), exist_ok=True)
            with open(self.delivery_log_path, 'w') as f:
                json.dump(delivery_log, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error logging delivery: {e}")

class EmailNotificationService:
    """Send email notifications for purchases and deliveries"""
    
    def __init__(self):
        self.sender_email = os.getenv('EMAIL_FROM', 'noreply@fiilthy.com')
        self.sender_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', 587))
        self.use_sendgrid = os.getenv('USE_SENDGRID', False)
    
    def send_purchase_confirmation(self, to_email: str, product_name: str, amount: float, download_link: str):
        """Send purchase confirmation email"""
        try:
            subject = f"Purchase Confirmation - {product_name}"
            
            body = f"""
Dear Customer,

Thank you for purchasing {product_name}!

Purchase Details:
- Product: {product_name}
- Amount: ${amount:.2f}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DOWNLOAD YOUR PURCHASE:
{download_link}

This link will expire in 24 hours.

If you have any questions, please contact us at support@fiilthy.com

Best regards,
Fiilthy Team
"""
            
            self._send_email(to_email, subject, body)
            logger.info(f"Purchase confirmation sent to {to_email}")
        
        except Exception as e:
            logger.error(f"Error sending confirmation: {e}")
    
    def send_download_reminder(self, to_email: str, product_name: str, download_link: str):
        """Send download reminder email"""
        try:
            subject = f"Your Download Link - {product_name}"
            
            body = f"""
Hi there,

Your download link for {product_name} is ready!

DOWNLOAD HERE:
{download_link}

This link expires in 24 hours. Make sure to download your product before it expires.

Questions? Contact us at support@fiilthy.com

Best regards,
Fiilthy Team
"""
            
            self._send_email(to_email, subject, body)
            logger.info(f"Download reminder sent to {to_email}")
        
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    def send_receipt(self, to_email: str, sale_details: Dict, product_details: Dict):
        """Send detailed receipt"""
        try:
            subject = f"Receipt #{sale_details['id']}"
            
            body = f"""
FIILTHY - PURCHASE RECEIPT

Receipt #: {sale_details['id']}
Date: {sale_details.get('created_at', datetime.now().isoformat())}
Customer Email: {to_email}

PRODUCT:
{product_details['title']}

AMOUNT: ${sale_details['amount']:.2f}
Payment Method: Credit Card
Status: {sale_details['status'].upper()}

DOWNLOAD:
{sale_details.get('download_url', 'N/A')}

Thank you for your business!

Fiilthy Team
support@fiilthy.com
"""
            
            self._send_email(to_email, subject, body)
            logger.info(f"Receipt sent to {to_email}")
        
        except Exception as e:
            logger.error(f"Error sending receipt: {e}")
    
    def _send_email(self, to_email: str, subject: str, body: str):
        """Send email via SMTP or SendGrid"""
        try:
            if self.use_sendgrid:
                self._send_via_sendgrid(to_email, subject, body)
            else:
                self._send_via_smtp(to_email, subject, body)
        
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            raise
    
    def _send_via_smtp(self, to_email: str, subject: str, body: str):
        """Send via SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
    
    def _send_via_sendgrid(self, to_email: str, subject: str, body: str):
        """Send via SendGrid API"""
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        message = Mail(
            from_email=self.sender_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        sg.send(message)

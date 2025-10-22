"""
Notification module for sending email and SMS notifications.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationConfig:
    """Configuration for notification services."""
    
    def __init__(self, smtp_server='smtp.gmail.com', smtp_port=587, 
                 smtp_username='', smtp_password='', smtp_from=''):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_from = smtp_from or smtp_username
        self.sms_enabled = False
        self.sms_api_key = ''


class EmailNotificationService:
    """Service for sending email notifications."""
    
    def __init__(self, config):
        self.config = config
    
    def send_email(self, to_email, subject, body):
        """
        Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.config.smtp_username or not self.config.smtp_password:
            logger.warning("SMTP credentials not configured. Email not sent.")
            logger.info(f"Would have sent email to {to_email}: {subject}")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_order_ready_notification(self, order):
        """
        Send order ready notification email.
        
        Args:
            order: Order object with customer and order details
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        subject = f"Order #{order['id']} is Ready for Pickup"
        
        body = f"""
        <html>
        <body>
            <h2>Your Order is Ready!</h2>
            <p>Dear {order['customer_name']},</p>
            <p>Great news! Your order is now ready for pickup.</p>
            
            <h3>Order Details:</h3>
            <ul>
                <li><strong>Order ID:</strong> #{order['id']}</li>
                <li><strong>Item:</strong> {order['item_description']}</li>
                <li><strong>Quantity:</strong> {order['quantity']}</li>
                <li><strong>Total Price:</strong> ${order['total_price']:.2f}</li>
                <li><strong>Status:</strong> {order['status']}</li>
            </ul>
            
            <p>Please come pick up your order at your earliest convenience.</p>
            <p>Thank you for your business!</p>
            
            <p>Best regards,<br>Order Management System</p>
        </body>
        </html>
        """
        
        return self.send_email(order['customer_email'], subject, body)


class SMSNotificationService:
    """Service for sending SMS notifications (stub implementation)."""
    
    def __init__(self, config):
        self.config = config
    
    def send_sms(self, to_phone, message):
        """
        Send an SMS notification.
        
        This is a stub implementation. In production, integrate with a service
        like Twilio, AWS SNS, or other SMS gateway.
        
        Args:
            to_phone: Recipient phone number
            message: SMS message content
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.config.sms_enabled:
            logger.info(f"SMS notifications not enabled. Would have sent to {to_phone}: {message}")
            return False
        
        logger.info(f"SMS stub: Sending to {to_phone}")
        logger.info(f"SMS stub: Message - {message}")
        
        return True
    
    def send_order_ready_sms(self, order):
        """
        Send order ready notification via SMS.
        
        Args:
            order: Order object with customer and order details
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not order.get('customer_phone'):
            logger.warning(f"No phone number for order #{order['id']}")
            return False
        
        message = (f"Your order #{order['id']} is ready for pickup! "
                  f"Item: {order['item_description']}, "
                  f"Total: ${order['total_price']:.2f}")
        
        return self.send_sms(order['customer_phone'], message)


class NotificationManager:
    """Manages all notification services."""
    
    def __init__(self, config=None):
        self.config = config or NotificationConfig()
        self.email_service = EmailNotificationService(self.config)
        self.sms_service = SMSNotificationService(self.config)
    
    def notify_order_ready(self, order):
        """
        Send notifications when order is marked as ready.
        
        Args:
            order: Order object with customer and order details
            
        Returns:
            dict: Status of email and SMS notifications
        """
        results = {
            'email_sent': False,
            'sms_sent': False
        }
        
        logger.info(f"Sending order ready notifications for order #{order['id']}")
        
        results['email_sent'] = self.email_service.send_order_ready_notification(order)
        
        if order.get('customer_phone'):
            results['sms_sent'] = self.sms_service.send_order_ready_sms(order)
        
        return results
    
    def update_config(self, smtp_server=None, smtp_port=None, 
                     smtp_username=None, smtp_password=None, smtp_from=None,
                     sms_enabled=None, sms_api_key=None):
        """
        Update notification configuration.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            smtp_username: SMTP username
            smtp_password: SMTP password
            smtp_from: From email address
            sms_enabled: Enable SMS notifications
            sms_api_key: SMS service API key
        """
        if smtp_server is not None:
            self.config.smtp_server = smtp_server
        if smtp_port is not None:
            self.config.smtp_port = smtp_port
        if smtp_username is not None:
            self.config.smtp_username = smtp_username
        if smtp_password is not None:
            self.config.smtp_password = smtp_password
        if smtp_from is not None:
            self.config.smtp_from = smtp_from
        if sms_enabled is not None:
            self.config.sms_enabled = sms_enabled
        if sms_api_key is not None:
            self.config.sms_api_key = sms_api_key

import imaplib
import email
from email.header import decode_header
import logging
from django.conf import settings
from celery import shared_task
from orders.models import Order

# Configure logging
logger = logging.getLogger(__name__)

@shared_task
def check_emails():
    logger.info("Starting check_emails task")
    try:
        # Connect to email server
        logger.debug("Connecting to IMAP server: %s", settings.EMAIL_HOST)
        mail = imaplib.IMAP4_SSL(settings.EMAIL_HOST)
        logger.debug("Logging in as: %s", settings.EMAIL_HOST_USER)
        mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        logger.info("Successfully logged in to email server")
        
        # Select inbox
        mail.select('INBOX')
        logger.info("Selected INBOX")
        
        # Search for unread emails from warehouse
        logger.debug("Searching for unread emails from: %s", settings.WAREHOUSE_EMAIL)
        result, data = mail.search(None, f'FROM {settings.WAREHOUSE_EMAIL} UNSEEN')
        if result != 'OK':
            logger.error("Failed to search emails: %s", result)
            mail.logout()
            return
        
        email_count = len(data[0].split())
        logger.info("Found %d unread emails from warehouse", email_count)
        
        for num in data[0].split():
            logger.debug("Fetching email number: %s", num)
            result, data = mail.fetch(num, '(RFC822)')
            if result != 'OK':
                logger.error("Failed to fetch email %s: %s", num, result)
                continue
            
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Decode subject
            subject, encoding = decode_header(msg['subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')
            logger.debug("Processing email with subject: %s", subject)
            
            # Check for confirmation keywords
            if 'order ready to dispatch' in subject.lower() or 'is ready' in subject.lower():
                logger.info("Found confirmation email with subject: %s", subject)
                # Extract order number
                for part in subject.split():
                    if part.isdigit():
                        order_id = part
                        logger.debug("Extracted order ID: %s", order_id)
                        try:
                            order = Order.objects.get(id=order_id)
                            logger.info("Found order %s for customer %s", order_id, order.customer_name)
                            order.status = 'Confirmed'
                            order.save()
                            logger.info("Updated order %s to Confirmed", order_id)
                            
                            # Send confirmation email
                            from django.core.mail import send_mail
                            send_mail(
                                f'Order #{order.id} Confirmed',
                                f'Your order #{order.id} is ready to dispatch.',
                                settings.DEFAULT_FROM_EMAIL,
                                [order.user_email],
                            )
                            logger.info("Sent confirmation email to %s", order.user_email)
                            
                            # Mark email as read
                            logger.debug("Marking email %s as read", num)
                            mail.store(num, '+FLAGS', '\\Seen')
                            logger.info("Email %s marked as read", num)
                            
                        except Order.DoesNotExist:
                            logger.warning("Order %s not found", order_id)
                            # Still mark as read to avoid reprocessing
                            mail.store(num, '+FLAGS', '\\Seen')
                            logger.info("Email %s marked as read despite order not found", num)
                            continue
            else:
                logger.debug("Email subject does not contain confirmation keywords")
                # Mark non-matching emails as read to avoid reprocessing
                mail.store(num, '+FLAGS', '\\Seen')
                logger.info("Email %s marked as read (no keywords)", num)
        
        # Commit changes and logout
        mail.expunge()
        mail.logout()
        logger.info("Logged out from email server")
        
    except Exception as e:
        logger.error("Error in check_emails task: %s", str(e), exc_info=True)
        raise
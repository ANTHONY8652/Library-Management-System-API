"""
Custom email backend for Brevo (formerly Sendinblue) using REST API.
This works on hosting providers like Render that block SMTP ports.
"""
import logging
import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class BrevoAPIEmailBackend(BaseEmailBackend):
    """
    Email backend for Brevo using their REST API.
    Uses HTTPS (port 443) which is not blocked by hosting providers.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.api_url = 'https://api.brevo.com/v3/smtp/email'
        self.timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
        
        if not self.api_key:
            logger.warning('BREVO_API_KEY is not set. Emails will not be sent.')
    
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of emails sent.
        """
        if not email_messages:
            return 0
        
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError('BREVO_API_KEY is not set in settings.')
            return 0
        
        num_sent = 0
        for message in email_messages:
            if self._send_email(message):
                num_sent += 1
        
        return num_sent
    
    def _send_email(self, email_message):
        """
        Send a single email message using Brevo API.
        """
        try:
            # Prepare the email data for Brevo API
            payload = {
                'sender': {
                    'name': getattr(settings, 'DEFAULT_FROM_NAME', 'Library Management System'),
                    'email': email_message.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
                },
                'to': [{'email': email} for email in email_message.to],
                'subject': email_message.subject,
                'htmlContent': email_message.body if email_message.content_subtype == 'html' else None,
                'textContent': email_message.body if email_message.content_subtype != 'html' else None,
            }
            
            # Add CC if present
            if email_message.cc:
                payload['cc'] = [{'email': email} for email in email_message.cc]
            
            # Add BCC if present
            if email_message.bcc:
                payload['bcc'] = [{'email': email} for email in email_message.bcc]
            
            # Add reply-to if present
            if hasattr(email_message, 'reply_to') and email_message.reply_to:
                payload['replyTo'] = {'email': email_message.reply_to[0]}
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            # If both htmlContent and textContent are None, use textContent
            if not payload.get('htmlContent') and not payload.get('textContent'):
                payload['textContent'] = email_message.body
            
            # Make API request
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'api-key': self.api_key,
            }
            
            logger.info(f'Sending email via Brevo API to: {email_message.to}')
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            
            # Check response
            if response.status_code == 201:
                response_data = response.json()
                message_id = response_data.get('messageId', 'unknown')
                logger.info(f'✅ Email sent successfully via Brevo API. Message ID: {message_id}')
                return True
            else:
                error_msg = f'Brevo API error: {response.status_code} - {response.text}'
                logger.error(error_msg)
                if not self.fail_silently:
                    raise Exception(error_msg)
                return False
                
        except requests.exceptions.Timeout:
            error_msg = f'Timeout connecting to Brevo API (timeout: {self.timeout}s)'
            logger.error(error_msg)
            if not self.fail_silently:
                raise Exception(error_msg)
            return False
        except requests.exceptions.RequestException as e:
            error_msg = f'Error connecting to Brevo API: {str(e)}'
            logger.error(error_msg)
            if not self.fail_silently:
                raise Exception(error_msg)
            return False
        except Exception as e:
            error_msg = f'Unexpected error sending email via Brevo API: {str(e)}'
            logger.error(error_msg, exc_info=True)
            if not self.fail_silently:
                raise
            return False


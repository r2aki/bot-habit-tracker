from services.notification_service import notification_service
import logging

logger = logging.getLogger(__name__)

def start_scheduler():
    """Start the notification scheduler"""
    notification_service.start()

def stop_scheduler():
    """Stop the notification scheduler"""
    notification_service.stop()
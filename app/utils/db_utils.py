import time
import logging
from functools import wraps
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)

def retry_on_db_lock(max_retries=3, retry_delay=0.5):
    """
    Decorator to retry database operations when encountering a database lock error.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        retry_delay (float): Delay in seconds between retries, with exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = retry_delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    if "database is locked" in str(e) and retries < max_retries:
                        retries += 1
                        logger.warning(f"Database locked, retrying operation ({retries}/{max_retries}) after {current_delay}s delay")
                        time.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff
                    else:
                        # If it's not a lock error or we've exhausted retries, re-raise the exception
                        logger.error(f"Database error after {retries} retries: {e}")
                        raise
            
            # If we got here, we've exhausted retries without success
            raise OperationalError("Database operation failed after maximum retries due to locks")
        return wrapper
    return decorator

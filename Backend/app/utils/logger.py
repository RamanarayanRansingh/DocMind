import logging
from datetime import datetime
import os

log_directory = 'logs'
os.makedirs(log_directory, exist_ok=True)

log_filename = os.path.join(log_directory, f"log_{datetime.now().strftime('%y-%m-%d')}.log")

# Ensure logs are written immediately
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def log_error(error: Exception, additional_info: str = None):
    error_message = f"Error: {str(error)}"
    if additional_info:
        error_message += f" | Additional Info: {additional_info}"
    logger.error(error_message)
    file_handler.flush()  # Ensure logs are written to file

def log_info(message: str):
    logger.info(message)
    file_handler.flush()

def log_warning(message: str):
    logger.warning(message)
    file_handler.flush()

def log_api_request(request_method: str, endpoint: str, user_id: int = None):
    message = f"API Request - Method: {request_method} | Endpoint: {endpoint}"
    if user_id:
        message += f" | User ID: {user_id}"
    logger.info(message)
    file_handler.flush()
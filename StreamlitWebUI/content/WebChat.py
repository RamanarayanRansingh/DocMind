from components.webrag import web_chat_interface
from utils.helpers import check_authentication

def show():
    check_authentication()
    web_chat_interface()
import requests
from colorama import just_fix_windows_console
just_fix_windows_console()
from colorama import init
init()
from colorama import Fore, Back, Style
import json
import time
import uuid

def get_random_uuid():
    return str(uuid.uuid4())
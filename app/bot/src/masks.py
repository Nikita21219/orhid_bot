import requests
import datetime
# from config import URL_APPOINTMENTS, HEADERS_AUTH
import re


def is_date(data):
    return True if len(data.split("-")) == 3 else False


def is_time(data):
    data_list = data.split(':')
    return len(data_list) == 2 and data_list[0].isdigit() and data_list[1].isdigit()


def is_full_name(data):
    return len(data.split()) == 2


def is_phone_number(text):
    pattern = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'
    return 1 if re.search(pattern, text) else 0

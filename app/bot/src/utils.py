import datetime
from babel.dates import format_datetime


def get_date_ru(datetime_date):
    date = datetime.datetime.strptime(datetime_date, '%Y-%m-%d')
    return format_datetime(date, 'd MMMM', locale='ru_RU')


def phone_to_crm_format(phone: str):
    """
    :param phone:
    :return: phone in format like +7-111-111-11-11
    """
    lst_phone = [digit for digit in phone if digit.isdigit()]
    if len(lst_phone) == 10:
        lst_phone.insert(0, '7')
    else:
        lst_phone[0] = '7'
    return ''.join(digit for digit in lst_phone)

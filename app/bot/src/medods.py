from collections import defaultdict
from typing import List

from config import *
from redis_storage import RedisStorage
import jwt
import utils
import datetime
import time
import requests
import threading


class Medods:
    """
    users are doctors
    """
    def __init__(self):
        self.users_result = self.get_users_from_cache()
        self.min_delta_appointment = datetime.timedelta(minutes=20)

    def get_client_id_by_full_name(self, surname, phone):
        params = {
            'surname': surname,
            'phone': phone,
            'limit': 1,
            'offset': 0,
        }
        response = requests.get(URL_CLIENTS, headers=self.get_auth(), params=params)
        print(f'{response.status_code}: {response.text}')
        try:
            if response.status_code == 200:
                return response.json()['data'][0]['id']
        except:
            return None

    def create_client(self, phone, client_full_name):
        surname, name = client_full_name.split()
        create_client_params = {
            'phone': phone,
            'surname': surname,
            'name': name,
        }
        data = self.check_client(phone)
        for user in data:
            if user['surname'] == surname:
                return user.get('id')
        try:
            result = requests.post(URL_CLIENTS, headers=self.get_auth(), json=create_client_params)
            if result.status_code == 422:
                return self.get_client_id_by_full_name(surname, phone)
            elif result.status_code != 200:
                return None
            return result.json().get('id')
        except:
            return None

    def get_schedule_users(self, user_ids: List[int]):
        day = datetime.datetime.now()
        start_date = day.strftime("%Y-%m-%d")
        end_date = (day + datetime.timedelta(days=28)).strftime("%Y-%m-%d")
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'clinicId': 1,
            'userIds': user_ids,
        }
        response = requests.post(URL_SCHEDULES, headers=self.get_auth(), json=params)
        if response.status_code != 200:
            return print(f"{response.status_code}: {response.text}")
        data = response.json().get('grid')
        return data

    def check_client(self, phone: str):
        params = {
            'phone': phone,
            'limit': 100,
            'offset': 0,
        }
        response = requests.get(URL_CLIENTS, headers=self.get_auth(), params=params)
        if response.status_code != 200:
            print(f"{response.status_code}: {response.text}")
            return list()
        return response.json().get('data')

    def get_user_full_name(self, user_id: int):
        for user in self.users_result:
            if user.get('id') == user_id:
                return f"{user.get('surname')} {user.get('name')}"
        return None

    def get_worktime_list(self, data, date: str, user_id: str):
        worktime = []
        for work_time in data[date][user_id]['workTimes']:
            time_start, time_end = work_time['timeRange'].split('-')
            time_start = datetime.datetime.strptime(f"{date} {time_start}", '%Y-%m-%d %H:%M')
            time_end = datetime.datetime.strptime(f"{date} {time_end}", '%Y-%m-%d %H:%M')
            worktime_dict = {
                'time_start': time_start,
                'time_end': time_end,
            }
            worktime.append(worktime_dict)
        return worktime

    def get_busy_times(self, data, date, user_id):
        busy_times = []
        for appointment in data[date][str(user_id)]['appointments']:
            delta_appointment = datetime.timedelta(minutes=appointment['duration'])
            start_appointment = datetime.datetime.strptime(
                date + ' ' + appointment['time'],
                '%Y-%m-%d %H:%M'
            )
            end_appointment = start_appointment + delta_appointment
            appointment_dict = {
                'start_appointment': start_appointment,
                'end_appointment': end_appointment,
            }
            busy_times.append(appointment_dict)
        return sorted(busy_times, key=lambda k: k['start_appointment'])

    def get_free_times(self, busy_times, worktime, user_id):
        free_times = []
        appointment_duration = self.get_appointment_duration(int(user_id))
        if busy_times:
            first_appointment = busy_times[0]['start_appointment']
            last_appointment = busy_times[len(busy_times) - 1]['end_appointment']
            for wt in worktime:
                start_worktime = wt['time_start']
                if first_appointment > start_worktime:
                    while first_appointment != start_worktime:
                        first_appointment -= appointment_duration
                        if first_appointment < start_worktime:
                            break
                        else:
                            free_times.append(first_appointment.strftime('%H:%M'))
                end_worktime = wt['time_end']
                while end_worktime - last_appointment >= appointment_duration:
                    free_times.append(last_appointment.strftime('%H:%M'))
                    last_appointment += appointment_duration
        else:
            for wt in worktime:
                cur = wt['time_start']
                end_worktime = wt['time_end']
                while cur <= end_worktime - appointment_duration:
                    free_times.append(cur.strftime('%H:%M'))
                    cur += appointment_duration

        # Дополняю список свободным временем для записи, которое доступно между приемами
        for i in range(len(busy_times) - 1):
            start_time_next_appointment = busy_times[i + 1]['start_appointment']
            end_time_appointment = busy_times[i]['end_appointment']
            while start_time_next_appointment - end_time_appointment >= appointment_duration:
                for td in worktime:
                    if td['time_start'] <= end_time_appointment < td['time_end'] and self.time_is_not_busy(end_time_appointment, busy_times):
                        free_times.append(end_time_appointment.strftime('%H:%M'))
                        break
                end_time_appointment += appointment_duration

        return sorted(free_times)

    def time_is_not_busy(self, time, busy_times):
        for appointment in busy_times:
            if appointment['start_appointment'] < time < appointment['end_appointment']:
                return False
        return True

    def get_times(self, user_id: str, date: str):
        data = RedisStorage().load_data('schedule')

        # Формирую список словарей с графиком работы врача
        worktime = self.get_worktime_list(data, date, user_id)

        # Формирую список из словарей со временем начала и конца приема
        busy_times = self.get_busy_times(data, date, user_id)

        # Формирую список со свободным временем, которое доступно для записи перед первым приемом и после последнего
        free_times = self.get_free_times(busy_times, worktime, user_id)

        return free_times

    def gen_token(self):
        unix_time = int(time.time())
        payload = {
            "iss": CRM_ISS,
            "iat": unix_time,
            "exp": unix_time + 60
        }
        token = jwt.encode(payload, CRM_SECRET_KEY, algorithm='HS512')
        return token

    def get_users_from_cache(self):
        return RedisStorage().load_data('users')

    def get_available_days_from_cache(self, user_id: str):
        data = RedisStorage().load_data('schedule')
        available_days = []
        for date in data:
            for doctor_id in data[date]:
                if doctor_id == user_id and self.get_times(user_id, date):
                    available_days.append(date)
                    break
        return available_days

    def get_users_from_crm(self):
        all_users = []
        limit = 100
        offset = total_items = 0
        while offset <= total_items:
            params = {
                'limit': limit,
                'offset': offset,
                'status': 'active',
                'hasAppointment': True,
                'currentClinicId': 1,
                'clinicId': 1,
                'userGroup': 'medical_staff'
            }
            auth = self.get_auth()
            response = requests.get(URL_USERS, headers=auth, params=params)
            if response.status_code == 200:
                response_data = response.json()
                all_users += response_data['data']
                total_items = response_data['totalItems']
            else:
                print(f'{response.status_code}: {response.text}')
            offset += limit
            time.sleep(0.5)

        users = [user for user in all_users if
                 user['specialties'][0]['title'] != 'Медсестра' and
                 user['surname'] != 'Дневной Стационар']

        return sorted(users, key=lambda d: d['surname'])

    def get_appointments(self, doctor_id, date):
        check_appointment_params = {
            'clinicId': 1,
            'userId': doctor_id,
            'dateStart': date,
            'dateEnd': date,
            'limit': 100,
            'offset': 0,
        }
        response = requests.get(URL_APPOINTMENTS, headers=self.get_auth(), params=check_appointment_params)
        if response.status_code != 200:
            return print(f'{response.status_code}: {response.text}')
        result = response.json()['data']
        return result[0] if result else result

    def make_appointment(self, data: dict) -> bool:
        params = {
            'duration': data['duration'],
            'clinicId': 1,
            'date': data['chosen_date'],
            'time': data['chosen_time'],
            'userId': data['user_id'],
            'clientId': data['client_id'],
            'appointmentTypeId': 1,
            'appointmentSourceId': 2,
            'note': 'Запись из бота телеграм',
        }
        response = requests.post(URL_APPOINTMENTS, headers=self.get_auth(), json=params)
        if response.status_code == 200:
            if "errors.appointment_intersects_with_existing_ones" in response.text:
                return False
            return True
        return False

    def filter_users_by_schedule(self):
        schedule = RedisStorage().load_data('schedule')
        users = []
        for user in self.users_result:
            user_id = str(user['id'])
            for date in schedule:
                if user_id in schedule[date]:
                    if schedule[date][user_id]['workTimes'] and self.get_available_days_from_cache(user_id):
                        users.append(user)
                        break
        RedisStorage().dump_data(users, 'users')

    def update_users(self):
        users = self.get_users_from_crm()
        RedisStorage().dump_data(users, 'users')

    def update_schedule(self):
        users = self.get_users_from_cache()
        user_ids = [user['id'] for user in users]
        schedule = self.get_schedule_users(user_ids)
        RedisStorage().dump_data(schedule, 'schedule')

    def update_token(self, token):
        r = RedisStorage()
        r.set('token', token)

    def get_appointment_duration(self, user_id: int):
        duration = None
        for user in self.users_result:
            if user_id == user.get('id'):
                duration = datetime.timedelta(minutes=user.get('appointmentDuration'))
                break
        return duration if duration else self.min_delta_appointment

    def get_auth(self):
        auth = {
            'Authorization': RedisStorage().get('token'),
            'Content-Type': 'application/json'
        }
        return auth


if __name__ == '__main__':
    medods = Medods()
    medods.update_token(medods.gen_token())
    for user in medods.users_result:
        print(user, "\n\n")


    # print('token:', medods.get_auth())

    # user_ids = [user['id'] for user in medods.users_result]
    # for user in medods.users_result:
    #     print(user, '\n')

    # {'id': 160, 'surname': 'Корнилова', 'name': 'Анастасия', 'secondName': 'Вадимовна', 'email': '', 'birthdate': None, 'status': 'active', 'phone': '79227180447', 'hasAppointment': True, 'appointmentDuration': 30, 'note': 'с 3 лет', 'currentClinicId': 1, 'clinicIds': [1], 'onlineRecordingInformation': None, 'availabilityForOnlineRecording': 'not_available', 'userGroups': ['medical_staff'], 'specialties': [{'id': 72, 'title': 'Невролог', 'userGroup': 'medical_staff'}], 'code': '', 'sex': 'female', 'avatars': None}

    # {'id': 142, 'surname': 'Трошина', 'name': 'Надежда ', 'secondName': 'Анатольевна', 'email': '', 'birthdate': None, 'status': 'active', 'phone': '79028634323', 'hasAppointment': True, 'appointmentDuration': 30, 'note': 'УЗИ БЕЗ ПРИЕМА НЕ ДЕЛАЕТ!!!     \r\n89823370911. ', 'currentClinicId': 1, 'clinicIds': [1], 'onlineRecordingInformation': None, 'availabilityForOnlineRecording': 'not_available', 'userGroups': ['medical_staff'], 'specialties': [{'id': 12, 'title': 'Акушер-гинеколог', 'userGroup': 'medical_staff'}], 'code': '', 'sex': 'female', 'avatars': None}

    # {'id': 89, 'surname': 'Корнилова', 'name': 'Ирина', 'secondName': 'Николаевна', 'email': '', 'birthdate': '1963-04-04', 'status': 'active', 'phone': '79080729539', 'hasAppointment': True, 'appointmentDuration': 20, 'note': 'Место работы: МБУЗ "ОБластная больница г. Троицк", должность: зав.  невролог. отделением.\r\n До 3 лет не смотрит. ', 'currentClinicId': 1, 'clinicIds': [1], 'onlineRecordingInformation': None, 'availabilityForOnlineRecording': 'not_available', 'userGroups': ['medical_staff'], 'specialties': [{'id': 72, 'title': 'Невролог', 'userGroup': 'medical_staff'}], 'code': '', 'sex': None, 'avatars': None}

    # {'id': 42, 'surname': 'Серебрякова', 'name': 'Алена', 'secondName': 'Владимировна', 'email': '', 'birthdate': '1968-09-23', 'status': 'active', 'phone': '79049788284', 'hasAppointment': True, 'appointmentDuration': 30, 'note': 'Внутрисуставные введение (дипроспан и т.д., ГОР БОЛЬНИЦА №8 врач-1категории, стаж ревматолога 23 г .первичный прием 30 мин повторный 30 мин. Принимает с 18 лет! Делает внутрисуставые инъекции дипроспан и гируан (17.000 по предоплате) Мин.оплата 4500 . Трансп расходы 1200 ', 'currentClinicId': 1, 'clinicIds': [1], 'onlineRecordingInformation': None, 'availabilityForOnlineRecording': 'available', 'userGroups': ['medical_staff'], 'specialties': [{'id': 112, 'title': 'Ревматолог', 'userGroup': 'medical_staff'}], 'code': '', 'sex': 'female', 'avatars': None}

    # {'id': 59, 'surname': 'Поздеева', 'name': 'Лариса', 'secondName': 'Ивановна', 'email': '', 'birthdate': '1981-04-23', 'status': 'active', 'phone': '79030899234', 'hasAppointment': True, 'appointmentDuration': 30, 'note': 'Место работы: ЧОКБ. врач высшей категории профиль Гепатолог!Приемы по 30 мин! повтор приемы по 20. (опыт работы с 2008 г.). Детей смотрит строго с  16 лет. минималка 2500.От М-ВИДЕО забирать. На прием желательно при себе иметь результаты УЗИ (брюшная полость). Возможно дообследование в областной больнице.   ', 'currentClinicId': 1, 'clinicIds': [1], 'onlineRecordingInformation': None, 'availabilityForOnlineRecording': 'available', 'userGroups': ['medical_staff'], 'specialties': [{'id': 38, 'title': 'Гастроэнтеролог', 'userGroup': 'medical_staff'}], 'code': '', 'sex': 'female', 'avatars': None}

    # {'id': 111, 'surname': 'Назарова', 'name': 'Мария ', 'secondName': 'Валерьевна', 'email': '', 'birthdate': '1971-11-11', 'status': 'active', 'phone': '79127719154', 'hasAppointment': True, 'appointmentDuration': 30, 'note': 'минималка 5000. Детский кардиоревматолог, педиатр приемы по 30 мин, 8 детская болница \r\nС собой на прием иметь амб. карту; если ранее проводились к-либо исследования, выписки из стационара, обязательно взять с собой. от Юности\r\nНа  кардиологический осмотр с собой иметь ЭКГ. \r\nДля кардиологического приема нужны манжеты для измерения АД разного размера. минималка \r\nВЗРОСЛЫХ НЕ ПРИНИМАЕТ. ', 'currentClinicId': 1, 'clinicIds': [1], 'onlineRecordingInformation': None, 'availabilityForOnlineRecording': 'not_available', 'userGroups': ['medical_staff'], 'specialties': [{'id': 57, 'title': 'Кардиоревматолог', 'userGroup': 'medical_staff'}, {'id': 96, 'title': 'Педиатр', 'userGroup': 'medical_staff'}], 'code': '', 'sex': 'female', 'avatars': None}

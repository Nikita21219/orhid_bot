FROM python:3.8-alpine

ENV MYSQL_ROOT_PASSWORD ${MYSQL_ROOT_PASSWORD}
ENV MYSQL_USER ${MYSQL_USER}
ENV MYSQL_PASSWORD ${MYSQL_PASSWORD}
ENV MYSQL_DATABASE ${MYSQL_DATABASE}
ENV BOT_TOKEN ${BOT_TOKEN}
ENV CRM_TOKEN ${CRM_TOKEN}
ENV URL_USERS ${URL_USERS}
ENV URL_SPECIALTIES ${URL_SPECIALTIES}
ENV URL_SCHEDULES ${URL_SCHEDULES}
ENV URL_APPOINTMENTS ${URL_APPOINTMENTS}
ENV URL_CLIENTS ${URL_CLIENTS}
ENV OWNER_CHAT_ID ${OWNER_CHAT_ID}
ENV DOCTOR1 ${DOCTOR1}
ENV DOCTOR2 ${DOCTOR2}


COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN apk add --no-cache build-base; \
    pip install --upgrade pip; \
    pip install -r requirements.txt

COPY src /app

CMD ["python", "bot.py"]

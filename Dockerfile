FROM python:3.12-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y ntpdate

RUN apt-get update
RUN apt-get install -y locales nano

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache -r /app/requirements.txt

CMD tail -f /dev/null
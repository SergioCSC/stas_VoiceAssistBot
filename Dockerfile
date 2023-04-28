#FROM python:3.10-slim-bullseye
FROM python:3.10.11-alpine3.17

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt


COPY ./ /app


WORKDIR /app


CMD ["python3", "bot.py"]

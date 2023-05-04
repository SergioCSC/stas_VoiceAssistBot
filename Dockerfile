FROM python:3.10.11-alpine3.17

RUN apk add --no-cache curl

RUN pip3 install --no-cache-dir aiogram==3.0.0b6

RUN pip3 install  --no-cache-dir environs==9.5.0

COPY ./ /app

WORKDIR /app

CMD ["python3", "bot.py"]

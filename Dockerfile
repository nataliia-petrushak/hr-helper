FROM python:3.11.2-slim-buster

ENV PYTHONUNBUFFERED 1

WORKDIR app/

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Define the command to run your bot when the container starts
CMD ["python", "telegram-bot.py"]
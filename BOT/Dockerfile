FROM python:3.9

WORKDIR /app

COPY ./bot /app/bot
COPY run.py /app
COPY requirements.txt /app

RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip && pip install -r requirements.txt

CMD [ "python3", "run.py"]
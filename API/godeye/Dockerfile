FROM python:3.9.2

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

WORKDIR /app
COPY . /app

RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip && pip install -r requirements.txt
RUN --mount=type=cache,target=/var/cache/apt apt-get update -yqq && apt-get install -yqq build-essential cmake

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD psql -h 192.168.100.10 -d "facerecognition" -U "admin" -p "5432"
CMD "/entrypoint.sh"

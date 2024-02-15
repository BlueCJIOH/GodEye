FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

WORKDIR /app
COPY . /app

RUN --mount=type=cache,target=/var/cache/apt apt-get update -y && apt-get install -y build-essential cmake
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip && pip install -r requirements.txt

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD psql -h 192.168.100.10 -d "facerecognition" -U "admin" -p "5432"
CMD "/entrypoint.sh"

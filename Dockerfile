FROM python:3.11.3-alpine3.17

WORKDIR /app

COPY requirements.txt .

RUN uname -a | grep -i armv7 && apk add --no-cache rust cargo

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

RUN mkdir -p /app/data

CMD ["python", "App.py"]

VOLUME /data

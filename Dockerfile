FROM python:3.11.3-alpine3.17

WORKDIR /app

RUN apk add --no-cache rust cargo

RUN pip install --no-cache-dir bcrypt

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

RUN mkdir -p /app/data

CMD ["python", "App.py"]

VOLUME /data

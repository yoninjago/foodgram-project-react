FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["run"]
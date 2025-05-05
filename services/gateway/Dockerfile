FROM python:3.9


COPY services/gateway/requirements.txt .

COPY services/broker/kafka_producer.py .

RUN pip install -r requirements.txt

COPY services/gateway/ .

ENTRYPOINT ["python", "main.py"]

FROM python:3.9

COPY services/users/requirements.txt .

RUN pip install -r requirements.txt

COPY services/users .

COPY services/broker/kafka_producer.py .

RUN chmod +x kafka_producer.py

ENTRYPOINT ["python3", "main.py"]
FROM python:3.9

WORKDIR /tests

COPY ./services/tests/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY ./services/tests .

COPY ./services/posts ./posts

COPY ./services/statistics/statistics_pb2.py ./posts/service/proto
COPY ./services/statistics/statistics_pb2_grpc.py ./posts/service/proto

RUN pip install -r ./posts/service/server/requirements.txt

RUN chmod +x ./wait-for-it.sh

ENTRYPOINT ["./wait-for-it.sh", "gateway_api:5000", "--","pytest", "-vs", "--log-level=INFO", "-W", "ignore::DeprecationWarning"]
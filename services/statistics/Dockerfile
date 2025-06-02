FROM python:3.9-slim

WORKDIR /statistics

COPY ./services/statistics/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./services/statistics .

RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    statistics.proto

CMD ["python", "main.py"]


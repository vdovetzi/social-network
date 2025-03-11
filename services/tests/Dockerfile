FROM python:3.9

WORKDIR /tests

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x ./wait-for-it.sh

ENTRYPOINT ["./wait-for-it.sh", "gateway_api:5000", "--","pytest", "-vs", "--log-level=INFO", "-W", "ignore::DeprecationWarning"]
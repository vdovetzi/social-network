FROM python:3.9

WORKDIR /posts

COPY ./server/requirements.txt .
RUN cat requirements.txt
RUN pip install -r requirements.txt

RUN apt update && apt install -y postgresql postgresql-contrib

RUN mkdir service
COPY ./__init__.py service/__init__.py
COPY ./server/ service/server/
COPY ./proto/ service/proto/

EXPOSE 8091

ENTRYPOINT ["python", "-m", "service.server.server"]
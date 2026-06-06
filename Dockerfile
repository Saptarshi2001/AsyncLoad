FROM python:3.12-alpine
WORKDIR /AsyncLoad
COPY . .
RUN pip install -e .
ENTRYPOINT ["asyncload"]

FROM python:3.9-alpine

MAINTAINER Klzy klzy@vlabpro.com

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

COPY . .

CMD [ "python", "./app.py" ]
FROM python:3.8
COPY requirements.txt /sandbox/

WORKDIR /sandbox

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY main.py /sandbox
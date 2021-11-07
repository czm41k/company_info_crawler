FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY code/ .

ENTRYPOINT [ "python3", "script.py" ]
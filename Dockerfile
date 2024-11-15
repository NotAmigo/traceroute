FROM python:3.11-slim

EXPOSE 8000

WORKDIR /traceroute

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
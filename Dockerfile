FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "main.py"]

FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN mkdir -p /root/.u2net
COPY .u2net/u2net.onnx /root/.u2net/u2net.onnx  # SALIN FILE SETELAH DIR KERJA

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Debug tambahan (opsional):
RUN ls -lh /root/.u2net

CMD ["python", "main.py"]

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY exporter.py .
ENV METRICS_FILE=/.repo/.metrics
ENV WINDOWS=5m,1h,24h
ENV EXPORTER_PORT=9108
# Montaremos o repo em /.repo via docker-compose
EXPOSE 9108
CMD ["python","/app/exporter.py"]

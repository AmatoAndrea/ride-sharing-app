FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

ENV FLASK_APP=app.main
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5002

CMD ["flask", "run"]
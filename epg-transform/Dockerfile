FROM python:3.11-slim

ARG INPUT
ARG OUTPUT

RUN apt-get update && \
    apt-get install -y jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python3", "app.py", "${INPUT}", "${OUTPUT}"]
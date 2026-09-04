FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps \
		gcc \
		musl-dev \
		linux-headers \
	&& pip install --no-cache-dir -r requirements.txt \
	&& apk del .build-deps

COPY app/ ./app/



CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.12-alpine AS build

RUN apk update && apk add --no-cache gcc musl-dev postgresql-dev libffi-dev

WORKDIR /install

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install/root -r requirements.txt

FROM python:3.12-alpine

RUN apk add --no-cache libpq

WORKDIR /app

COPY --from=build /install/root /usr/local

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# syntax=docker/dockerfile:1.7
FROM python:3.12.3-slim-bookworm

WORKDIR /code

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["python3"]
CMD ["app.py"]
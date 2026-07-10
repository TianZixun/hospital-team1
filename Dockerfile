FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5055
ENV HOSPITAL_TEAM1_HOST=0.0.0.0

COPY pyproject.toml README.md ./
COPY hospital_team1 ./hospital_team1
COPY datasets ./datasets
COPY docs ./docs
COPY scripts ./scripts
COPY slides ./slides
COPY tests ./tests
COPY main.py test.py serve.py wsgi.py ./
COPY results ./results
COPY require.rtf require.rtf

RUN pip install --no-cache-dir .

EXPOSE 5055

CMD ["python", "serve.py"]

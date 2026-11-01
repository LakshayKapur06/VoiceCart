FROM python:3.12.14-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/voicecart
COPY pyproject.toml README.md ./
COPY voicecart ./voicecart
RUN pip install --no-cache-dir . && useradd --uid 10001 --create-home voicecart
USER voicecart
EXPOSE 8080
CMD ["python", "-m", "voicecart.server", "--host", "0.0.0.0"]

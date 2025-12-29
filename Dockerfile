FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY tests/ tests/
COPY README.md .

ENV PYTHONPATH=/app

# Default command runs the adversarial test
CMD ["python3", "-m", "unittest", "tests/test_adversarial.py"]

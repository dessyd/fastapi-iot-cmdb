FROM python:3.10-slim-bookworm
WORKDIR /usr/src/app

# Upgrade system packages to address vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get clean

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Put this COPY last to avoid re running pip at change source code change
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

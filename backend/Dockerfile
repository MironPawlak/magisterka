FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app
RUN apt-get update && \
apt-get install --no-install-recommends -y \
libpq-dev build-essential postgresql-client \
&& apt-get clean && rm -rf /var/lib/apt/lists/* 
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
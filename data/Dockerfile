# Dockerfile
FROM postgres:15

# Install unzip
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# Environment variables will be supplied via docker-compose
ENV POSTGRES_DB=mydb
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Copy zip files and scripts
COPY ./raw/*.zip /raw/
COPY ./init.sql /docker-entrypoint-initdb.d/1-init.sql
COPY ./unzip_and_load.sh /docker-entrypoint-initdb.d/2-unzip_and_load.sh
COPY ./load_data.sql /docker-entrypoint-initdb.d/3-load_data.sql

# Make the shell script executable
RUN chmod +x /docker-entrypoint-initdb.d/2-unzip_and_load.sh
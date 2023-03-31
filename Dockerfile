# Base image
FROM python:3.9-slim-buster

# Set the working directory
RUN mkdir /app
WORKDIR /app

# Dependencies
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y mariadb-server mariadb-client libmariadb-dev-compat

# Initialize MariaDB server and start service
RUN service mysql start

# Copy the requirements.txt file and install dependencies
COPY ./requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt \
    && pip install gunicorn \
    && rm -rf /root/.cache

# Copy the rest of the application code
COPY . .

# Expose port 80
EXPOSE 80

# Start the application
CMD [ "bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:80" ]
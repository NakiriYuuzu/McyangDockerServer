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

RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run database migrations
RUN . venv/bin/activate && \
    python manage.py migrate

# Expose port 80
EXPOSE 80

# Start the application
CMD [ "bash", "-c", "source venv/bin/activate && python manage.py runserver 0.0.0.0:80" ]
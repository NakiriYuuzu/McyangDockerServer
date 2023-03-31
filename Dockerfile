# Base image
FROM python:3.9-slim-buster

# Set the working directory
RUN mkdir /app
WORKDIR /app

# dependencies

# Copy the requirements.txt file and install dependencies
COPY ./requirements.txt .
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 80
EXPOSE 80

# Start the application
CMD [ "bash", "-c", "source venv/bin/activate && python manage.py runserver 0.0.0.0:80" ]

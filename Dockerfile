# Use the official Python image from the Docker Hub
FROM python:3.10

# Set environment variables for non-interactive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install required locales and set the default locale
RUN apt-get update && apt-get install -y locales && \
    echo "es_ES.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen es_ES.UTF-8

# Set environment variables for locale settings
ENV LANG=es_ES.UTF-8
ENV LANGUAGE=es_ES:es
ENV LC_ALL=es_ES.UTF-8

# Copy the requirements file
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application code to the container
COPY . ./

# Expose port 8080
EXPOSE 8080

# Run the application using Gunicorn
CMD gunicorn -b 0.0.0.0:8080 app:server -w 4

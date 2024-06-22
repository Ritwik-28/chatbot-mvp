# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Rasa
RUN pip install rasa

# Install Weights & Biases
RUN pip install wandb

# Install Scrapy for website scraping
RUN pip install scrapy

# Install Elasticsearch client
RUN pip install elasticsearch

# Install Docker client and curl
RUN apt-get update && apt-get install -y docker.io curl

# Install Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Make port 5005 available to the world outside this container
EXPOSE 5005

# Define environment variable
ENV NAME World

# Run Rasa server
CMD ["rasa", "run", "--enable-api", "--cors", "*"]
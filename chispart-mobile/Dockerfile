# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js and npm
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package.json and package-lock.json files
COPY package.json ./
COPY package-lock.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the application's code
COPY . .

# The command to run the application will be specified in the docker-compose.yml file

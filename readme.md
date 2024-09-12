# Dash App Setup and Deployment

This document provides instructions to run a Dash app using both Docker and directly on a CentOS server.

## Prerequisites

Before you start, make sure you have the following installed:

- For Docker setup:
  - [Docker](https://docs.docker.com/get-docker/)

- For CentOS setup:
  - CentOS 7 or 8
  - Python 3.10
  - Pip (Python package installer)
  - Git

## Option 1: Running the App with Docker

### Step 1: Clone the Repository

First, clone the repository that contains your Dash app.

```bash
git clone <repository_url>
cd <repository_folder>
```

### Step 2: Create a .env File
Create a .env file in the root directory of your project and add your environment variables.

```dosini
# .env
DEVURL=<your_dev_url>
EMAIL=<your_email>
PASSWORD=<your_password>
```

Replace the placeholders with your actual environment variable values.

### Step 3: Build the Docker Image
To build the Docker image, run the following command in the root directory of your project (where the Dockerfile is located):

```bash
docker build -t dash_app .
```

- -t dash_app: Tags the image with the name dash_app.
- .: Refers to the current directory where the Dockerfile is located.

Step 4: Run the Docker Container
Run the Docker container using the docker run command:

```bash
docker run -p 8080:8080 dash_app
```

- -p 8080:8080: Maps port 8080 of the container to port 8080 on your host machine.
- dash_app: The name of the Docker image built in Step 3.

#### Optional: Run with Multiple Workers
If you want to run the app with multiple Gunicorn workers for better performance, you can specify the number of workers:

```bash
docker run -p 8080:8080 dash_app gunicorn -b 0.0.0.0:8080 app:server -w 4
```

Replace 4 with the desired number of workers.

### Step 5: Access the App
Open your web browser and navigate to http://localhost:8080. You should see your Dash app running.

#### Troubleshooting
Error: unsupported locale setting
1.Make sure your Dockerfile has the following commands to install the necessary locales:

```
RUN apt-get update && apt-get install -y locales && \
    locale-gen es_ES.UTF-8 && \
    update-locale LANG=es_ES.UTF-8
```

2. Issue with Dependencies
If you run into dependency issues, check your requirements.txt file to ensure all necessary packages are listed.

3. Port Already in Use
If port 8080 is already in use, you can map to a different port by modifying the -p option in the docker run command, e.g., -p 9090:8080.

### Step 6: Stop the Docker Container
To stop the running Docker container, press Ctrl + C in the terminal where the container is running. Alternatively, you can use the docker stop command:

```bash
docker ps  # Find the container ID
docker stop <container_id>
```

## Option 2: Running the App Directly on a CentOS Server
### Step 1: Install Required Packages
First, ensure that your CentOS server is up to date and has Python 3.10, pip, and Git installed.

1. Update the system:

```bash
sudo yum update -y
```

2. Install Python 3.10 and pip:

CentOS 7:

```bash
sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel
sudo yum groupinstall -y "Development Tools"
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz
sudo tar xzf Python-3.10.0.tgz
cd Python-3.10.0
sudo ./configure --enable-optimizations
sudo make altinstall
```

CentOS 8:

```bash
sudo dnf install -y python3.10
```

Install Git:

```bash
sudo yum install -y git
```

Install virtualenv:

```bash
sudo pip3 install virtualenv
```

### Step 2: Clone the Repository
Clone your repository from GitHub (or any other Git service):

```bash
git clone <repository_url>
cd <repository_folder>
```

Replace <repository_url> with your repository URL.

### Step 3: Set Up a Python Virtual Environment
Create and activate a Python virtual environment:

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### Step 4: Install Python Dependencies
Install the required Python packages from requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 5: Create a .env File
Create a .env file in the root directory of your project and add your environment variables.

```plaintext
# .env
DEVURL=<your_dev_url>
EMAIL=<your_email>
PASSWORD=<your_password>
```

Replace the placeholders with your actual environment variable values.

### Step 6: Run the App with Gunicorn
Run the app using Gunicorn:

```bash
gunicorn -b 0.0.0.0:8080 app:server
```

- -b 0.0.0.0:8080: Binds the app to 0.0.0.0 on port 8080.
- app:server: Points to the server object in your Dash app.

#### Optional: Run with Multiple Workers
To improve performance, run Gunicorn with multiple workers:

The general rule of thumb for determining the number of workers is:

Number of Workers=(2×Number of CPU Cores)+1
This formula provides a good balance between concurrency and efficient CPU usage.

```bash
gunicorn -b 0.0.0.0:8080 app:server -w 4
```

Replace 4 with the desired number of workers.

### Step 7: Access the App
Open your web browser and navigate to http://<your-server-ip>:8080. You should see your Dash app running.
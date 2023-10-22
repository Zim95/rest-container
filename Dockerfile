FROM python:3.11-slim

## setup docker section

# Install necessary packages
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
# Install Docker
RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh

## setup python section

# setup work directory
RUN mkdir app
COPY . app/
WORKDIR /app
# install dependencies
RUN apt-get update && apt-get install -y build-essential
RUN pip install -r requirements.txt

# run code
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app", "--reload"]
FROM python:3.11-slim

RUN mkdir app
COPY . app/
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential
RUN pip install -r requirements.txt

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app", "--reload"]
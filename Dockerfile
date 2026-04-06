
FROM python:3.14

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# Install unixODBC and other necessary dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    unixodbc \
    unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 5000

CMD ["fastapi", "run", "app/main.py", "--port", "80", "--reload"]
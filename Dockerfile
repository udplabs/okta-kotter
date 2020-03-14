FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN apk add --no-cache gcc
RUN apk add --no-cache \
        libressl-dev \
        musl-dev \
        libffi-dev && \
    pip install cryptography==2.8 && \
    apk del \
        libressl-dev \
        musl-dev \
        libffi-dev
RUN pip install -r requirements.txt
EXPOSE 5000
CMD flask run -h 0.0.0.0

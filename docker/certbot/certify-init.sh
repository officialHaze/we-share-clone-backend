#!/bin/sh

set -e

# wait for the proxy to be available then get the first certificate
until nc -z proxy 80; do
    echo "waiting for proxy"
    sleep 5s & wait ${!}
done

# get the certificate
certbot certonly \
    --webroot \
    --webroot-path "/vol/www/" \
    -d "${DOMAIN}" \
    --email $EMAIL \
    --rsa-key-size 4096 \
    --agree-tos \
    --noninteractive
    
upstream backend {
    ip_hash;

    server ${APP_HOST}:${APP_PORT} max_fails=3 fail_timeout=10s;
}

server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}
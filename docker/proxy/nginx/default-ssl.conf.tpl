upstream backend {
    server https://${DOMAIN};

    sticky cookie srv_id expires=1h domain=${DOMAIN} path=/;
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

server {
    listen 443 ssl;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate             /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key         /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    include /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max_age=31536000; includeSubDomains" always;

    location /static {
        alias /vol/static;
    }

    location / {
        proxy_pass                  http://backend;
        include                     /etc/nginx/uwsgi_params;
        client_max_body_size        50M;
    }


}
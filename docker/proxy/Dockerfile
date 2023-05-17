FROM nginx:1.23.0-alpine

COPY ./nginx/* /etc/nginx/
COPY ./run.sh /run.sh

ENV APP_HOST=app
ENV APP_PORT=8080

RUN apk add --no-cache openssl bash
RUN mkdir -p /vol/static && \
    chmod 755 /vol && \
    chmod +x /run.sh

VOLUME /vol/static
VOLUME /vol/www

CMD [ "/run.sh" ]

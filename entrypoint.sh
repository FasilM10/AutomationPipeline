#!/bin/bash
set -e
# Get the maximum upload file size for Nginx, default to 0: unlimited
USE_NGINX_MAX_UPLOAD=${NGINX_MAX_UPLOAD:-0}
# Generate Nginx config for maximum upload file size
echo "client_max_body_size $USE_NGINX_MAX_UPLOAD;" > /etc/nginx/conf.d/upload.conf

# Get the listen port for Nginx, default to 80
USE_LISTEN_PORT=${LISTEN_PORT:-80}
if ! grep -q "listen ${USE_LISTEN_PORT};" /etc/nginx/conf.d/nginx.conf ; then
    sed -i -e "/server {/a\    listen ${USE_LISTEN_PORT};" /etc/nginx/conf.d/nginx.conf
fi

# Get the URL for static files from the environment variable
USE_STATIC_URL=${STATIC_URL:-'/static'}
# Get the absolute path of the static files from the environment variable
USE_STATIC_PATH=${STATIC_PATH:-'/app/static'}

# Generate Nginx config first part using the environment variables
echo 'server {
    proxy_connect_timeout 360s;
    proxy_send_timeout 360s;
    proxy_read_timeout 360s;
    send_timeout 360s;
    uwsgi_read_timeout 600s;
    uwsgi_send_timeout 600s;
    client_body_timeout 600s ;
    location / {
        try_files $uri @app;
        proxy_connect_timeout 360s;
        proxy_send_timeout 360s;
        proxy_read_timeout 360s;
        send_timeout 360s;
        uwsgi_read_timeout 600s;
        uwsgi_send_timeout 600s;
        client_body_timeout 600s ;
    }
    location @app {
        include uwsgi_params;
        uwsgi_pass unix:///tmp/uwsgi.sock;
        uwsgi_read_timeout 600s;
        uwsgi_send_timeout 600s;
        
    }
    '"location $USE_STATIC_URL {
        alias $USE_STATIC_PATH;
        uwsgi_read_timeout 600s;
        uwsgi_send_timeout 600s;
        
    }" > /etc/nginx/conf.d/nginx.conf

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
if [[ $STATIC_INDEX == 1 ]] ; then
echo "    location = / {
        index $USE_STATIC_URL/index.html;
    }" >> /etc/nginx/conf.d/nginx.conf
fi
# Finish the Nginx config file
echo "}" >> /etc/nginx/conf.d/nginx.conf

exec "$@"
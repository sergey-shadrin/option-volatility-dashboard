FROM nginx:1.25.5-bookworm

RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf

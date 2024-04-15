FROM nginx:1.22.1
COPY nginx.conf /etc/nginx/templates/default.conf.template
# COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY result_build /usr/share/nginx/html/frontend
COPY docs /usr/share/nginx/html/api/docs

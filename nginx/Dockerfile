FROM nginx:alpine

# Копирование конфигурации
COPY nginx.conf /etc/nginx/nginx.conf

# Порт для nginx
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]


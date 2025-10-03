# syntax=docker/dockerfile:1
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . ./

EXPOSE 3000
ENV HOST=0.0.0.0 \
    PORT=3000 \
    CHOKIDAR_USEPOLLING=true

CMD ["npm", "start"]

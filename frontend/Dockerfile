# Dev Dockerfile, będzie trzeba wyłączyć hot reload
FROM node:23-alpine

WORKDIR /app

COPY frontendApps/package*.json ./
RUN npm install

COPY frontendApps/ .

EXPOSE 5173

CMD ["npm", "run", "host"]

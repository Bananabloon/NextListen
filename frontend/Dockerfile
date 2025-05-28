# Dev Dockerfile, będzie trzeba wyłączyć hot reload
FROM node:23-alpine

WORKDIR /app

COPY webApp/package*.json ./
RUN npm install

COPY webApp/ .

EXPOSE 5173

CMD ["npm", "run", "host"]

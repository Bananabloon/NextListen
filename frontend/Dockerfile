# development
FROM node:22-alpine

WORKDIR /app

COPY ./webApp/package.json ./webApp/package-lock.json  ./

RUN npm i

COPY ./webApp ./

EXPOSE 5173

CMD [ "npm", "run", "host" ]

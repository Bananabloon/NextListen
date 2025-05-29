# production
FROM node:22-alpine

WORKDIR /app

COPY ./webApp/package.json ./webApp/package-lock.json  ./

RUN npm i
RUN npm i -g serve

COPY --exclude=./webApp/package.json ./webApp /app

RUN npm run build

EXPOSE 5173

CMD [ "serve", "-l", "5173", "-s", "dist" ]

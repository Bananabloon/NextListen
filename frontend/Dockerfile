# Etap 1: Build Vite
FROM node:18-alpine AS build

WORKDIR /app

# Skopiuj zależności i zainstaluj
COPY frontendApps/package*.json ./
RUN npm install


COPY frontendApps/ .

RUN npm run build

FROM node:18-alpine

WORKDIR /app


RUN npm install -g serve


COPY --from=build /app/dist .


EXPOSE 5173

# Uruchamiamy serwer
CMD ["serve", "-s", ".", "-l", "5173"]
FROM node:22-alpine

WORKDIR /app

COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web .

RUN npm run build

EXPOSE 3000

CMD ["sh", "-c", "npx next start -p ${PORT:-3000}"]

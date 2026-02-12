
FROM node:20.19.6-alpine

WORKDIR /app

COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* /app/


RUN npm install --legacy-peer-deps


COPY . /app


RUN npm run build || true
EXPOSE 3000
CMD ["npm", "run", "start:prod"]



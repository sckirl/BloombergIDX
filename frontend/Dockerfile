FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

EXPOSE 8080

CMD ["sh", "-c", "npx next start -H 0.0.0.0 -p ${PORT:-8080}"]

FROM node:22-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY server.js .
COPY index.html .
COPY fitness-data.json .
COPY spin-demo.html .
EXPOSE 3001
CMD ["node", "server.js"]

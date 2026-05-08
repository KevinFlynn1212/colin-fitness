FROM node:22-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY server.js .
COPY index.html .
COPY fitness-data.json .
COPY spin-demo.html .
COPY manifest.json .
COPY icon.svg .
EXPOSE 3001
CMD ["node", "server.js"]

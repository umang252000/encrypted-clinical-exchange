FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --legacy-peer-deps
COPY src ./src
RUN mkdir -p /app/public && echo "<div id='root'></div>" > /app/public/index.html
EXPOSE 3000
CMD ["npm","start"]
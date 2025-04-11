FROM node:slim

WORKDIR /app

COPY .npmrc ./
COPY package*.json ./
RUN npm install

COPY . ./
RUN npm run build

CMD ["cp", "-r", "build", "result_build"]

FROM node:lts-alpine
EXPOSE 5001
WORKDIR /app
COPY ./frontend .
RUN npm install
RUN npm run build
CMD ["npm", "run", "serve"]

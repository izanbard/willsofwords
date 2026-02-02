FROM node:lts-alpine
EXPOSE 5001
WORKDIR /app
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-localhost:5000}
COPY ./frontend .
RUN npm install
RUN npm run build
CMD ["npm", "run", "serve"]

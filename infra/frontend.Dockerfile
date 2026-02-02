FROM node:lts-alpine AS build
WORKDIR /app
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-localhost:5000}
COPY ./frontend/package.json .
RUN npm install
COPY ./frontend .
RUN npm run build

FROM node:lts-alpine AS serve
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-localhost:5000}
EXPOSE 5001
WORKDIR /app
RUN npm install -g http-server
COPY --from=build /app/dist /app/public
CMD ["http-server", "/app/public", "-p", "5001", "--cors","--proxy", "http://${VITE_API_BASE_URL}?"]

FROM node:lts-alpine AS build
EXPOSE 5001
WORKDIR /app
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-localhost:5000}
COPY ./frontend/package.json .
RUN npm install
COPY ./frontend .
RUN npm run build

FROM node:lts-alpine AS serve
WORKDIR /app
RUN npm install -g http-server
COPY --from=build /app/dist /app/public
CMD ["http-server", "public", "-p", "5001", "--cors"]

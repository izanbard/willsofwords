#!/bin/bash
echo "Specify your image tag"
read -r tag
docker login

docker build -f infra/backend.Dockerfile --tag=gordywills/wordsworth:"$tag" ./
docker build -f infra/frontend.Dockerfile --tag=gordywills/dorothy:"$tag" ./

docker push gordywills/wordsworth:"$tag"
docker push gordywills/dorothy:"$tag"
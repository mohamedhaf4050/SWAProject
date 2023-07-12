docker plugin install grafana/loki-docker-driver:latest --alias loki --grant-all-permissions



docker compose -f "docker-compose.yml" up -d --build


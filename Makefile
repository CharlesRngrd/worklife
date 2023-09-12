.ONESHELL:

CONTAINER_EXECUTOR = docker exec -w /wl/app worklife-test-api

# Deployment
.PHONY: up
up:
	docker compose -f ./docker-compose.yml up -d

.PHONY: down
down:
	docker compose -f ./docker-compose.yml down -v

.PHONY: build
build:
	docker compose -f docker-compose.yml build

.PHONY: tests
tests:
	docker compose -f docker-compose.yml run worklife-test-api pytest --cov=app app/tests/ -v

# DB
.PHONY: create-db
create-db:
	docker exec worklife-test-db psql -U dev -d postgres -f /scripts/create_db.sql -v db="dev"

.PHONY: drop-db
drop-db:
	docker exec worklife-test-db psql -U dev -d postgres -f /scripts/drop_db.sql -v db="dev"

.PHONY: downgrade-db
downgrade-db:
	$(CONTAINER_EXECUTOR) alembic downgrade -1

.PHONY: migrate-db
migrate-db:
	$(CONTAINER_EXECUTOR) alembic upgrade head

.PHONY: autogenerate-migration
autogenerate-migration:
	$(CONTAINER_EXECUTOR) alembic revision --autogenerate -m $(revision_message)

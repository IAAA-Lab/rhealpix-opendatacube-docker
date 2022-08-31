## You can follow the steps below in order to get yourself a local ODC.
## Start by running `setup` then you should have a system that is fully configured
##
## Once running, you can access a Jupyter environment
## at 'http://localhost' with password 'secretpassword'
.PHONY: help setup up down clean

# For now only a part of Europe, as the index fails sometimes with a larger bbox
BBOX := -10,36,4,44

help: ## Print this help
	@grep -E '^##.*$$' $(MAKEFILE_LIST) | cut -c'4-'
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-10s\033[0m %s\n", $$1, $$2}'

setup: build up init ## Run a full local/development setup
# setup-prod: up-prod init product index ## Run a full production setup

up: ## 1. Bring up your Docker environment
	docker-compose up -d postgres
	docker-compose run checkdb
	docker-compose up -d jupyter

init: ## 2. Prepare the database
	docker-compose exec -T jupyter conda run -n odc_env datacube -v system init

# index: ## 4. Index some data (Change extents with BBOX='<left>,<bottom>,<right>,<top>')	
# 	docker-compose exec -T jupyter conda run -n odc_env bash -c \
# 		"stac-to-dc \
# 			--catalog-href='https://planetarycomputer.microsoft.com/api/stac/v1/' \
# 			--collections='nasadem' \
# 			--bbox='$(BBOX)'"
# 	docker-compose exec -T jupyter conda run -n odc_env bash -c \
# 		"stac-to-dc \
# 			--bbox='$(BBOX)' \
# 			--catalog-href='https://earth-search.aws.element84.com/v0/' \
# 			--collections='sentinel-s2-l2a-cogs' \
# 			--datetime='2021-06-01/2021-07-01'"
# 	docker-compose exec -T jupyter conda run -n odc_env bash -c \
# 		"stac-to-dc \
# 			--catalog-href=https://planetarycomputer.microsoft.com/api/stac/v1/ \
# 			--collections='io-lulc'"

down: ## Bring down the system
	docker-compose down

build: ## Rebuild the base image
	docker-compose pull
	docker-compose build

shell: ## Start an interactive shell
	docker-compose exec jupyter bash

clean: ## Delete everything
	docker-compose down --rmi all -v

logs: ## Show the logs from the stack
	docker-compose logs --follow

# build-image:
# 	docker build --tag opendatacube/cube-in-a-box .
# 
# push-image:
# 	docker push opendatacube/cube-in-a-box

# up-prod: ## Bring up production version
# 	docker-compose -f docker-compose-prod.yml pull
# 	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --detach postgres
# 	docker-compose run checkdb
# 	docker-compose -f docker-compose.yml -f docker-compose-prod.yml up --detach --no-build

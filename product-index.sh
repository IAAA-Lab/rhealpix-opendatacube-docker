#!/bin/bash

mkdir -p data_repo

# Data was 7-zipped with `7z a -v49m "data_repo.7z" data_repo/` as GitHub does not recommend files larger 
# than 50m (and won't accept files larger than 100m)

# Uncompress data (it will create the .data_repo directory which is mapped to /home in the Docker container
7z -y x ./data_compressed/data_repo.7z.001

make down
# # This will ask for your sudo password
sudo rm -r ./data/pg
make up
make init

# Load data into datacube
docker-compose exec jupyter conda run -n odc_env datacube product add /home/Aragón-RHEALPIX/Aragón-RHEALPIX.yaml
docker-compose exec jupyter conda run -n odc_env datacube product add /home/C_GLS_SCE500/c_gls_sce500_product.yaml
docker-compose exec jupyter conda run -n odc_env datacube product add /home/C_GLS_SCE500-RHEALPIX/c_gls_sce500_product-RHEALPIX.yaml
docker-compose exec jupyter conda run -n odc_env datacube product add /home/NasaDEM/nasadem_product.yaml
docker-compose exec jupyter conda run -n odc_env datacube product add /home/NasaDEM-RHEALPIX/nasadem_product-RHEALPIX.yaml

docker-compose exec jupyter conda run -n odc_env datacube dataset add /home/Aragón-RHEALPIX/Aragón-RHEALPIX_res9.yaml
docker-compose exec jupyter conda run -n odc_env datacube dataset add /home/C_GLS_SCE500/c_gls_sce500_dataset_202204260000_CEURO_MODIS_V1.0.1.yaml
docker-compose exec jupyter conda run -n odc_env datacube dataset add /home/C_GLS_SCE500-RHEALPIX/c_gls_sce500_dataset_202204260000_CEURO_MODIS_V1.0.1-RHEALPIX.yaml
docker-compose exec jupyter conda run -n odc_env datacube dataset add /home/NasaDEM/nasadem_dataset.yaml
docker-compose exec jupyter conda run -n odc_env datacube dataset add /home/NasaDEM-RHEALPIX/nasadem_dataset-RHEALPIX.yaml

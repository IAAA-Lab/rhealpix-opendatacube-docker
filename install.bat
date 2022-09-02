docker-compose pull
docker-compose build
docker-compose up -d postgres
docker-compose up -d jupyter
docker-compose exec -T jupyter conda run -n odc_env datacube -v system init

"C:\Program Files\7-Zip"\7z x data_compressed/data_repo.7z.001 o data_repo

chcp 65001

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


pause

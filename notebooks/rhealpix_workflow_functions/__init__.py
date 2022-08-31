import geopandas as gpd
import numpy as np
import rasterio.features
import scipy.stats
import shapely

from datacube.utils import geometry, masking


# ###########################
# Functions for the common workflow
# ###########################
        
        
def load_datasets(dc, study_area_lat, study_area_lon, common_crs, common_resolution):
    """
    Load nasadem and snow cover 500 datasets from the datacube, extracting a bounding box
    delimited by study_area_lat and study_area_lon, reprojecting to common_crs and
    resampling to common_resolution.
    """
    product = "nasadem_partial"
    time = "2000-02-20"
    measurements = ["elevation"]
    nasadem_ds = dc.load(product=product,             
                     latitude=study_area_lat, longitude=study_area_lon,                    
                     time = time,
                     output_crs = common_crs,
                     resolution = common_resolution,
                     resampling='nearest',
                     measurements = measurements                     
                    )
        
    product = "c_gls_sce500"
    time = "2022-04-26"
    measurements = ["snow_cover_value"]
    sce500_ds = dc.load(product=product,                    
                    time = time,                    
                    measurements = measurements,
                    latitude=study_area_lat, longitude=study_area_lon,                    
                    output_crs = common_crs,
                    resolution = common_resolution,
                    resampling='nearest'
                   )

    return nasadem_ds, sce500_ds

def load_Aragón_geometry(dc, path, common_crs, out_shape, transform):
    """
    Load a vector polygon to exactly define the area of interest
    We are interested just in the Pyrenees that belong to Aragón.
    This polygon is already in EPSG:25830, in a local shapefile.
    """
    polygon_to_drill = gpd.read_file(path, encoding='utf-8')
    geom = geometry.Geometry(geom=polygon_to_drill.iloc[0].geometry, crs=polygon_to_drill.crs).to_crs(common_crs)

    # Create a mask by drilling the vector geometry of Aragón
    # Open Data Cube xr_rasterize function is not readily available in cube-in-a-box. 
    # This also works but generates
    # an np.array (that we will process later to make it a DataArray to use at a mask)
    polygon_mask_array = rasterio.features.geometry_mask([geom],
                                      out_shape=out_shape,
                                      transform=transform,
                                      invert=True)
    return polygon_mask_array

def dem_processing(dc, nasadem_ds, polygon_mask_array):
    without_nodata = masking.valid_data_mask(nasadem_ds)
    polygon_mask = nasadem_ds.copy(data={"elevation":[polygon_mask_array]}, deep=True)

    # Remove nodata
    nasadem_ds_WholeArea = nasadem_ds.where(without_nodata)
    # Clip (drill) with Aragón
    nasadem_ds_Aragón = nasadem_ds_WholeArea.where(polygon_mask)
    return nasadem_ds_WholeArea, nasadem_ds_Aragón

def sce_processing(dc, sce500_ds, polygon_mask_array):
    # Create masks for invalida data (nodata + flags)
    # To print the flags for the dataset, uncomment this:
    # print(sce500_ds.snow_cover_value.attrs["flags_definition"])
    invalid_data_mask = (
        masking.make_mask(sce500_ds.snow_cover_value, data='outside area of interest') |
        masking.make_mask(sce500_ds.snow_cover_value, data='sea mask') |
        masking.make_mask(sce500_ds.snow_cover_value, data='lake mask') |
        masking.make_mask(sce500_ds.snow_cover_value, data='river mask') |
        masking.make_mask(sce500_ds.snow_cover_value, data='cloud mask') |
        masking.make_mask(sce500_ds.snow_cover_value, data='polar night') |
        masking.make_mask(sce500_ds.snow_cover_value, data='input data error')
    )

    polygon_mask = sce500_ds.copy(data={"snow_cover_value":[polygon_mask_array]}, deep=True)

    # Apply masks to the dataset; with and without the Aragón region mask   
    without_nodata = masking.valid_data_mask(sce500_ds)
    sce500_ds_WholeArea = sce500_ds.where(without_nodata).where(~invalid_data_mask)
    sce500_ds_Aragón = sce500_ds_WholeArea.where(polygon_mask)

    # Subtract 100 so we have values in [0,100] (they have an offset of +100 in the original dataset)
    sce500_ds_WholeArea = sce500_ds_WholeArea - 100
    sce500_ds_Aragón = sce500_ds_Aragón - 100
    
    return sce500_ds_WholeArea, sce500_ds_Aragón

def get_result_datasets(sce500_ds_WholeArea, sce500_ds_Aragón, nasadem_ds_WholeArea, nasadem_ds_Aragón, study_area_min_altitude):
    """
    Select cells from sce500 where height in the DEM is above the min height established for this study
    """
    sce500_Pyrenees = sce500_ds_WholeArea.where(nasadem_ds_WholeArea[dict(time=0)].elevation >= study_area_min_altitude)
    sce500_AragónPyrenees = sce500_ds_Aragón.where(nasadem_ds_Aragón[dict(time=0)].elevation >= study_area_min_altitude)
    return sce500_Pyrenees, sce500_AragónPyrenees

def get_area_result_datasets(ds_Pyrenees, ds_AragónPyrenees, percentage):       
    return ds_Pyrenees.where(ds_Pyrenees.snow_cover_value >= percentage), ds_AragónPyrenees.where(ds_AragónPyrenees.snow_cover_value >= percentage),

# ###########################
# Now the rHEALPix functions
# ###########################

def load_datasets_rhealpix(dc, study_area_lat, study_area_lon, forced_align):
    """
    Load nasadem and snow cover 500 datasets from the rhealpix versions in the datacube, extracting a 
    bounding box delimited by study_area_lat and study_area_lon. No reprojection or resampling are
    needed, as we choose the pre-calculated DGGS resolution/resampling strategy that fits the needs
    of this study.
    """
    product = "nasadem_partial_RHEALPIX"
    time = "2000-02-20"
    measurements = ["elevation"]

    nasadem_rhealpix_ds = dc.load(product=product,             
                                  time = time,
                                  latitude=study_area_lat, longitude=study_area_lon,
                                  measurements = measurements,
                                  align=forced_align)
    
    product = "c_gls_sce500_RHEALPIX"
    time = "2022-04-26"
    measurements = ["snow_cover_value"]
    
    sce500_rhealpix_ds = dc.load(product=product,
                                 latitude=study_area_lat, longitude=study_area_lon,
                                 time = time,
                                 measurements = measurements,
                                 align=forced_align)
    
    product = "Aragon_RHEALPIX"
    time = "2022-04-26"
    measurements = ["data"]

    # The geometry is already available as a rhealpix dataset
    Aragón_rhealpix_mask_ds = dc.load(product=product,                                  
                                      latitude=study_area_lat, longitude=study_area_lon,
                                      time = time,                                        
                                      measurements = measurements,
                                      align=forced_align)

    return nasadem_rhealpix_ds, sce500_rhealpix_ds, Aragón_rhealpix_mask_ds
    
def dem_rhealpix_processing(dc, nasadem_rhealpix_ds, Aragón_rhealpix_mask):
    without_nodata = masking.valid_data_mask(nasadem_rhealpix_ds)
    nasadem_rhealpix_ds_WholeArea = nasadem_rhealpix_ds.where(without_nodata)
    nasadem_rhealpix_ds_Aragón = nasadem_rhealpix_ds.where(without_nodata).where(Aragón_rhealpix_mask.data == 2)
    
    return nasadem_rhealpix_ds_WholeArea, nasadem_rhealpix_ds_Aragón

def sce_rhealpix_processing(dc, sce500_rhealpix_ds, Aragón_rhealpix_mask):
    # Create masks for invalida data (nodata + flags)
    # To print the flags for the dataset, uncomment this:
    # print(sce500_rhealpix_ds.snow_cover_value.attrs["flags_definition"])
    invalid_data_mask = (
        masking.make_mask(sce500_rhealpix_ds.snow_cover_value, data='outside area of interest') |
        masking.make_mask(sce500_rhealpix_ds.snow_cover_value, data='sea mask') |
        masking.make_mask(sce500_rhealpix_ds.snow_cover_value, data='lake mask') |
        masking.make_mask(sce500_rhealpix_ds.snow_cover_value, data='river mask') |
        masking.make_mask(sce500_rhealpix_ds.snow_cover_value, data='cloud mask') |
        masking.make_mask(sce500_rhealpix_ds.snow_cover_value, data='polar night') |
        masking.make_mask(sce500_rhealpix_ds.snow_cover_value, data='input data error')
    )

    without_nodata = masking.valid_data_mask(sce500_rhealpix_ds)

    # Apply masks to the dataset; with and without the Aragón region mask
    sce500_rhealpix_ds_WholeArea = sce500_rhealpix_ds.where(without_nodata).where(~invalid_data_mask)
    sce500_rhealpix_ds_Aragón = sce500_rhealpix_ds_WholeArea.where(Aragón_rhealpix_mask.data == 2)

    
    # Subtract 100 so we have values in [0,100] (they have an offset of +100 in the original dataset)
    sce500_rhealpix_ds_WholeArea = sce500_rhealpix_ds_WholeArea - 100
    sce500_rhealpix_ds_Aragón = sce500_rhealpix_ds_Aragón - 100
    
    return sce500_rhealpix_ds_WholeArea, sce500_rhealpix_ds_Aragón

# ###########################
# Auxiliary functions
# ###########################

def print_products_info(dc):
    """
    Print info of the products in the data cube. Useful for debugging these product definitions.
    """
    for product_name in dc.list_products(dataset_count=True)["name"]:
        print("=============")
        print(f"Product: {product_name}")
        print("=============")
        ds = dc.find_datasets(product=product_name)[0]
        print(ds.center_time)
        print(ds.bounds)
        print(ds.crs)
        print(ds.crs.dimensions)
        print(ds.local_path)

        
        print(ds.local_uri)
        print(ds.extent)

def calc_cohen_d(a, b):    
    """
    Calculate the Cohen's d between a and b.
    """
    denom = (len(a) + len(b) - 2)    
    num = (len(a) - 1) * (np.nanstd(a) ** 2) + (len(b) - 1) * (np.nanstd(b) ** 2) 
    pooled_std = (num / denom) ** 0.5
    return (np.nanmean(a) - np.nanmean(b)) / pooled_std

def calc_mae_bias_r(test, control):
    """
    Calculate MAE, BIAS and Spearman's r between test and control.
    Test and control must have the same length.
    """    
    # nanmean because there are NaN in our data
    mae =  np.nanmean(np.abs(test - control))    
    bias = np.nanmean(test - control)
    # Spearman correlation coeff. The pearsonr in scipy.stats does not handle nan values, and the Spearman R works fine and makes less assumptions on the distribution of the data
    spearman_r = scipy.stats.spearmanr(test.values.flatten(), control.values.flatten(), nan_policy='omit').correlation      
        
    return mae, bias, spearman_r

def rhealpix_ds_to_geodataframe(rhealpix_ds, rdggs, rhealpix_common_proj_string, rhealpix_common_resolution_index):
    cells = {"cellid" : [], "geometry" : [], "snow_cover" : []}

    nrows = len(rhealpix_ds.snow_cover_value.coords["y"])
    ncols = len(rhealpix_ds.snow_cover_value.coords["x"])

    for i in range(nrows):
        for j in range(ncols):
            data = rhealpix_ds.snow_cover_value.values[0][i][j]        
            if not np.isnan(data):                        
                x = rhealpix_ds.snow_cover_value.coords["x"][j].values
                y = rhealpix_ds.snow_cover_value.coords["y"][i].values
                curr_cell = rdggs.cell_from_point(rhealpix_common_resolution_index, (x, y))
                cells["cellid"].append(str(curr_cell))
                curr_cell_centroid = curr_cell.centroid()
                cells['geometry'].append(shapely.geometry.Point(x, y))
                cells['snow_cover'].append(data)

    gdf = gpd.GeoDataFrame(cells, crs=rhealpix_common_proj_string)    
    return gdf

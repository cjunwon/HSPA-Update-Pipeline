import geopandas as gpd
import boto3
import numpy as np
from config_functions import *

def main():
    s3_client = start_session()

    # SRI bucket name
    bucket = 'junwon-sri-test-bucket'
    # Path to designated folder for data on S3
    path = 'Test-Folder/'
    file_name = 'hillside_inventory_LA_centrality_full_new_evacmidnorth_lodes_kriging.geojson'
    # file_2_name = 'Street Centerline.geojson'
    object_name = "hillside_inventory_LA_centrality_full_new_evacmidnorth_lodes_kriging.geojson"
    # object_2_name = "Streets_Centerline.geojson"

    initial_upload = True   # Set to True if first time uploading data to S3


    '''
        Initial migration of local data to S3
    '''


    # Upload local copy file to S3

    # Check if folder directory exists and not empty (i.e. path is correct)
    if initial_upload:
        file_upload(s3_client, file_name, bucket, path, object_name=object_name, verbose=True)
        # file_upload(s3_client, file_2_name, bucket, path, object_name=object_2_name, verbose=True)
        return
        

    '''
        Data Pipeline for updating Designation
    '''


    # Read current ver. of data from S3  

    udf=gpd.read_file(f"s3://{bucket}/{path}{object_name}")
    # centerline=gpd.read_file(f"s3://{bucket}/{path}{object_2_name}")
    print("Data successfully read from S3")

    # inventory_data_extracted["Street_Designation"]=None

    # Data manipulation goes here

    # Upload updated data to S3
    geo_upload(s3_client, udf, bucket, path, object_name=object_name, verbose=True)
    # geo_upload(s3_client, centerline, bucket, path, object_name=object_2_name, verbose=True)
    return

if __name__ == "__main__":
    main()
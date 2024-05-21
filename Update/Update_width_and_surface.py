import geopandas as gpd
import pandas as pd
import json
import io
import boto3
import requests

s3_bucket = 'srilabgeodata'
s3_key_main_db = 'hillside_inventory_LA_centrality_full_new_evacmidnorth.geojson'
s3_key_street_centerline = 'Streets_Centerline_For_URL.geojson'

def update_width_surface():

    # Get content from the website
    s3 = boto3.client('s3')
    response = requests.get('https://opendata.arcgis.com/api/v3/datasets/aaaa5c1b83db4097985a15aba93082d5_0/downloads/data?format=geojson&spatialRefId=4326&where=1%3D1')

    if response.status_code == 200:
        # Convert the bytes response content into a GeoDataFrame
        gdf_online = gpd.read_file(io.BytesIO(response.content))
        print(gdf_online)
    try:
        # Read S3's GeoJSON file
        obj = s3.get_object(Bucket=s3_bucket, Key=s3_key_main_db)
        gdf_local = gpd.read_file(io.BytesIO(obj['Body'].read()))

        # Update length, width, surface
        # gdf_local['ST_LENGTH'] = gdf_local['SECT_ID'].map(gdf_online.set_index('SECT_ID')['ST_LENGTH'])
        gdf_local['ST_WIDTH'] = gdf_local['SECT_ID'].map(gdf_online.set_index('SECT_ID')['ST_WIDTH'])
        gdf_local['ST_SURFACE'] = gdf_local['SECT_ID'].map(gdf_online.set_index('SECT_ID')['ST_SURFACE'])
        
        # Save the updated GeoDataFrame back to the file
        updated_geojson = gdf_local.to_json()
        s3.put_object(Bucket=s3_bucket, Key=s3_key_main_db, Body=updated_geojson)

    except FileNotFoundError:
        print(f"File not found")
    except json.JSONDecodeError as e:
        print(f"Error decoding online JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    

if __name__ == "__main__":
    update_width_surface()
   

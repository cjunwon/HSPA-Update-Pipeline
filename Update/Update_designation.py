import geopandas as gpd
import pandas as pd
import json
import io
import boto3
import requests

s3_bucket = 'srilabgeodata'
s3_key_main_db = 'hillside_inventory_LA_centrality_full_new_evacmidnorth.geojson'
s3_key_street_centerline = 'Streets_Centerline_For_URL.geojson'

def update_designation():
    print("Update st_designation")

    s3 = boto3.client('s3')
    #Get data frp, data_la_city file
    response = requests.get('https://data.lacity.org/api/geospatial/keky-nxxr?method=export&format=GeoJSON')
    if response.status_code == 200:
        # Convert the bytes response content into a GeoDataFrame
        gdf_online = gpd.read_file(io.BytesIO(response.content))
    try:
        # Read GeoJSON file from S3
        obj = s3.get_object(Bucket=s3_bucket, Key=s3_key_main_db)
        gdf_local = gpd.read_file(io.BytesIO(obj['Body'].read()))

        # Extract the relevant columns from both GeoDataFrames
        online_columns = ['sect_id', 'street_des']
        local_columns = ['SECT_ID', 'Street_Designation']

        # Merge the DataFrames based on the common column 'sect_id' and 'SECT_ID'
        merged_df = pd.merge(gdf_local[local_columns], gdf_online[online_columns], left_on='SECT_ID', right_on='sect_id', how='left')

        # Update the 'Street_Designation' column in the local GeoDataFrame with the values from the online GeoDataFrame
        gdf_local['Street_Designation'] = merged_df['street_des']

        # Print and update local GeoDataFrame
        updated_geojson = gdf_local.to_json()
        s3.put_object(Bucket=s3_bucket, Key=s3_key_main_db, Body=updated_geojson)

    except FileNotFoundError:
        print(f"File not found")
    except json.JSONDecodeError as e:
        print(f"Error decoding online JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    update_designation()

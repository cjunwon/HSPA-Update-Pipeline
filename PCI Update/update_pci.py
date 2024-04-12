import io
import boto3
import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from scipy.spatial import KDTree
import json
import time



url_data_la_city = 'https://data.lacity.org/api/geospatial/yjxu-2kqq?method=export&format=GeoJSON'

s3_bucket = 'srilabgeodata'
s3_key_main_db = 'hillside_inventory_LA_centrality_full_new_evacmidnorth.geojson'
s3_key_street_centerline = 'Streets_Centerline_For_URL.geojson'

#Update the db's pci from data_lacity website
def update_pci_data_lacity():
    s3 = boto3.client('s3')
    #Download data_la_city
    response = requests.get(url_data_la_city)
    if response.status_code == 200:
        # Convert the bytes response content into a GeoDataFrame
        gdf_online = gpd.read_file(io.BytesIO(response.content))

    try:
        # gdf_local = gpd.read_file(url_local)
        obj = s3.get_object(Bucket=s3_bucket, Key=s3_key_main_db)
        gdf_local = gpd.read_file(io.BytesIO(obj['Body'].read()))

        online_columns = ['sect_id', 'pci']
        local_columns = ['SECT_ID', 'pci']
        before_update_count = gdf_local['pci'].eq(-1).sum()
        merged_df = pd.merge(gdf_local[local_columns], gdf_online[online_columns].drop_duplicates(subset=['sect_id']), left_on='SECT_ID', right_on='sect_id', how='left')
        print(gdf_local[local_columns])
        print(merged_df)
        # Update 'pci' values only if they are -1
        gdf_local.loc[gdf_local['pci'] == -1.0, 'pci'] = merged_df.loc[gdf_local['pci'] == -1, 'pci_y'].astype('float64')
        updated_geojson = gdf_local.to_json()
        s3.put_object(Bucket=s3_bucket, Key=s3_key_main_db, Body=updated_geojson)
        
        # print("After update_pci_data_lacity, we have ", before_update_count, " -1 value")

    except s3.exceptions.NoSuchKey:
        print(f"No such key: {s3_key_main_db}")
    except Exception as e:
        print(f"An error occurred: {e}")


#Update the db's pci from navigateLA website
def update_pci_navigateLA():
    s3 = boto3.client('s3')
    def get_pci_value(url):
        response = requests.get(url)
        #BeautifulSoup scrape data using certain criteria on the website
        soup = BeautifulSoup(response.content, 'html.parser')
        pci_element = soup.find('th', string='Pavement Condition Index (PCI)')
        try:
            pci_value = pci_element.find_next('td')
            pci_value = str(pci_value.find_next('td').get_text()).strip()
            # print(float(pci_value))
            return float(pci_value)
        except (AttributeError, ValueError, TypeError):
            return -1.0
        

    try:
        print("Getting objects...")
        obj1 = s3.get_object(Bucket=s3_bucket, Key=s3_key_main_db)
        gdf_local = gpd.read_file(io.BytesIO(obj1['Body'].read()))
        
        obj2 = s3.get_object(Bucket=s3_bucket, Key=s3_key_street_centerline)
        gdf_url = gpd.read_file(io.BytesIO(obj2['Body'].read()))

        url_columns = ['SECT_ID', 'NLA_URL']
        local_columns = ['SECT_ID', 'pci']

        gdf_url_df = gdf_url[url_columns].copy().drop_duplicates(subset=['SECT_ID'])
        gdf_local_df = gdf_local[local_columns].copy()

        # Merge gdf_local_df with gdf_url_df on SECT_ID
        merged_df = pd.merge(gdf_local_df, gdf_url_df, on='SECT_ID', how='left')
        print(merged_df)
        print("UPDATING PCI...")
        # Update 'pci' value in gdf_local for the corresponding SECT_ID
        gdf_local['pci'] = merged_df['NLA_URL'].apply(lambda url: get_pci_value('https://navigatela.lacity.org/' + str(url)))
        print(gdf_local['pci'])
       

        # Convert the updated GeoDataFrame to a GeoJSON string
        updated_geojson = gdf_local.to_json()

        # Upload the updated GeoJSON to the same S3 location
        s3.put_object(Bucket=s3_bucket, Key=s3_key_main_db, Body=updated_geojson)
        print(f"Successfully updated and uploaded the GeoJSON to S3")


    except Exception as e:
        print(f"An error occurred: {e}")


#Knearest neighbor
#Centroids
#Linear Regression
#Neural Net
#Update missing pci
#Kriging
def update_missing_point():
    s3 = boto3.client('s3')
    count = 0
    obj = s3.get_object(Bucket=s3_bucket, Key=s3_key_main_db)
    df = gpd.read_file(io.BytesIO(obj['Body'].read()))
    print(df)
    lats=np.array(df["centroid_lat"]).reshape((-1,1))
    lons=np.array(df["centroid_lon"]).reshape((-1,1))

    centroids=np.concatenate([lats,lons],axis=1)

    kdpoints=KDTree(centroids)

    pcis_prefinal=np.array(df["pci"])
    pcis_prefinal_new=np.array(df["pci"])

    kmax=0

    # Read the file and extract PCI values

    for i in range(0,len(pcis_prefinal)):
        if str(pcis_prefinal[i]) == "nan":
            point=centroids[i,:]
            k=6
            while True:
                result=kdpoints.query(point, k=k)
                
                dsts=result[0][1:]
                idxs=result[1][1:]
                pcis=pcis_prefinal[list(idxs)]
                dsts_new=dsts[~np.isnan(pcis)]
                idxs_new=idxs[~np.isnan(pcis)]
                pcis_new=pcis[~np.isnan(pcis)]
                if len(pcis_new)>2:
                    if k>kmax:
                        kmax=k
                    break
                else:
                    k+=1
            dstsum=sum(1/dsts_new)

            pcinew=sum(pcis_new*(1/dsts_new))/dstsum
            pcis_prefinal_new[i]=pcinew
            count += 1
        elif pcis_prefinal[i] == -1.0 :
            point=centroids[i,:]
            k=6
            while True:
                result=kdpoints.query(point, k=k)
                
                dsts=result[0][1:]
                idxs=result[1][1:]
                pcis=pcis_prefinal[list(idxs)]
                dsts_new=dsts[pcis!=-1.0]
                idxs_new=idxs[pcis!=-1.0]
                pcis_new=pcis[pcis!=-1.0]
                if len(pcis_new)>2:
                    if k>kmax:
                        kmax=k
                    break
                else:
                    k+=1
            dstsum=sum(1/dsts_new)
            
            pcinew=sum(pcis_new*(1/dsts_new))/dstsum
            pcis_prefinal_new[i]=pcinew
            count += 1
    df["pci"] = pcis_prefinal_new

    # Convert the updated GeoDataFrame to a GeoJSON string
    updated_geojson = df.to_json()


    # Upload the updated GeoJSON to S3
    s3.put_object(Bucket=s3_bucket, Key=s3_key_main_db, Body=updated_geojson)
    print(f"Successfully updated and uploaded the GeoJSON to S3: {s3_bucket}/{s3_key_main_db}")
    # print("AFTER update lacity, we have", count, "missing points")
        
def update_pci():
    update_pci_navigateLA()
    update_pci_data_lacity()
    update_missing_point()


if __name__ == "__main__":
    update_pci()

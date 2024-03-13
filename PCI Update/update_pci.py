import io
import boto3
import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from scipy.spatial import KDTree


url_data_la_city = 'https://data.lacity.org/api/geospatial/yjxu-2kqq?method=export&format=GeoJSON'

s3_bucket = 'srilabgeodata'
s3_key_main_db = 'hillside_inventory_LA_centrality_full_new_evacmidnorth_UPDATED_copy.geojson'
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

        merged_df = pd.merge(gdf_local[local_columns], gdf_online[online_columns], left_on='SECT_ID', right_on='sect_id', how='left')

        # Update 'pci' values only if they are -1
        gdf_local.loc[gdf_local['pci'] == -1, 'pci'] = merged_df.loc[gdf_local['pci'] == -1, 'pci_y'].astype('float64')

        # gdf_local.to_file(url_local, driver='GeoJSON')
        updated_geojson = gdf_local.to_json()
        s3.put_object(Bucket=s3_bucket, Key=s3_key_main_db, Body=updated_geojson)

    except s3.exceptions.NoSuchKey:
        print(f"No such key: {s3_key_main_db}")
    except Exception as e:
        print(f"An error occurred: {e}")


#Update the db's pci from navigateLA website
def update_pci_navigateLA():
    s3 = boto3.client('s3')
    fail_c = 0
    def get_pci_value(url):
        nonlocal fail_c
        try:
            response = requests.get(url)
            #BeautifulSoup scrape data using certain criteria on the website
            soup = BeautifulSoup(response.content, 'html.parser')
            pci_element = soup.find('th', string='Pavement Condition Index (PCI)')
            pci_value = pci_element.find_next('td')
            pci_value = int(pci_value.find_next('td').get_text())
            return pci_value
        except ValueError:
            fail_c+=1

    try:
        obj1 = s3.get_object(Bucket=s3_bucket, Key=s3_key_main_db)
        gdf_local = gpd.read_file(io.BytesIO(obj1['Body'].read()))
        
        obj2 = s3.get_object(Bucket=s3_bucket, Key=s3_key_street_centerline)
        gdf_url = gpd.read_file(io.BytesIO(obj2['Body'].read()))

        url_columns = ['SECT_ID', 'NLA_URL']
        local_columns = ['SECT_ID', 'pci']

        merged_df = pd.merge(gdf_local[local_columns], gdf_url[url_columns], left_on='SECT_ID', right_on='SECT_ID', how='left')

        gdf_local['pci'] = merged_df['NLA_URL'].apply(lambda url: get_pci_value('https://navigatela.lacity.org/' + url))

        # Convert the updated GeoDataFrame to a GeoJSON string
        updated_geojson = gdf_local.to_json()

        # Upload the updated GeoJSON to the same S3 location
        s3.put_object(Bucket=s3_bucket, Key=s3_key_main_db, Body=updated_geojson)
        print(f"Successfully updated and uploaded the GeoJSON to S3 with {fail_c} failures.")

    except Exception as e:
        print(f"An error occurred: {e}")



#Update missing pci
def update_missing_point():
    s3 = boto3.client('s3')

    obj = s3.get_object(Bucket=s3_bucket, Key=s3_key_main_db)
    df = gpd.read_file(io.BytesIO(obj['Body'].read()))

    lats=np.array(df["centroid_lat"]).reshape((-1,1))
    lons=np.array(df["centroid_lon"]).reshape((-1,1))

    centroids=np.concatenate([lats,lons],axis=1)

    kdpoints=KDTree(centroids)

    pcis_prefinal=np.array(df["pci"])
    pcis_prefinal_new=np.array(df["pci"])

    kmax=0

    for i in range(len(pcis_prefinal)):
        if pcis_prefinal[i]==-1:
            point=centroids[i,:]
            k=6
            while True:
                result=kdpoints.query(point, k=k)
                
                dsts=result[0][1:]
                idxs=result[1][1:]
                pcis=pcis_prefinal[list(idxs)]
                dsts_new=dsts[pcis!=-1]
                idxs_new=idxs[pcis!=-1]
                pcis_new=pcis[pcis!=-1]
                if len(pcis_new)>2:
                    if k>kmax:
                        kmax=k
                    break
                else:
                    k+=1
            dstsum=sum(1/dsts_new)
            
            pcinew=sum(pcis_new*(1/dsts_new))/dstsum
            pcis_prefinal_new[i]=pcinew
    df["pci"] = pcis_prefinal_new

    # Convert the updated GeoDataFrame to a GeoJSON string
    updated_geojson = df.to_json()

    # Upload the updated GeoJSON to S3
    s3.put_object(Bucket=s3_bucket, Key=s3_key_main_db, Body=updated_geojson)
    print(f"Successfully updated and uploaded the GeoJSON to S3: {s3_bucket}/{s3_key_main_db}")
    
        
def update_pci():
    update_pci_navigateLA()
    update_pci_data_lacity()
    update_missing_point()


if __name__ == "__main__":
    update_pci()

import pickle
import numpy as np
import geopandas as gpd
import numpy as np
import pickle
import boto3


with open(r'intermediate_files/B_matrix_weighted_updated.pickle', 'rb') as handle:
    B_matrix_weighted_array= pickle.load(handle)    
    
sumarray=B_matrix_weighted_array[:,6].copy()
sumarray.sort()
sumarray_reversed=sumarray[::-1]

def start_session():
    # Start session with AWS credentials
    # session = boto3.Session(profile_name="default")

    # S3 where the data is stored
    s3_client = boto3.client('s3')
    return s3_client

def download_file(s3_client, bucket, path, file_name, folder_to_save):
    # Download file from S3
    s3_client.download_file(bucket, path + file_name, folder_to_save + file_name)

s3_client = start_session()
bucket = 'junwon-sri-test-bucket'
path = 'Test-Folder/'
file_name = 'hillside_inventory_LA_centrality_full_new_evacmidnorth_lodes.geojson'
folder_to_save = 'lodes_od_data/'
download_file(s3_client, bucket, path, file_name, folder_to_save)

udf=gpd.read_file(r"udf/hillside_inventory_LA_centrality_full_new_evacmidnorth_lodes.geojson")

sids=np.array(udf["SECT_ID"]).astype(int)
allocated_Bmatrix=np.zeros((len(sids),10))

exceptioncounter=0
for i in range(len(sids)):
    print(i)
    try:
        sid=sids[i]
        idx=np.where(B_matrix_weighted_array[:,2]==sid)[0][0]
        allocated_Bmatrix[i,:]=B_matrix_weighted_array[idx,6:16]
    except:
        exceptioncounter+=1
    
    

    
udf["S000_adjusted"]=allocated_Bmatrix[:,0]/np.max(allocated_Bmatrix[:,0])
udf["SA01_adjusted"]=allocated_Bmatrix[:,1]/np.max(allocated_Bmatrix[:,1])
udf["SA02_adjusted"]=allocated_Bmatrix[:,2]/np.max(allocated_Bmatrix[:,2])
udf["SA03_adjusted"]=allocated_Bmatrix[:,3]/np.max(allocated_Bmatrix[:,3])
udf["SE01_adjusted"]=allocated_Bmatrix[:,4]/np.max(allocated_Bmatrix[:,4])
udf["SE02_adjusted"]=allocated_Bmatrix[:,5]/np.max(allocated_Bmatrix[:,5])
udf["SE03_adjusted"]=allocated_Bmatrix[:,6]/np.max(allocated_Bmatrix[:,6])
udf["SI01_adjusted"]=allocated_Bmatrix[:,7]/np.max(allocated_Bmatrix[:,7])
udf["SI02_adjusted"]=allocated_Bmatrix[:,8]/np.max(allocated_Bmatrix[:,8])
udf["SI03_adjusted"]=allocated_Bmatrix[:,9]/np.max(allocated_Bmatrix[:,9])

sumarray_hs=allocated_Bmatrix[:,0].copy()

sumarray_hs.sort()
sumarray_hs_reversed=sumarray_hs[::-1]

udf.to_file(r"udf/hillside_inventory_LA_centrality_full_new_evacmidnorth_lodes.geojson", driver='GeoJSON')
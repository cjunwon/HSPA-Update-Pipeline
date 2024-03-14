import boto3

# Create an S3 client
s3 = boto3.client('s3')

bucket = 'junwon-sri-test-bucket'
path = 'Test-Folder/'
file_name = 'hillside_inventory_LA_centrality_full_new_evacmidnorth_lodes.geojson'

# Specify the local file path
local_file_path = 'udf/hillside_inventory_LA_centrality_full_new_evacmidnorth_lodes_kriging.geojson'

# Upload the file to S3
s3.upload_file(local_file_path, bucket, path + file_name)
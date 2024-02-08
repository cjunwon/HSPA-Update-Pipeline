import boto3

def start_session():
    # Start session with AWS credentials
    # session = boto3.Session(profile_name="default")

    # S3 where the data is stored
    s3 = boto3.client('s3')
    return s3

def folder_exists_and_not_empty(bucket:str, path:str) -> bool:
    '''
    Folder should exists. 
    Folder should not be empty.
    '''
    s3 = boto3.client('s3')
    if not path.endswith('/'):
        path = path+'/' 
    resp = s3.list_objects(Bucket=bucket, Prefix=path, Delimiter='/',MaxKeys=1)
    return 'Contents' in resp
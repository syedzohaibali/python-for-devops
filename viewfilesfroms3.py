import boto3

s3 = boto3.client("s3")

bucket_name = "testing11669"
prefix = "server1/"

response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

if "Contents" in response:
    for obj in response["Contents"]:
        print(f"{obj['LastModified']} {obj['Size']} {obj['Key']}")
else:
    print("No files found in server1/")

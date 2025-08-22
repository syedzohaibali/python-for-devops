import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def list_buckets():
    try:
        # Create an S3 client (reads credentials from your AWS CLI config)
        s3 = boto3.client("s3")

        response = s3.list_buckets()
        buckets = response.get("Buckets", [])

        if not buckets:
            print("No buckets found.")
            return

        print("Your S3 buckets:")
        for bucket in buckets:
            print(f"- {bucket['Name']} (created on {bucket['CreationDate']})")

    except NoCredentialsError:
        print("❌ No AWS credentials found. Run `aws configure` first.")
    except PartialCredentialsError:
        print("❌ Incomplete AWS credentials. Check your AWS config.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    list_buckets()

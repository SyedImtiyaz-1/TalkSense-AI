import boto3
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_DEFAULT_REGION,
    S3_BUCKET,
    S3_PREFIX
)

class S3Service:
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_DEFAULT_REGION
        )
        self.bucket = S3_BUCKET
        self.prefix = S3_PREFIX

    def upload_file(self, file_obj, filename):
        """Upload a file to S3 bucket"""
        try:
            key = f"{self.prefix}{filename}"
            self.client.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs={'ACL': 'private'}
            )
            return True, f"Successfully uploaded {filename}"
        except Exception as e:
            return False, str(e)

    def delete_file(self, key):
        """Delete a file from S3 bucket"""
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            return True, f"Successfully deleted {key}"
        except Exception as e:
            return False, str(e)

    def list_files(self):
        """List all files in the S3 bucket/prefix"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=self.prefix
            )
            files = response.get('Contents', [])
            return [
                {
                    'Key': f['Key'],
                    'Size': f['Size'],
                    'LastModified': f['LastModified'],
                    'URL': f"https://{self.bucket}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{f['Key']}"
                }
                for f in files if f['Key'] != self.prefix  # Exclude the prefix itself
            ]
        except Exception as e:
            print(f"Error listing S3 files: {e}")
            return []

# Create a singleton instance
s3_service = S3Service() 
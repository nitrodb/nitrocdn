import os
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

# the secret the Rest API should use.
secret = os.getenv('secret')

client = Minio(
    endpoint=os.getenv('host'),
    access_key=os.getenv('access_key', ''),
    secret_key=os.getenv('secret_key', ''),
    secure=False
)

# initialize buckets

if not client.bucket_exists('user-avatars'):
    client.make_bucket('user-avatars')

if not client.bucket_exists('user-banners'):
    client.make_bucket('user-banners')

if not client.bucket_exists('guild-avatars'):
    client.make_bucket('guild-avatars')

if not client.bucket_exists('guild-banners'):
    client.make_bucket('guild-banners')

if not client.bucket_exists('guild-user-avatars'):
    client.make_bucket('guild-user-avatars')

if not client.bucket_exists('guild-user-banners'):
    client.make_bucket('guild-user-banners')

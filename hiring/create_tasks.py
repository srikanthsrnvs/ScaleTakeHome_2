import json
import os
import requests

HIRING_NAME = 'Srikanth'
# Your Scale API Test Key
SCALE_API_KEY = 'test_5598408ae5ec4431ab22c52715bfda61'
S3_BUCKET_URL = f'https://fe-hiring.s3-us-west-2.amazonaws.com/{HIRING_NAME}/'

attachments = []

for index in range(3):
    attachment = os.path.join(S3_BUCKET_URL, 'frames/frame_%d.json' % index)
    attachments.append(attachment)

payload = {
    'callback_url': 'http://example.com/callback',
    'instruction': 'Please label all cars, pedestrians, and cyclists in each frame.',
    'attachment_type': 'json',
    'attachments': attachments,
    'labels': ['car', 'pedestrian', 'cyclist'],
    'meters_per_unit': 1,
    'max_distance_meters': 30
}

headers = {"Content-Type": "application/json"}

task_request = requests.post("https://api.scale.ai/v1/task/lidarannotation",
    json=payload,
    headers=headers,
    auth=(SCALE_API_KEY, ''))

print(task_request.json())

import pykitti
import json
import os
import numpy as np
import boto3
from pyquaternion import Quaternion

# Name of your bucket
HIRING_NAME = 'Srikanth'
S3_BUCKET = 'fe-hiring'

# kitti data definitions
BASEDIR = 'C:\\Users\\Srikanth\\Downloads\\ScaleTakeHome_2\\hiring\\files'

# S3 connection
s3 = boto3.client(
    's3',
    aws_access_key_id='AKIATMR3LYHUDYJSJ3C7',
    aws_secret_access_key='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'
)

DRIVE_DATE = '2011_09_26'
DRIVE_ID = '0048'

# S3 Upload
def upload_frame(frame_name, frame):
  frame_bucket_key = f'{HIRING_NAME}/frames/' + frame_name
  #  s3.put_object(Bucket=S3_BUCKET, Key=frame_bucket_key, Body=json.dumps(frame, indent=2), ACL='public-read')
  s3.put_object(Bucket=S3_BUCKET, Key=frame_bucket_key, Body=json.dumps(frame, indent=2))
  print(frame_bucket_key + " Uploaded")

def upload_image(index):
  # upload image to s3
  with open(os.path.join(BASEDIR, f'{DRIVE_DATE}/{DRIVE_DATE}_drive_{DRIVE_ID}_sync/image_00/data/',f'000000000{index}.png' ), 'rb') as image:
    image_bucket_key = f'{HIRING_NAME}/images/000000000{index}.png'
    s3.put_object(Bucket=S3_BUCKET, Key=image_bucket_key, Body=image)
    print(image_bucket_key + " Uploaded")

FRAME_COUNT = 3

def run():
    # get intrinsic values
    data = pykitti.raw(BASEDIR, DRIVE_DATE, DRIVE_ID, frames=range(FRAME_COUNT))

    K = data.calib.K_cam0
    fx = K[0,0]
    fy = K[1,1]
    cx = K[0,2]
    cy = K[1,2]

    # Extract extrinsics values
    point_velo = np.array([0,0,0,1])
    point_cam0 = data.calib.T_cam0_velo.dot(point_velo)
    R = Quaternion(matrix=data.calib.T_cam0_velo.T)

    cameraRotation = R
    cameraPosition = point_cam0

    for index in range(FRAME_COUNT):
        upload_image(index) # upload image to s3
        frame = {
                'points': [],
                "timestamp": 0,
                "device_position": {
                    "x": 0,
                    "y": 0,
                    "z": 0
                },
                "device_heading": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "w": 1
                },
                "images": [
                    {
                        "fy": fy,
                        "cx": cx,
                        "image_url": f"https://s3.us-west-2.amazonaws.com/fe-hiring/{HIRING_NAME}/images/000000000{index}.png",
                        "position": {
                            "x": cameraPosition[0],
                            "y": cameraPosition[1],
                            "z": cameraPosition[2]
                        },
                        "fx": fx,
                        "timestamp": 1,
                        "cy": cy,
                        "heading": {
                            "w": cameraRotation[0],
                            "x": cameraRotation[1],
                            "y": cameraRotation[2],
                            "z": cameraRotation[3]
                            }
                        }
                    ],
            }
        # timestamp
        frame['timestamp'] =  data.timestamps[index].timestamp()

        # points
        for p_index, points in enumerate(data.velo):
            if(p_index == index):
                for point in points:
                    frame["points"].append({ 'x': float(point[0]),'y': float(point[1]),'z': float(point[2]),'i': 0.5 })

        upload_frame('frame_%s.json' % index, frame)

run()

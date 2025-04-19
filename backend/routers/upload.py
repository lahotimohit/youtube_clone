from fastapi import Depends, HTTPException, APIRouter
from schema import UploadMetaData
from database import get_session
from models import Video
from sqlmodel import Session
from oauth2 import current_user
from config import settings
import boto3
import uuid

router=APIRouter()

s3_client=boto3.client("s3", region_name=settings.aws_region_name)

@router.get("/url")
def generate_presigned_url(user=Depends(current_user)):
    try:
        print(user)
        video_id=f"videos/{user.id}/{uuid.uuid4()}"
        response = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket":settings.aws_raw_videos_bucket,
                "Key":video_id,
                "ContentType":"video/mp4"
            }
        )
        return {
            "url":response,
            "video_id":video_id
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/url/thumbnail")
def generate_presigned_url_tumbnail(user=Depends(current_user)):
    try:
        print(user)
        thumbnail_id=f"videos/{user.id}/{uuid.uuid4()}"
        response = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket":settings.aws_thumbnail_bucket,
                "Key":thumbnail_id,
                "ContentType":"image/*"
            }
        )
        return {
            "url":response,
            "thumbnail_id":thumbnail_id
        }
    except Exception as e:
        raise HTTPException(500, str(e))
    

@router.post("/metadata")
def upload_metadata(
        metadata: UploadMetaData,
        user=Depends(current_user),
        db:Session = Depends(get_session)
):
    print(metadata)
    new_video = Video(
        id=metadata.video_id,
        title=metadata.title,
        description=metadata.desciption,
        video_s3_key=metadata.video_s3_key,
        visibility=metadata.visibility,
        user_id=user.id
    )

    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return new_video

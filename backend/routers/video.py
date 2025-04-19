from fastapi import APIRouter, Depends, HTTPException
from database import get_session
from models import Video, VideoProcessing, VideoVisibility
from sqlmodel import Session, select, or_
from oauth2 import current_user

router = APIRouter()

@router.get("/all")
def get_all_videos(
    user=Depends(current_user),
    db:Session=Depends(get_session)
):
    videos=db.exec(select(Video).filter(Video.is_processing==VideoProcessing.COMPLETED, Video.visibility==VideoVisibility.PUBLIC)).all()
    return videos

@router.get("/")
def get_video_info(
    video_id:str,
    user=Depends(current_user),
    db:Session=Depends(get_session)
):
    video=db.exec(select(Video).
                   filter(Video.is_processing==VideoProcessing.COMPLETED, 
                          or_(Video.visibility==VideoVisibility.PUBLIC,
                              Video.visibility==VideoVisibility.UNLISTED))).first()
    return video


@router.put("/")
def update_video_by_id(id:str, db:Session=Depends(get_session)):
    video=db.exec(select(Video).filter(Video.id==id)).first()
    if not video:
        raise HTTPException(404, "Video Not Found....")
    video.is_processing=VideoProcessing.COMPLETED
    db.commit()
    db.refresh(video)
    return video
import json
from fastapi import APIRouter, Depends

from .ticket import tickets, user_email_dict
from .image import local_img_dirs, drive_img_dirs
from ..utils.security import api_key_checker


router = APIRouter()


@router.get('/get_status')
async def get_status():
    return dict(zip(
        ('tickets', 'user_email_dict', 'local_img_dirs', 'drive_img_dirs'),
        map(bool, (tickets, user_email_dict, local_img_dirs, drive_img_dirs))))


def config(app, settings):
    app.include_router(
        router,
        tags=['status'],
        prefix="/api/v1",
        # dependencies=[Depends(api_key_checker)],
    )

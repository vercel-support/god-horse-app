import json
from fastapi import APIRouter, Depends, HTTPException

from .ticket import tickets, user_email_dict
from .image import drive_img_dirs
from ..utils.ticket import get_tickets, clear_sheet
from ..utils.image import update_drive_img_dirs
from ..utils.security import api_key_checker


router = APIRouter()


@router.get('/refresh', dependencies=[Depends(api_key_checker)],)
async def refresh(sheet_name):
    global tickets, user_email_dict, drive_img_dirs
    try:
        tickets.update(get_tickets(sheet_name=sheet_name))
        user_email_dict = dict()
        await clear_sheet(sheet_name)
        update_drive_img_dirs(drive_img_dirs)
        return {'status': f'refresh {sheet_name}'}
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f'Error: {str(e)}')


@router.get('/info')
async def status():
    return dict(zip(
        ('tickets', 'user_email_dict', 'drive_img_dirs'),
        map(bool, (tickets, user_email_dict, drive_img_dirs))))


def config(app, settings):
    app.include_router(
        router,
        tags=['status'],
        prefix="/api/v1",
        # dependencies=[Depends(api_key_checker)],
    )

import logging
from typing import Optional
from pydantic import EmailStr
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.logger import logger

from .image import local_img_dirs, drive_img_dirs
from ..utils.ticket import update_sheet, get_tickets, generate_finish_cert, clear_sheet
from ..utils.image import get_img
from ..utils.security import api_key_checker

logger.setLevel(logging.DEBUG)
router = APIRouter()
tickets = dict()
user_email_dict = dict()


@router.get('/get_ticket')
async def get_ticket(sheet_name: str, email: EmailStr, background_tasks: BackgroundTasks, name: str):
    global tickets, user_email_dict
    if email in user_email_dict:
        number, title, words = user_email_dict[email]
        return {'words': words}
    if sheet_name not in tickets:
        raise HTTPException(
            status_code=404, detail=f'{sheet_name} not in tickets!!')
    if not tickets.get(sheet_name):
        raise HTTPException(
            status_code=404, detail=f'{sheet_name} is empty!!')
    number, title, words, *_ = tickets[sheet_name].pop()
    user_email_dict[email] = (number, title, words)
    background_tasks.add_task(update_sheet, sheet_name,
                              ind=number, values=[name, email, '0'])
    background_tasks.add_task(
        generate_finish_cert, dir_name=sheet_name, name=name, title=title, words=words)
    return {'words': words}


@router.get('/refresh_tickets')
async def refresh_tickets(sheet_name, background_tasks: BackgroundTasks = None):
    global tickets, user_email_dict
    try:
        tickets.update(get_tickets(sheet_name=sheet_name))
        await clear_sheet(sheet_name)
        get_img(sheet_name, 'template.png', background_tasks,
                local_img_dirs, drive_img_dirs)
        user_email_dict = dict()

        return {'status': f'refresh {sheet_name}'}
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f'Error: {str(e)}')


# @router.on_event('startup')
# async def on_startup() -> None:
#     await refresh_tickets('20210227')


def config(app, settings):
    app.include_router(
        router,
        tags=['ticket'],
        prefix="/api/v1",
        dependencies=[Depends(api_key_checker)],
    )

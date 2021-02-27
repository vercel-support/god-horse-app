from typing import Optional
from pydantic import EmailStr
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.logger import logger
import logging

from .image import drive_img_dirs
from ..utils.ticket import update_sheet, get_tickets, generate_finish_cert, clear_sheet
from ..utils.image import update_drive_img_dirs
from ..utils.security import api_key_checker
from ..config import get_settings

logger.setLevel(logging.DEBUG)
router = APIRouter()
settings = get_settings()
tickets = dict()
user_email_dict = dict()


@router.get('/get_ticket')
async def get_ticket(sheet_name: str, email: EmailStr, background_tasks: BackgroundTasks, name: str):
    global tickets, user_email_dict, drive_img_dirs
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
        generate_finish_cert, sheet_name, drive_img_dirs, title, words, name)
    return {'words': words}


@router.get('/update_tickets')
def update_tickets(sheet_name: str, background_tasks: BackgroundTasks):
    global tickets, user_email_dict
    tickets[sheet_name] = list()
    _tickets = get_tickets(sheet_name=sheet_name)
    for number, title, words, name, email, is_sendt in _tickets:
        if name and email:
            user_email_dict[email] = (number, title, words)
        else:
            tickets[sheet_name].append(
                (number, title, words, name, email, is_sendt))

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

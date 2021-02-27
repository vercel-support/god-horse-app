from app.utils.image import get_img_id, update_drive_img_dirs
import logging
from starlette.types import Message
from fastapi import APIRouter, Depends, exceptions
from fastapi import BackgroundTasks, HTTPException
from fastapi.logger import logger
from starlette.status import HTTP_202_ACCEPTED

from .image import drive_img_dirs
from ..schemas.email import EmailAttachFileSchema
from ..utils.security import api_key_checker
from ..utils.ticket import get_tickets, updae_is_sent_list
from ..utils.email import send_mail
from ..config import get_settings

router = APIRouter()
settings = get_settings()
logger.setLevel(logging.DEBUG)


@router.post("/send_email", status_code=HTTP_202_ACCEPTED, deprecated=False)
async def go_send_email(message: EmailAttachFileSchema):
    succeed = await send_mail(message)
    if not succeed:
        raise HTTPException(
            status_code=404, detail=f'Fail to send this mail with {message.email} !!')
    return {'info': 'Send the mail successfully !!'}


@router.post("/send_all_emails", status_code=HTTP_202_ACCEPTED, deprecated=False)
async def go_send_all_email(dir_name: str, background_tasks: BackgroundTasks):
    tickets = get_tickets(sheet_name=dir_name)
    update_drive_img_dirs(drive_img_dirs)
    send_list = list()
    for number, title, words, name, email, is_sent in tickets[dir_name]:
        if email and name and is_sent == '0':
            try:
                img_id = get_img_id(dir_name, f'{name}.png', drive_img_dirs)
                message = dict(
                    to_email=email,
                    from_email=settings.FROM_EMAIL,
                    subject='神駒團愛你',
                    html_content=f'<strong>{words} - {name}</strong>',
                    file_type='image/png',
                    file_id=img_id,
                    file_name=f'{name}.png',
                )
                succeed = await send_mail(message)
                if succeed:
                    send_list.append(number)
                else:
                    logger.warning(f'Fail to send the mail ({email})!!')
            except Exception as e:
                logger.warning(f'Fail to send the mail ({email})!!')
    logger.info('Finish sending all mails!!')
    logger.info(f'Updating the column "is_sent" of sheet ({dir_name})')
    background_tasks.add_task(updae_is_sent_list, dir_name, send_list)
    return {'info': 'Finish sending all mails!!'}


def config(app, settings):
    app.include_router(
        router,
        tags=['email'],
        prefix="/api/v1",
        dependencies=[Depends(api_key_checker)],
    )

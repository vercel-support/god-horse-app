import logging
from starlette.types import Message
from fastapi import APIRouter, Depends
from fastapi import BackgroundTasks
from fastapi.logger import logger
from starlette.status import HTTP_202_ACCEPTED

from ..schemas.email import EmailSchema, EmailAttachFileSchema
from ..utils.security import api_key_checker
from ..utils.ticket import get_tickets, updae_is_sent
from ..utils.email import send_mail
from ..config import get_settings

router = APIRouter()
settings = get_settings()
logger.setLevel(logging.DEBUG)


@router.post("/send_email", status_code=HTTP_202_ACCEPTED, deprecated=False)
async def go_send_email(message: EmailAttachFileSchema):
    succeed = await send_mail(message)
    if succeed:
        return {'status': f'Fail to send this mail with {message.email} !!'}
    return {'status': 'Send the mail successfully !!'}


@router.post("/send_all_emails", status_code=HTTP_202_ACCEPTED, deprecated=False)
async def go_send_all_email(dir_name: str, background_tasks: BackgroundTasks):
    tickets = get_tickets(sheet_name=dir_name)
    send_list = list()
    for number, words, name, email, is_sent in tickets[dir_name]:
        if email and name and is_sent == '0':
            message = dict(
                to_email=email,
                from_email=settings.FROM_EMAIL,
                subject='神駒團愛你',
                html_content=f'<strong>{words} - {name}</strong>',
                file_type='image/png',
                file_name=f'app/files/{dir_name}/{number}.png',
            )
            succeed = await send_mail(message)
            if succeed:
                send_list.append(int(number)+1)
            else:
                logger.warning(f'Fail to send the mail ({email})!!')
    logger.info('Finish sending all mails!!')
    logger.info(f'Updating the column "is_sent" of sheet ({dir_name})')
    background_tasks.add_task(updae_is_sent, dir_name, send_list)
    return {'status': 'Finish sending all mails!!'}


def config(app, settings):
    app.include_router(
        router,
        tags=['email'],
        prefix="/api/v1",
        dependencies=[Depends(api_key_checker)],
    )

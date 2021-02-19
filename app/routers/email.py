from pydantic.utils import to_camel
from starlette.types import Message
from app.config import Settings
from fastapi import APIRouter, Depends
from fastapi import BackgroundTasks
from starlette.status import HTTP_202_ACCEPTED

from ..schemas.email import EmailSchema, EmailAttachFileSchema
from .ticket import user_email_dict
from ..utils.security import api_key_checker
from ..utils.task import send_mail
from ..config import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/send_email", status_code=HTTP_202_ACCEPTED, deprecated=False)
async def go_send_email(message: EmailAttachFileSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        send_mail, message, settings.SENDGRID_API_KEY.get_secret_value())
    return {'status': 'Finish sending !!'}


@router.post("/send_all_emails", status_code=HTTP_202_ACCEPTED, deprecated=False)
async def go_send_all_email(dir_name: str, background_tasks: BackgroundTasks):
    for email, number_name in user_email_dict.items():
        number, name, words = number_name
        message = EmailAttachFileSchema(
            to_email=email,
            from_emal='whighwall@gmail.com',
            subject='神駒團愛你',
            html_contemt=f'<strong>{words}</strong>{name}',
            file_type='image/png',
            file_name=f'app/files/{dir_name}/{number}.png',
        )
        background_tasks.add_task(
            send_mail, message, settings.SENDGRID_API_KEY.get_secret_value())
    return {'status': 'Finish sending !!'}


def config(app, settings):
    app.include_router(
        router,
        tags=['email'],
        prefix="/api/v1",
        dependencies=[Depends(api_key_checker)],
    )

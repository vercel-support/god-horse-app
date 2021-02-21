from functools import lru_cache
from typing import BinaryIO, Union, Dict
import pathlib
import base64
import logging
from fastapi.logger import logger

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileName, FileType, FileContent, Disposition

from ..schemas.email import EmailSchema, EmailAttachFileSchema
from ..config import get_settings

logger.setLevel(logging.DEBUG)
settings = get_settings()


@lru_cache()
def get_sg_client(api_key: str = None):
    if not api_key:
        api_key = settings.SENDGRID_API_KEY.get_secret_value()
    return SendGridAPIClient(api_key)


async def send_mail(message: Union[Dict, EmailSchema, EmailAttachFileSchema]):
    message = message if isinstance(message, Dict) else message.dict()
    email = generate_email(**message)
    succeed = False
    try:
        sg = get_sg_client()
        response = sg.send(email)
        logger.info('send mail status_code: '+str(response.status_code))
        succeed = response.status_code >= 200
        # logger.info('response body: ' + str(response.body))
        # logger.info('response header' + str(response.headers))
    except Exception as e:
        logger.warning(f'Error: {str(e)}')
    return succeed


def generate_email(
    from_email: str,
    to_email: str,
    subject: str,
    html_content: str = None,
    plain_text_content: str = None,
    file_name: str = None,
    file_type: str = None,
):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
        plain_text_content=plain_text_content,
    )
    if file_name:
        file = pathlib.Path(file_name)
        if file.exists():
            data = open(file_name, 'rb').read()
            message.attachment = generate_attachFile(
                data, file_name, file_type)
        else:
            logger.warning(f'{file_name} does not exist!!')
    return message


def generate_attachFile(
    data: BinaryIO,
    file_name: str,
    file_type: str,
):
    encoded_file = base64.b64encode(data).decode()
    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName(file_name),
        FileType(file_type),
        Disposition('attachment')
    )
    return attachedFile

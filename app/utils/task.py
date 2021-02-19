from typing import BinaryIO, Union
import base64
import logging
from fastapi.logger import logger
from fastapi import HTTPException, status

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileName, FileType, FileContent, Disposition

from ..schemas.email import EmailSchema, EmailAttachFileSchema

logger.setLevel(logging.DEBUG)


async def send_mail(message: Union[EmailSchema, EmailAttachFileSchema], api_key: str):
    email = generate_email(**message.dict())
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(email)
        logger.info('send mail status_code: '+str(response.status_code))
        # print('response body: ', response.body)
        # print('response header', response.headers)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={
                            'error': str(e)})


def generate_email(
    from_email: str,
    to_email: str,
    subject: str,
    html_contemt: str,
    plain_text_content: str,
    file_name: str,
    file_type: str,
):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_contemt,
        plain_text_content=plain_text_content,
    )
    if file_name:
        data = open(f'app/files/{file_name}', 'rb').read()
        message.attachment = generate_attachFile(data, file_name, file_type)
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

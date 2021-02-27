from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from sendgrid.helpers.mail import file_name


class ContentType(str, Enum):
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"


class BaseEmailSchema(BaseModel):
    to_email: EmailStr
    from_email: EmailStr


class EmailSchema(BaseEmailSchema):
    subject: str = Field(max_length=78)
    html_content: Optional[str]
    plain_text_content: Optional[str]


class EmailAttachFileSchema(EmailSchema):
    file_type: Optional[str]
    file_id: Optional[str]
    file_name: Optional[str]

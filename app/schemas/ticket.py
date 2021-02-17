from pydantic import BaseModel, EmailStr


class Ticket(BaseModel):
    number: int
    words: str
    name: str
    email: EmailStr

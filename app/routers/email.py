from fastapi import APIRouter, Depends
from fastapi import BackgroundTasks
from starlette.status import HTTP_202_ACCEPTED

from ..schemas.email import EmailSchema
from ..utils.security import api_key_checker
from ..utils.task import send_mail

router = APIRouter()


@router.post("/emails", status_code=HTTP_202_ACCEPTED, deprecated=True)
async def send_email(message: EmailSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_mail, **message.dict(by_alias=True))


def config(app, settings):
    app.include_router(
        router,
        tags=['email'],
        prefix="/api/v1",
        dependencies=[Depends(api_key_checker)],
    )

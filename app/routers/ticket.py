from typing import Optional
from pydantic import EmailStr
from fastapi import APIRouter, Depends, BackgroundTasks

from ..utils.ticket import update_sheet, get_tickets
from ..utils.security import api_key_checker


router = APIRouter()
tickets = dict()


@router.get('/get_ticket')
async def get_ticket(sheet_name: str, email: EmailStr, background_tasks: BackgroundTasks, name: Optional[str] = None):
    global tickets
    if sheet_name not in tickets:
        return {'number': -1, 'words': f'{sheet_name} not in tickets'}
    if not tickets.get(sheet_name):
        return {'number': -1, 'words': f'{sheet_name} is empty!!'}
    number, words, *_ = tickets[sheet_name].pop()
    background_tasks.add_task(update_sheet, sheet_name, ind=int(
        number)+1, values=[name, email])
    return {'number': number, 'words': words}


@router.get('/refresh_tickets')
async def refresh_tickets(sheet_name):
    global tickets
    try:
        tickets = get_tickets(tickets, sheet_name)
        return {'status': f'refresh {sheet_name}'}
    except Exception as e:
        print(str(e))
        return {'status': f'Worksheet {sheet_name} not found'}


def config(app, settings):
    app.include_router(
        router,
        tags=['ticket'],
        prefix="/api/v1",
        dependencies=[Depends(api_key_checker)],
    )

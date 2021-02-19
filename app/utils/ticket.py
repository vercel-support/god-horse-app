from typing import List, Dict
from io import BytesIO, TextIOWrapper
import string
from random import shuffle
import gspread

from .image import image_merge_text
from ..config import get_settings

settings = get_settings()
gc = gspread.service_account(filename=settings.SERVICE_ACCOUNT_CRED_PATH)


def get_sheet(sheet_name: str):
    sh = gc.open(settings.SHEET_FILE_NAME).worksheet(sheet_name)
    return sh


def update_sheet(sheet_name: str, ind: int, values: List):
    wks = gc.open(settings.SHEET_FILE_NAME).worksheet(sheet_name)
    end = string.printable[37+len(values)]
    wks.update(f'C{ind}:{end}{ind}', [values])


def get_tickets(tickets: Dict, sheet_name: str, shuffled=True):
    sh = get_sheet(sheet_name)
    titles, *sheet_tickets = sh.get_all_values()
    if shuffled:
        shuffle(sheet_tickets)
    tickets.update({sheet_name: sheet_tickets})
    return tickets


async def generate_finish_cert(dir_name: str, name: str, number: str, words: str):
    img = BytesIO(
        open(f'{settings.APP_DIR}/files/{dir_name}/template.png', 'rb').read())
    img = image_merge_text(image=img, text=words)
    img = image_merge_text(image=img, xy=(50, 50), text=name)
    with open(f'app/files/{dir_name}/{number}.png', 'wb') as f:
        f.write(img.read())

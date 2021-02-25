from logging import log
import logging
from cachetools.func import ttl_cache
from functools import lru_cache
from pathlib import Path
from typing import List, Dict
from io import BytesIO
from fastapi.logger import logger
import logging
import json
import string
from random import shuffle
import gspread
from gspread.models import Cell

from .image import image_merge_text, save_img
from ..config import get_settings

settings = get_settings()
gc = gspread.service_account(filename=settings.SERVICE_ACCOUNT_CRED_PATH)
logger.setLevel(logging.DEBUG)
a_z = string.printable[36:62]


@ttl_cache(ttl=600)
def get_sheet(sheet_name: str = None):
    spread_sh = gc.open(settings.SHEET_FILE_NAME)
    if not sheet_name:
        return spread_sh
    return spread_sh.worksheet(sheet_name)


def update_sheet(sheet_name: str, ind: int, values: List):
    wks = gc.open(settings.SHEET_FILE_NAME).worksheet(sheet_name)
    end = a_z[a_z.index('C')+len(values)]
    wks.update(f'D{ind}:{end}{ind}', [values])


def get_sheet_list(sheet_name: str, shuffled=False):
    sh = get_sheet(sheet_name)
    titles, *sheet_list = sh.get_all_values()
    if shuffled:
        shuffle(sheet_list)
    return titles, sheet_list


@ttl_cache(ttl=600)
def get_tickets(sheet_name: str, shuffled=True):
    _, sheet_tickets = get_sheet_list(sheet_name, shuffled)
    return {sheet_name: sheet_tickets}


def str_to_tuple(s):
    # s = (1, 2, 3, 4)
    return tuple(map(int, s.replace('(', '').replace(')', '').replace(' ', '').split(',')))


@ttl_cache(ttl=600)
def get_cert_configs(sheet_name: str):
    titles, config_list = get_sheet_list(sheet_name)
    cert_conf_dict = dict()
    for text_conf in config_list:
        temp = dict(zip(titles[1:], text_conf[1:]))
        [temp.update({k: func(temp[k])}) for k, func in zip(
            ('color', 'size', 'position', 'box'), (str_to_tuple, int, str_to_tuple, str_to_tuple)) if temp.get(k)]
        cert_conf_dict.update({text_conf[0]: temp})
    return cert_conf_dict


async def generate_finish_cert(dir_name: str, name: str, words: str, title: str):
    text_conf_dict = get_cert_configs(settings.SHEET_CERT_CONF_NAME)
    img = BytesIO(
        open(settings.IMG_DIR.joinpath(f'{dir_name}/template.png').absolute(), 'rb').read())
    img = image_merge_text(img, words, **text_conf_dict['words'])
    img = image_merge_text(img, name, **text_conf_dict['name'])
    img = image_merge_text(img, title, **text_conf_dict['title'])
    file_path = settings.IMG_DIR.joinpath(
        f'{dir_name}/{name}.png').absolute()
    save_img(img, file_path)


async def clear_sheet(sheet_name: str, sheet_range: str = 'D2:F582'):
    sh = get_sheet()
    sh.values_clear(f"{sheet_name}!{sheet_range}")


def updae_is_sent_list(sheet_name: str, row_list: List[int]):
    if not row_list:
        logger.warning('send_list is empty')
        return
    sh = get_sheet(sheet_name)
    sh.update_cells([
        Cell(row, 6, 1) for row in map(int, row_list)
    ])

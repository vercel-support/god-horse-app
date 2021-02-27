from functools import lru_cache
from io import BytesIO, StringIO
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional
from textwrap import wrap
from fastapi import BackgroundTasks
from fastapi.logger import logger
from PIL import Image, ImageFont, ImageDraw

from pydrive.auth import GoogleAuth, ServiceAccountCredentials
from pydrive.drive import GoogleDrive

from ..config import get_settings

settings = get_settings()
logger.setLevel(logging.DEBUG)


def get_drive():
    gauth = GoogleAuth()
    scope = ['https://www.googleapis.com/auth/drive']
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        settings.SERVICE_ACCOUNT_CRED_PATH, scope)
    drive = GoogleDrive(gauth)
    return drive


drive = get_drive()


def get_dir_list(q_id='1TFlN9CB18Xv4g29swpjvhGKkBWAxFig6', dir_only=False):
    dir_str = "mimeType='application/vnd.google-apps.folder' and" if dir_only else ''
    file_list = drive.ListFile(
        {'q': f"'{q_id}' in parents and {dir_str} trashed=false"}).GetList()
    return {file['title']: file['id'] for file in file_list}


def update_drive_img_dirs(img_dirs: Dict):
    if img_dirs is None:
        logger.warning(f'img_dirs can not be None!!')
        return
    _img_dirs = get_dir_list(dir_only=True)
    for title, _id in _img_dirs.items():
        if title not in img_dirs and '.' not in title:
            img_dirs[title] = {'id': _id,
                               'files': get_dir_list(q_id=_id)}


def get_img_id(dir_name: str, img_name: str, drive_img_dirs: Dict):
    if not drive_img_dirs.get(dir_name) or not drive_img_dirs.get(dir_name).get('files').get(img_name):
        logger.info('go updating drive_img_dirs!!')
        update_drive_img_dirs(drive_img_dirs)
    return drive_img_dirs.get(dir_name).get('files').get(img_name)


def get_img(img_id) -> BytesIO:
    img = BytesIO(get_file(img_id))
    return img


@lru_cache()
def get_file(_id: str, decoding=False):
    file = drive.CreateFile({'id': _id})
    file.FetchContent()
    if decoding:
        return file.content.getvalue().decode('utf-8')
    return file.content.getvalue()


def upload_img(img: BytesIO, dir_id: str, img_name: str):
    file = drive.CreateFile({'parents': [{'id': dir_id}]})
    file.content = img
    file['title'] = img_name
    file['mimeType'] = 'image/png'
    file.Upload()


def image_merge_text(
        image: BytesIO,
        text: str,
        position: Union[Tuple, List] = None,
        box: Union[Tuple, List] = None,
        draw_box: bool = False,
        font: str = 'SFNSMono.ttf',
        size: int = 150,
        color: Union[Tuple[int], List[int]] = (0, 0, 0)) -> BytesIO:
    img = Image.open(image).convert('RGBA')
    img_editable = ImageDraw.Draw(img)
    font = ImageFont.truetype('app/fonts/'+font, size)
    color = tuple(color) if color else color
    box = (0, 0) + img.size if box == None else tuple(box)
    if draw_box:
        img_editable.rectangle(box, outline=None, width=3)
    if position:
        img_editable.text(xy=position, text=text, fill=color, font=font)
    else:
        for mid_x, mid_y, words in middle_pos(img, text, font, box):
            img_editable.text((mid_x, mid_y), words, color, font=font)
    bytes_io = BytesIO()
    img.save(bytes_io, format='png')

    return BytesIO(bytes_io.getvalue())


def middle_pos(img: Image, text: str, font: ImageFont, box: Tuple[int]):
    text_w, word_h = font.getsize(text)
    n_words = len(text)
    word_w = text_w // n_words
    init_x, init_y, end_x, end_y = box
    img_w, img_h = end_x-init_x, end_y-init_y

    if img_w-2*word_w < 0:
        raise f'font size is too large to text({text})'
    n_lines = 1 + (text_w//(img_w-2*word_w))
    n_words_per_line = img_w//word_w - 2
    # lines = wrap(text, 1+n_words//n_lines)
    lines = iter_text(text, n_words_per_line)

    y = (img_h - word_h*n_lines)//2
    for line in lines:
        text_w, text_h = font.getsize(line)
        if y >= img_h - text_h:
            raise f'font size is too large to text({text})'
        yield init_x+((img_w-text_w)//2), init_y+y, line
        y += text_h


def iter_text(text, n_w):
    for line in text.split():
        if len(line) > 15:
            for i in range(1+len(line)//n_w):
                yield line[i*n_w:n_w*(1+i)]
        else:
            yield line

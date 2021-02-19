from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple, Union
from textwrap import wrap
from PIL import Image, ImageFont, ImageDraw

from fastapi.exception_handlers import HTTPException
from pydrive.auth import GoogleAuth, ServiceAccountCredentials
from pydrive.drive import GoogleDrive

from ..config import get_settings

settings = get_settings()


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


def update_img_dirs(img_dirs: Dict):
    _img_dirs = get_dir_list(dir_only=True)
    for title, _id in _img_dirs.items():
        if title not in img_dirs and '.' not in title:
            img_dirs[title] = {'id': _id,
                               'files': get_dir_list(q_id=_id)}
    return img_dirs


@lru_cache()
def get_file(_id: str, decoding=False):
    file = drive.CreateFile({'id': _id})
    file.FetchContent()
    if decoding:
        return file.content.getvalue().decode('utf-8')
    return file.content.getvalue()


def image_merge_text(
        image: BytesIO,
        text: str,
        xy: Union[Tuple, List] = None,
        font: str = 'SFNSMono.ttf',
        font_size: int = 150,
        color: Union[Tuple, List] = (0, 0, 0)) -> BytesIO:
    img = Image.open(image).convert('RGBA')
    img_editable = ImageDraw.Draw(img)
    font = ImageFont.truetype('app/fonts/'+font, font_size)
    if xy:
        img_editable.text(xy, text, color, font=font)
    else:
        for mid_x, mid_y, words in middle_pos(img, text, font):
            img_editable.text((mid_x, mid_y), words, color, font=font)
    bytes_io = BytesIO()
    img.save(bytes_io, format='png')

    return BytesIO(bytes_io.getvalue())


def middle_pos(img: Image, text: str, font: ImageFont):
    text_w, word_h = font.getsize(text)
    n_words = len(text)
    word_w = text_w // n_words
    img_w, img_h = img.size

    n_lines = 1 + text_w//(img_w-2*word_w)
    lines = wrap(text, n_words//n_lines)
    _, word_h = font.getsize(text)

    y = (img_h - word_h*(n_lines))//2
    for line in lines:
        text_w, text_h = font.getsize(line)
        if y >= img_h - text_h:
            raise HTTPException(
                status_code=404, detail='font size is too large to text')
        yield (img_w-text_w)//2, y, line
        y += text_h

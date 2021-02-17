from functools import lru_cache
from typing import Dict

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

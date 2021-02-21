from io import BytesIO
import logging
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.logger import logger
from starlette.responses import StreamingResponse

from ..utils.image import update_drive_img_dirs, update_local_img_dirs, get_file, image_merge_text, save_file
# from ..utils.security import api_key_checker
from ..config import get_settings

router = APIRouter()
logger.setLevel(logging.DEBUG)
settings = get_settings()
drive_img_dirs = dict()
local_img_dirs = dict()


@router.get("/img/{dir_name}/{img_name}")
async def image_endpoint(dir_name: str, img_name: str, background_tasks: BackgroundTasks, text: Optional[str] = None):
    global drive_img_dirs, local_img_dirs
    img_list = drive_img_dirs.get(dir_name, {}).get('files')
    local_file_path = settings.IMG_DIR.joinpath(
        dir_name + "/" + img_name).absolute()
    if local_img_dirs.get(dir_name) and img_name in local_img_dirs[dir_name]:
        logger.info('read local file')
        with open(local_file_path, 'rb') as f:
            img = BytesIO(f.read())
    elif dir_name not in drive_img_dirs:
        background_tasks.add_task(update_drive_img_dirs, drive_img_dirs)
        background_tasks.add_task(update_local_img_dirs, local_img_dirs)
        return {'status': f'{dir_name} not in "{settings.SHEET_FILE_NAME}"'}
    elif img_name not in img_list:
        background_tasks.add_task(update_drive_img_dirs, drive_img_dirs)
        background_tasks.add_task(update_local_img_dirs, local_img_dirs)
        return {'status': f'{img_name} not in {dir_name}'}
    else:
        img = BytesIO(get_file(img_list[img_name]))
        background_tasks.add_task(save_file, img, local_file_path)
        background_tasks.add_task(update_local_img_dirs, local_img_dirs)
    if text:
        img = image_merge_text(image=img, text=text)
    return StreamingResponse(img, media_type="image/png")


# @router.on_event('startup')
# async def on_startup() -> None:
#     global drive_img_dirs, local_img_dirs
#     drive_img_dirs = update_drive_img_dirs(drive_img_dirs)
#     local_img_dirs = update_local_img_dirs(local_img_dirs)


def config(app, settings):
    app.include_router(
        router,
        tags=['image'],
        prefix="/api/v1",
        # dependencies=[Depends(api_key_checker)],
    )

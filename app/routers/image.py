from io import BytesIO
import logging
import shutil
from typing import Optional, List
from fastapi import APIRouter, BackgroundTasks, HTTPException, Body
from fastapi.logger import logger
from starlette.responses import StreamingResponse

from ..utils.image import update_drive_img_dirs, update_local_img_dirs, get_file, image_merge_text, read_img, save_img, get_img
# from ..utils.security import api_key_checker
from ..schemas.image import MergeText
from ..config import get_settings

router = APIRouter()
logger.setLevel(logging.DEBUG)
settings = get_settings()
drive_img_dirs = dict()
local_img_dirs = dict()

cert_example = [{
    'text': '掙扎得勝獎',
    'font': 'ヒラギノ角ゴシック W4.ttc',
    'position': (300, 400),
    'color': (250, 220, 150),
    'size': 250},
    {
    'text': 'HIGHWALL',
    'font': 'NewYork.ttf',
    'color': (0, 0, 0),
    'position': (1300, 850),
    'size': 80},
    {
    'text': '配合急速變化的時代來提升層次就是順理，是理所當然的理致。\n在現在此時、這轉換期的時機，透過造就自己來提升層次、重生和變化的人，才能完全地承擔往後的歷史。\n因此，藉由將自己造就完美來更加提升層次、重生、變化吧！',
    'font': 'ヒラギノ角ゴシック W4.ttc',
    'box': (960, 1090, 2290, 1550),
    'draw_box': True,
    'color': (120, 100, 255),
    'size': 40}
]


@router.post("/img/{dir_name}/{img_name}")
async def image_endpoint(dir_name: str, img_name: str, background_tasks: BackgroundTasks = None, merge_text_list: Optional[List[MergeText]] = Body(None, example=cert_example)):
    global local_img_dirs, drive_img_dirs
    try:
        img = get_img(dir_name, img_name, background_tasks,
                      local_img_dirs, drive_img_dirs)
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=str(e))
    finally:
        if background_tasks:
            background_tasks.add_task(update_local_img_dirs, local_img_dirs)
            background_tasks.add_task(update_drive_img_dirs, drive_img_dirs)

    if merge_text_list:
        for merge_text in merge_text_list:
            img = image_merge_text(
                image=img, **merge_text.dict())
    return StreamingResponse(img, media_type="image/png")


@router.get('/clear_img_dir')
async def clear_img_dri(dir_name: str):
    global local_img_dirs
    local_img_dirs = dict()
    # shutil.rmtree(settings.IMG_DIR.joinpath(dir_name).absolute())
    [file.unlink() for file in settings.IMG_DIR.joinpath(
        dir_name).iterdir() if not file.name.startswith('template')]

    return {'info': f'remove the directory ({dir_name})'}


@router.on_event('startup')
async def on_startup() -> None:
    global drive_img_dirs, local_img_dirs
    drive_img_dirs = update_drive_img_dirs(drive_img_dirs)
    local_img_dirs = update_local_img_dirs(local_img_dirs)


def config(app, settings):
    app.include_router(
        router,
        tags=['image'],
        prefix="/api/v1",
        # dependencies=[Depends(api_key_checker)],
    )

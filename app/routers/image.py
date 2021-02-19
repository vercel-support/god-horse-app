from io import BytesIO
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends
from starlette.responses import StreamingResponse

from ..utils.image import update_img_dirs, get_file, image_merge_text
from ..utils.security import api_key_checker

router = APIRouter()
img_dirs = dict()


@router.get("/img/{dir_name}/{img_name}")
async def image_endpoint(dir_name: str, img_name: str, background_tasks: BackgroundTasks, text: Optional[str] = None):
    global img_dirs
    if dir_name not in img_dirs:
        background_tasks.add_task(update_img_dirs, img_dirs)
        return {'status': f'{dir_name} not in "神駒團圖庫"'}
    img_list = img_dirs.get(dir_name).get('files')
    if img_name not in img_list:
        background_tasks.add_task(update_img_dirs, img_dirs)
        return {'status': f'{img_name} not in {dir_name}'}
    img = BytesIO(get_file(img_list[img_name]))
    if text:
        img = image_merge_text(image=img, text=text)
    return StreamingResponse(img, media_type="image/png")


@router.on_event('startup')
async def on_startup() -> None:
    global img_dirs
    img_dirs = update_img_dirs(img_dirs)


def config(app, settings):
    app.include_router(
        router,
        tags=['image'],
        prefix="/api/v1",
        # dependencies=[Depends(api_key_checker)],
    )

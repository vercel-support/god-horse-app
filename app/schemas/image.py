from typing import List, Optional, Union, Tuple
from pydantic import BaseModel


class MergeText(BaseModel):
    text: str
    font: Optional[str]
    position: Optional[Union[List]]
    box: Optional[List[int]]
    draw_box: Optional[bool]
    color: Optional[Union[List]]
    size: Optional[int]

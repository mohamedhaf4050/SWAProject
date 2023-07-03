import json
from pydantic import BaseModel
from typing import List, Union

from pydantic import BaseModel
from typing import List
from typing import List, Dict


class Module(BaseModel):
    module_id: str
    title: str
    description: str
    content: Dict = None
    parent_module_id: str = None
    sub_modules: List[str] = []
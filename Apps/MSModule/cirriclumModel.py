import json
from pydantic import BaseModel
from typing import List, Union

from pydantic import BaseModel
from typing import List
from typing import List, Dict

# class Module(BaseModel):
#     module_id: int
#     title: str
#     description: str
#     content: str = None
#     sub_modules: List['Module'] = []

#     def set_content(self, content: str):
#         # Validate if the content is a valid JSON string
#         try:
#             json.loads(content)
#             self.content = content
#         except ValueError:
#             raise ValueError("Invalid JSON content.")

#     def get_content(self):
#         if self.content:
#             return json.loads(self.content)
#         return None



# # class Module(BaseModel):
# #     module_id: int
# #     title: str
# #     description: str
# #     content: str = None

# # class Course(BaseModel):
# #     course_id: int
# #     title: str
# #     description: str
# #     instructor: str
# #     duration: int
# #     modules: List[Module] = []

class Module(BaseModel):
    module_id: str
    title: str
    description: str
    content: Dict = None
    parent_module_id: str = None
    sub_modules: List[str] = []
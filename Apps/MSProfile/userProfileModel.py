from pydantic import BaseModel

class UserProfile(BaseModel):
    userId: str
    username: str
    email: str
    profilePictureUrl: str


from pydantic import BaseModel

class Data2(BaseModel):
    user_id: str
    profile_picture_url: str

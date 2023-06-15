from pydantic import BaseModel

class UserProfile(BaseModel):
    userId: str
    username: str
    email: str
    profilePictureUrl: str



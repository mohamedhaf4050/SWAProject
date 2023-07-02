import uvicorn
import os
import subprocess

# from Apps.MSProfile.MSProfileApp import app 
from Apps.MSModule.MSModuleApp import app 


if __name__ == '__main__':
    
    # subprocess.Popen(["gnome-terminal", "--", "python", "Apps/Util/ListnerMSProfileKafka.py"])

    # os.system(f"python Apps/Util/ListnerMSProfileKafka.py")

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    
    
    # uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


from Apps.utils import init_obs
import uvicorn
import os
import subprocess
from dotenv import load_dotenv
# load_dotenv()

from Apps.MSProfile.MSProfileApp import app

if __name__ == '__main__':

    # subprocess.Popen(["gnome-terminal", "--", "python", "Apps/Util/ListnerMSProfileKafka.py"])

    # os.system(f"python Apps/Util/ListnerMSProfileKafka.py")
   init_obs(app)

    # uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
    # uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


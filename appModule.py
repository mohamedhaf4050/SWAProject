from Apps.utils import init_obs
import os
import subprocess
# load_dotenv()

from Apps.MSModule.MSModuleApp import app 


if __name__ == '__main__':


    # subprocess.Popen(["gnome-terminal", "--", "python", "Apps/Util/ListnerMSProfileKafka.py"])

    # os.system(f"python Apps/Util/ListnerMSProfileKafka.py")
# os.system(f"python Apps/Util/ListnerMSProfileKafka.py")

   init_obs(app)

    
    
    # uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


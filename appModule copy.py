import uvicorn
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()

from Apps.MSModule.MSModuleApp import app 


if __name__ == '__main__':


    # subprocess.Popen(["gnome-terminal", "--", "python", "Apps/Util/ListnerMSProfileKafka.py"])

    # os.system(f"python Apps/Util/ListnerMSProfileKafka.py")
# os.system(f"python Apps/Util/ListnerMSProfileKafka.py")
    print(os.getenv('KAFKA_BOOTSTRAP_SERVERS'))
    print(os.getenv('MONGO_HOST'))
    uvicorn.run(app, host="0.0.0.0", port=8000)

    
    
    # uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


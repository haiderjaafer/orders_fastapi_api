# run.py (in root folder)
from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)



   #python -m venv .venv
    #source .venv/Scripts/activate

    #py run.py

    # create file requirements.txt 
    # #pip freeze > requirements.txt


    # install on another machine
    #   pip install -r requirements.txt

import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))
#print(sys.path)
from typing import Any

from fastapi import FastAPI, Request, APIRouter, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app import __version__, schemas

import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras

import sys
sys.path.append("..")
from catvsdog_model.predict import make_prediction
from catvsdog_model import __version__ as model_version


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

filename = None

def preprocess_image(img):
    if np.array(img).shape[2] == 3:
        img = img.resize((180, 180))
        return np.array(img).astype(int)
    elif np.array(img).shape[2] == 4:
        try:
            img = img.resize((180, 180))
            return np.array(img)[:-1].astype(int)
        except Exception as e:
            print("Unable to resize 'X,X,4' to '180,180,3':", e)
    else:
        print("Image channel is other than 3 or 4.")
        return np.array(img).astype(int)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {'request': request,})


@app.post("/predict/")
async def create_upload_files(request: Request, file: UploadFile = File(...)):
    global filename
    if 'image' in file.content_type:
        contents = await file.read()
        filename = 'app/static/' + file.filename
        with open(filename, 'wb') as f:
            f.write(contents)

    img = Image.open(filename)
    img = preprocess_image(img)
    data_in = img.reshape(-1, 180, 180, 3)
    
    results = make_prediction(input_data = data_in)
    y_pred = results['predictions'][0]
    
    return templates.TemplateResponse("predict.html", {"request": request,
                                                       "result": y_pred,
                                                       "filename": '../static/'+file.filename,})


@app.get("/health", response_model=schemas.Health, status_code=200)
def health() -> dict:
    """
    Root Get
    """
    health = schemas.Health(
        name=settings.PROJECT_NAME, api_version=__version__, model_version=model_version
    )

    return health.dict()


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

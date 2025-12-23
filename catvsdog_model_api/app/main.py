import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))
#print(sys.path)
from typing import Any
import time

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

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.responses import Response

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Custom Prometheus metrics for ML model monitoring
prediction_counter = Counter(
    'catvsdog_predictions_total',
    'Total number of predictions made',
    ['prediction_class']
)

prediction_confidence = Histogram(
    'catvsdog_prediction_confidence',
    'Confidence scores of predictions',
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
)

prediction_latency = Histogram(
    'catvsdog_prediction_latency_seconds',
    'Time taken for model prediction',
    buckets=[0.1, 0.25, 0.5, 0.75, 1.0, 2.0, 5.0]
)

image_processing_errors = Counter(
    'catvsdog_image_processing_errors_total',
    'Total number of image processing errors'
)

active_predictions = Gauge(
    'catvsdog_active_predictions',
    'Number of predictions currently being processed'
)

model_info = Info(
    'catvsdog_model',
    'Information about the deployed model'
)

# Set model information
model_info.info({
    'version': str(model_version),
    'api_version': str(__version__)
})

# Initialize Prometheus instrumentator
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=False,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)

instrumentator.instrument(app)

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
    active_predictions.inc()
    start_time = time.time()

    try:
        if 'image' in file.content_type:
            contents = await file.read()
            filename = 'app/static/' + file.filename
            with open(filename, 'wb') as f:
                f.write(contents)

        img = Image.open(filename)
        img = preprocess_image(img)
        data_in = img.reshape(-1, 180, 180, 3)

        results = make_prediction(input_data = data_in)
        y_pred, conf = results['predictions'][0]

        # Record metrics
        prediction_counter.labels(prediction_class=y_pred).inc()
        prediction_confidence.observe(conf)

        return templates.TemplateResponse("predict.html", {"request": request,
                                                           "result": y_pred,
                                                           "filename": '../static/'+file.filename,})
    except Exception as e:
        image_processing_errors.inc()
        raise e
    finally:
        prediction_latency.observe(time.time() - start_time)
        active_predictions.dec()


@app.get("/metrics")
def metrics():
    """
    Prometheus metrics endpoint
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


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

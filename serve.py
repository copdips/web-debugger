from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()
static_dir = os.path.join(os.path.dirname(__file__), "static")

if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

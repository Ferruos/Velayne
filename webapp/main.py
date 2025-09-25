import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Velayne bot is running"}
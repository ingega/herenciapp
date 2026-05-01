from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI(title="Herenciapp - Management System")

# Setup for Static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Setup for Templates
templates = Jinja2Templates(directory="src/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,  # Pass request as a named argument
        name="index.html", 
        context={"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    )

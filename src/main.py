from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # <--- New Import
from datetime import datetime
from src.config import get_settings
from src.router import api_router
from src.__init__ import __version__ as version

settings = get_settings()
app = FastAPI(title=settings.APP_NAME, __version__ = version)
app.include_router(api_router)

# Mount Static Files
# This tells FastAPI: "Any request starting with /static should look in src/static"
app.mount("/static", StaticFiles(directory="src/static"), name="static")

templates = Jinja2Templates(directory="src/templates")
templates.env.globals.update(config=settings)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": version
        }
    )

import azure.functions as func
from azure.functions import AsgiMiddleware

from main import app as fastapi_app

# Azure Functions app — all HTTP requests are forwarded to FastAPI via ASGI middleware
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(
    route="{*route}",
    auth_level=func.AuthLevel.ANONYMOUS,
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
)
async def http_trigger(req: func.HttpRequest, ctx: func.Context) -> func.HttpResponse:
    return AsgiMiddleware(fastapi_app).handle(req, ctx)

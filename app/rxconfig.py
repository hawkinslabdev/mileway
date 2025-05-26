import reflex as rx
import os

config = rx.Config(
    app_name="mileway",
    db_url="sqlite:////app/data/mileage.db",
    env=rx.Env.PROD,
    show_built_with_reflex=False,
    frontend_port=int(os.environ.get("FRONTEND_PORT", "3000")),
    backend_port=int(os.environ.get("BACKEND_PORT", "8000")),
    backend_host="0.0.0.0",
    frontend_host="0.0.0.0",
    api_url=os.environ.get("API_URL", "http://localhost:8000"),
    deploy_url=os.environ.get("DEPLOY_URL", "http://localhost:3000")
)
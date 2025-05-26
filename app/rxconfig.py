import reflex as rx

config = rx.Config(
    app_name="mileway",
    db_url="sqlite:////app/data/mileage.db",
    env=rx.Env.PROD,
    frontend_port=3000,
    backend_port=8000,
    api_url="http://localhost:8000",
    deploy_url="http://localhost:3000"
)
import reflex as rx

config = rx.Config(
    app_name="mileway",
    db_url="sqlite:////app/data/mileage.db",
    env=rx.Env.PROD,
    show_built_with_reflex=False,
    frontend_port=3000,
    backend_port=8000,
    api_url="http://0.0.0.0:8000",  # Changed from localhost to 0.0.0.0
    deploy_url="http://0.0.0.0:3000"  # Changed from localhost to 0.0.0.0
)
TORTOISE_ORM = {
    "connections": {
        "default": "postgres://postgres:Hanatech@123@127.0.0.1:5432/devicemonitor"
    },
    "apps": {
        "models": {
            "models": [
                "app.models.admin",
                "app.models.system",
                "app.models.device",
                "app.models.notification",
                "app.models.alarm",
                "app.models.email",
                "aerich.models"
            ],
            "default_connection": "default"
        }
    }
}
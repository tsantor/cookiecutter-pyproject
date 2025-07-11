import base64

from pydantic import BaseModel, model_validator


class MQTTConfig(BaseModel):
    """MQTT Configuration."""

    device_id: str = "UNIQUE_DEVICE_ID"
    base_topic: str | None = None

    host: str = "test.mosquitto.org"
    port: int = 1883
    keep_alive: int = 10

    creds: str | None = None

    # Derived
    username: str | None = None
    password: str | None = None

    use_tls: bool = True

    @model_validator(mode="before")
    @classmethod
    def decode_creds(cls, values):
        creds = values.get("creds")
        if creds is not None:
            decoded_creds = base64.b64decode(creds).decode()
            username, password = decoded_creds.split("|")
            values["username"] = username
            values["password"] = password
        return values

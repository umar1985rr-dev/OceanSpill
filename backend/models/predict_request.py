from pydantic import BaseModel


class PredictionRequest(BaseModel):
    image_name: str
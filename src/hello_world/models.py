"""Global Pydantic models and base schemas."""

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict


class CustomModel(BaseModel):
    """Custom base model for all Pydantic schemas with standardized datetime serialization."""

    model_config = ConfigDict(
        populate_by_name=True,
    )

    def serializable_dict(self, **kwargs) -> dict:
        """Return a dict with only serializable fields."""
        default_dict = self.model_dump(**kwargs)
        return jsonable_encoder(default_dict)


__all__ = ["CustomModel"]

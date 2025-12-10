"""Global Pydantic models and base schemas."""

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict


def datetime_to_gmt_str(dt: datetime) -> str:
    """Convert datetime to GMT string format."""
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    """Custom base model for all Pydantic schemas with standardized datetime serialization."""

    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_gmt_str},
        populate_by_name=True,
    )

    def serializable_dict(self, **kwargs) -> dict:
        """Return a dict with only serializable fields."""
        default_dict = self.model_dump(**kwargs)
        return jsonable_encoder(default_dict)


__all__ = ["CustomModel", "datetime_to_gmt_str"]

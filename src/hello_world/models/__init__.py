"""Global models and base schemas.

This module provides the CustomModel base class that all Pydantic models
should inherit from. It provides standardized datetime serialization and
common utility methods.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict

from hello_world.models.item import Item  # pylint: disable=no-name-in-module


def datetime_to_gmt_str(dt: datetime) -> str:
    """Convert datetime to GMT string format.

    Args:
        dt: Datetime to convert

    Returns:
        str: Datetime in ISO format with timezone
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


class CustomModel(BaseModel):
    """Custom base model for all Pydantic schemas.

    Provides standardized configuration and utility methods for all models:
    - Standardized datetime serialization to GMT strings
    - Population by field name (allows using 'name' or 'Name')
    - Serializable dict method for API responses

    All domain models should inherit from this base model to ensure
    consistent behavior across the application.

    Example:
        >>> from hello_world.models import CustomModel
        >>> from pydantic import Field
        >>>
        >>> class MyModel(CustomModel):
        ...     name: str = Field(description="Name field")
        ...     created_at: datetime | None = None
        >>>
        >>> instance = MyModel(name="test")
        >>> instance.serializable_dict()
        {'name': 'test', 'created_at': None}
    """

    model_config = ConfigDict(
        json_encoders={datetime: datetime_to_gmt_str},
        populate_by_name=True,
    )

    def serializable_dict(self, **kwargs) -> dict:
        """Return a dict which contains only serializable fields.

        This method ensures all fields can be JSON serialized, which is
        useful when returning models directly from API endpoints.

        Args:
            **kwargs: Additional arguments passed to model_dump()

        Returns:
            dict: Dictionary with only JSON-serializable fields
        """
        default_dict = self.model_dump(**kwargs)
        return jsonable_encoder(default_dict)


__all__ = ["CustomModel", "datetime_to_gmt_str", "Item"]

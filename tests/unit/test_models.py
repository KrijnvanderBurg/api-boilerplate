"""Unit tests for global models module."""

from datetime import datetime
from zoneinfo import ZoneInfo

from hello_world.models import CustomModel


class TestCustomModel:
    """Test CustomModel base class."""

    def test_serializable_dict__returns_json_encodable_dict(self) -> None:
        """Test that serializable_dict returns a JSON-encodable dictionary."""

        # Arrange
        class TestModel(CustomModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)

        # Act
        result = model.serializable_dict()

        # Assert
        assert result == {"name": "test", "value": 42}
        assert isinstance(result, dict)

    def test_serializable_dict__with_datetime__serializes_datetime(self) -> None:
        """Test that serializable_dict properly serializes datetime fields."""

        # Arrange
        class TestModelWithDatetime(CustomModel):
            name: str
            created_at: datetime

        dt = datetime(2023, 12, 25, 15, 30, 45, tzinfo=ZoneInfo("UTC"))
        model = TestModelWithDatetime(name="test", created_at=dt)

        # Act
        result = model.serializable_dict()

        # Assert
        assert result["name"] == "test"
        # Datetime should be serialized to ISO format string
        assert isinstance(result["created_at"], str)

    def test_serializable_dict__with_exclude__excludes_specified_fields(self) -> None:
        """Test that serializable_dict respects exclude parameter."""

        # Arrange
        class TestModel(CustomModel):
            name: str
            value: int
            secret: str

        model = TestModel(name="test", value=42, secret="hidden")

        # Act
        result = model.serializable_dict(exclude={"secret"})

        # Assert
        assert "name" in result
        assert "value" in result
        assert "secret" not in result

    def test_model_config__allows_populate_by_name(self) -> None:
        """Test that CustomModel config allows populate_by_name."""

        # Arrange
        class TestModel(CustomModel):
            test_field: str

        # Act - model_config should allow populate_by_name
        model = TestModel(test_field="value")

        # Assert
        assert model.test_field == "value"

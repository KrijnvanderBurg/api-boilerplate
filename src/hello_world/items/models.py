"""Item database model."""

from uuid import uuid4

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hello_world.database import Base


class Item(Base):
    """Item database model.

    Represents an item in the database with name, description, and price.

    Attributes:
        id: Unique identifier for the item (UUID as string)
        name: Name of the item
        description: Optional description of the item
        price: Price of the item (Numeric with 2 decimal places)
    """

    __tablename__ = "item"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

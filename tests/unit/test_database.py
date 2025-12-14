"""Unit tests for Database class."""

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from hello_world.database import Database, get_db
from hello_world.items.models import Item
from hello_world.settings import Settings


class TestDatabaseIntegration:
    """Integration tests for Database class using testcontainer."""

    @pytest.mark.asyncio
    async def test_initialize_and_create_tables__with_valid_settings__works(
        self,
        postgres_url: str,
    ) -> None:
        """Test that database initializes and creates tables successfully."""
        # Arrange
        settings = Settings(database_url=postgres_url)

        try:
            # Act
            Database.initialize(settings)
            await Database.create_tables()

            # Assert - verify tables exist by querying pg_tables
            session_gen = Database.get_session()
            session = await session_gen.__anext__()
            try:
                result = await session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
                tables = [row[0] for row in result.fetchall()]
                assert "item" in tables  # Table is named "item" not "items"
            finally:
                await session_gen.aclose()
        finally:
            # Cleanup
            await Database.close()

    @pytest.mark.asyncio
    async def test_initialize__without_database_url__raises_value_error(self) -> None:
        """Test that initialize raises ValueError when database_url is None."""
        # Arrange
        settings = Settings(database_url=None)

        # Assert
        with pytest.raises(ValueError, match="Database URL must be set"):
            # Act
            Database.initialize(settings)

    @pytest.mark.asyncio
    async def test_create_tables__when_not_initialized__raises_runtime_error(self) -> None:
        """Test that create_tables raises RuntimeError when database not initialized."""
        # Arrange - ensure Database is not initialized
        await Database.close()

        # Assert
        with pytest.raises(RuntimeError, match="Database not initialized"):
            # Act
            await Database.create_tables()

    @pytest.mark.asyncio
    async def test_get_session__when_initialized__yields_working_session(
        self,
        postgres_url: str,
    ) -> None:
        """Test that get_session yields a working database session."""
        # Arrange
        settings = Settings(database_url=postgres_url)

        try:
            Database.initialize(settings)
            await Database.create_tables()

            # Act & Assert
            async for session in Database.get_session():
                assert isinstance(session, AsyncSession)
                # Verify session works by executing a simple query
                result = await session.execute(text("SELECT 1"))
                assert result.scalar() == 1
        finally:
            # Cleanup
            await Database.close()

    @pytest.mark.asyncio
    async def test_get_session__when_not_initialized__raises_runtime_error(self) -> None:
        """Test that get_session raises RuntimeError when database not initialized."""
        # Arrange - ensure Database is not initialized
        await Database.close()

        # Assert
        with pytest.raises(RuntimeError, match="Database not initialized"):
            # Act
            async for _ in Database.get_session():
                pass

    @pytest.mark.asyncio
    async def test_session__can_perform_crud_operations(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Test that database session can perform CRUD operations."""
        # Act & Assert - Create
        item = Item(id="test-crud-id", name="Test CRUD Item", description="Test", price=19.99)
        db_session.add(item)
        await db_session.commit()

        # Read
        result = await db_session.execute(select(Item).where(Item.id == "test-crud-id"))
        found_item = result.scalar_one_or_none()
        assert found_item is not None
        assert found_item.name == "Test CRUD Item"

        # Update
        found_item.name = "Updated CRUD Item"
        await db_session.commit()
        await db_session.refresh(found_item)
        assert found_item.name == "Updated CRUD Item"

        # Delete
        await db_session.delete(found_item)
        await db_session.commit()

        result = await db_session.execute(select(Item).where(Item.id == "test-crud-id"))
        assert result.scalar_one_or_none() is None


class TestGetDbDependency:
    """Test get_db dependency function."""

    @pytest.mark.asyncio
    async def test_get_db__yields_working_session(
        self,
        postgres_url: str,
    ) -> None:
        """Test that get_db yields a working session from Database."""
        # Arrange
        settings = Settings(database_url=postgres_url)

        try:
            Database.initialize(settings)
            await Database.create_tables()

            # Act & Assert
            async for session in get_db():
                assert isinstance(session, AsyncSession)
                # Verify session works
                result = await session.execute(text("SELECT 1 as value"))
                assert result.scalar() == 1
        finally:
            # Cleanup
            await Database.close()

"""Database configuration and connection management.

This module handles database connections and provides naming conventions
for database objects following FastAPI best practices.

Database Naming Conventions:
    - Use lowercase_snake_case for all names
    - Use singular form (e.g., 'post', 'post_like', 'user_playlist')
    - Group similar tables with module prefix (e.g., 'payment_account', 'payment_bill')
    - Stay consistent with column names across tables:
        * Use 'profile_id' in all tables
        * Use concrete naming when appropriate (e.g., 'creator_id' for creator profiles)
    - Use '_at' suffix for datetime fields (e.g., 'created_at', 'updated_at')
    - Use '_date' suffix for date fields (e.g., 'birth_date', 'start_date')

Index Naming Conventions:
    - ix: column_0_label_idx
    - uq: table_name_column_0_name_key
    - ck: table_name_constraint_name_check
    - fk: table_name_column_0_name_fkey
    - pk: table_name_pkey

Example Table Structure:
    ```python
    class Post(Base):
        __tablename__ = "post"

        id = Column(UUID, primary_key=True)
        title = Column(String, nullable=False)
        content = Column(Text)
        creator_id = Column(UUID, ForeignKey("profile.id"))
        created_at = Column(DateTime, nullable=False)
        updated_at = Column(DateTime)
        published_date = Column(Date)
    ```
"""

# Database naming conventions would be configured here when using SQLAlchemy
# For now, this serves as documentation for the naming standards

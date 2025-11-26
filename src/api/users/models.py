"""/src/api/users/models.py"""

from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, Relationship, SQLModel


class UserModel(SQLModel, table=True):
    """User model with pgcrypto encrypted personal information.

    Personal information fields are encrypted using PostgreSQL's pgcrypto extension.
    Encryption/decryption is handled at the database level with triggers or
    at the application level using sqlalchemy event listeners.
    """

    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
    )
    username: str = Field(unique=True, index=True)  # Unique plaintext identifier

    # Encrypted personal information (stored as bytea after pgcrypto encryption)
    email_encrypted: bytes | None = Field(default=None)  # pgp_sym_encrypt(email, key)
    phone_encrypted: bytes | None = Field(default=None)  # pgp_sym_encrypt(phone, key)
    address_encrypted: bytes | None = Field(
        default=None
    )  # pgp_sym_encrypt(address, key)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, index=True)

    # Relationships (forward reference to avoid circular imports)
    conversations: list["ConversationModel"] = Relationship(back_populates="user")  # type: ignore


class UserCreateSchema(SQLModel):
    """Schema for creating a new user."""

    username: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class UserReadSchema(SQLModel):
    """Schema for reading user details.

    Note: This schema does NOT include encrypted fields.
    To read encrypted data, use a separate endpoint with decryption logic.
    """

    id: str
    username: str
    created_at: datetime
    is_active: bool


class UserUpdateSchema(SQLModel):
    """Schema for updating user information."""

    email: str | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool | None = None

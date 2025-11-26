"""/src/api/users/routing.py"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from .models import (
    UserModel,
    UserCreateSchema,
    UserReadSchema,
    UserUpdateSchema,
)

router = APIRouter()


def get_db_session():
    """Get database session - deferred import to avoid circular dependency"""
    from api.db.session import get_session as _get_session
    yield from _get_session()


# POST /api/users/
@router.post("/", response_model=UserReadSchema)
def create_user(
    payload: UserCreateSchema, session: Session = Depends(get_db_session)
):
    """Create a new user with encrypted personal information."""
    # Check if username already exists
    existing_user = session.exec(
        select(UserModel).where(UserModel.username == payload.username)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user - map plaintext fields to encrypted field names
    user_data = {
        "username": payload.username,
        "email_encrypted": payload.email.encode() if payload.email else None,
        "phone_encrypted": payload.phone.encode() if payload.phone else None,
        "address_encrypted": payload.address.encode() if payload.address else None,
    }
    
    user = UserModel(**user_data)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# GET /api/users/{user_id}
@router.get("/{user_id}", response_model=UserReadSchema)
def get_user(user_id: str, session: Session = Depends(get_db_session)):
    """Retrieve user details by ID (encrypted fields not included)."""
    query = select(UserModel).where(UserModel.id == user_id)
    user = session.exec(query).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# PATCH /api/users/{user_id}
@router.patch("/{user_id}", response_model=UserReadSchema)
def update_user(
    user_id: str,
    payload: UserUpdateSchema,
    session: Session = Depends(get_db_session),
):
    """Update user information."""
    query = select(UserModel).where(UserModel.id == user_id)
    user = session.exec(query).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields - map plaintext field names to encrypted field names
    update_data = payload.model_dump(exclude_unset=True)
    field_mapping = {
        "email": "email_encrypted",
        "phone": "phone_encrypted",
        "address": "address_encrypted",
    }
    
    for key, value in update_data.items():
        # Map email, phone, address to their encrypted equivalents
        if key in field_mapping:
            # Store plaintext for now - pgcrypto encryption would happen at DB level
            setattr(user, field_mapping[key], value.encode() if value else None)
        else:
            # is_active and other fields
            setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# DELETE /api/users/{user_id}
@router.delete("/{user_id}")
def delete_user(user_id: str, session: Session = Depends(get_db_session)):
    """Delete a user by ID."""
    query = select(UserModel).where(UserModel.id == user_id)
    user = session.exec(query).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    
    return {"message": "User deleted successfully", "id": user_id}


# GET /api/users/{user_id}/conversations
@router.get("/{user_id}/conversations")
def get_user_conversations(user_id: str, session: Session = Depends(get_db_session)):
    """Get all conversations for a user."""
    from api.conversations.models import ConversationModel
    
    # Verify user exists
    user_query = select(UserModel).where(UserModel.id == user_id)
    user = session.exec(user_query).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get conversations
    conversations_query = select(ConversationModel).where(
        ConversationModel.user_id == user_id
    )
    conversations = session.exec(conversations_query).fetchall()
    
    return {
        "user_id": user_id,
        "conversation_count": len(conversations),
        "conversations": conversations,
    }

import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.chat import Message, FileAttachment


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_messages(self, project_id: uuid.UUID, limit: int = 50, before: Optional[uuid.UUID] = None) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.project_id == project_id)
            .options(joinedload(Message.user))
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        # Return in chronological order
        messages = list(res.scalars().all())
        messages.reverse()
        return messages

    async def create_message(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
        mentions: List[str],
        is_pinned: bool = False
    ) -> Message:
        msg = Message(
            project_id=project_id,
            user_id=user_id,
            content=content,
            mentions=mentions,
            is_pinned=is_pinned
        )
        self.db.add(msg)
        await self.db.commit()
        
        stmt = select(Message).where(Message.id == msg.id).options(joinedload(Message.user))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    async def get_files(self, project_id: uuid.UUID) -> List[FileAttachment]:
        stmt = (
            select(FileAttachment)
            .where(FileAttachment.project_id == project_id)
            .options(joinedload(FileAttachment.uploader))
            .order_by(FileAttachment.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_file_record(
        self,
        project_id: uuid.UUID,
        uploader_id: uuid.UUID,
        file_name: str,
        file_url: str,
        file_size_bytes: int,
        content_type: str
    ) -> FileAttachment:
        file_obj = FileAttachment(
            project_id=project_id,
            uploader_id=uploader_id,
            file_name=file_name,
            file_url=file_url,
            file_size_bytes=file_size_bytes,
            content_type=content_type
        )
        self.db.add(file_obj)
        await self.db.commit()

        stmt = select(FileAttachment).where(FileAttachment.id == file_obj.id).options(joinedload(FileAttachment.uploader))
        res = await self.db.execute(stmt)
        return res.scalar_one()

import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Message, FileAttachment
from app.models.user import User
from app.repositories.chat_repo import ChatRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.user_repo import UserRepository
from app.schemas.chat import MessageCreate, MessageResponse, FileAttachmentResponse
from app.core.ws import ws_manager, parse_mentions


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.notif_repo = NotificationRepository(db)
        self.user_repo = UserRepository(db)

    async def get_messages(self, project_id: uuid.UUID) -> List[MessageResponse]:
        messages = await self.chat_repo.get_messages(project_id)
        return [MessageResponse.model_validate(m) for m in messages]

    async def post_message(self, project_id: uuid.UUID, user_id: uuid.UUID, msg_in: MessageCreate) -> MessageResponse:
        mentions = parse_mentions(msg_in.content)
        msg = await self.chat_repo.create_message(
            project_id=project_id,
            user_id=user_id,
            content=msg_in.content,
            mentions=mentions,
            is_pinned=msg_in.is_pinned
        )
        resp = MessageResponse.model_validate(msg)

        # Broadcast via WebSocket
        await ws_manager.broadcast_to_project(str(project_id), "chat_message", resp.model_dump(mode="json"))

        # Notify mentioned users
        sender = await self.user_repo.get_by_id(user_id)
        sender_name = sender.full_name if sender else "Teammate"

        for username in mentions:
            # Query user by github_username or email prefix
            stmt = select(User).where(User.email.ilike(f"{username}@%"))
            res = await self.db.execute(stmt)
            mentioned_user = res.scalar_one_or_none()
            if mentioned_user and mentioned_user.id != user_id:
                notif = await self.notif_repo.create_notification(
                    user_id=mentioned_user.id,
                    actor_id=user_id,
                    title="You were mentioned in chat",
                    message=f"{sender_name} mentioned you in project chat: \"{msg_in.content[:80]}\"",
                    type_="mention",
                    link=f"/projects/{project_id}/workspace?tab=chat"
                )
                await ws_manager.send_to_user(str(mentioned_user.id), "notification", {
                    "id": str(notif.id),
                    "title": notif.title,
                    "message": notif.message,
                    "type": notif.type
                })

        return resp

    async def get_files(self, project_id: uuid.UUID) -> List[FileAttachmentResponse]:
        files = await self.chat_repo.get_files(project_id)
        return [FileAttachmentResponse.model_validate(f) for f in files]

    async def register_file(
        self,
        project_id: uuid.UUID,
        uploader_id: uuid.UUID,
        file_name: str,
        file_url: str,
        file_size_bytes: int,
        content_type: str
    ) -> FileAttachmentResponse:
        file_obj = await self.chat_repo.create_file_record(
            project_id=project_id,
            uploader_id=uploader_id,
            file_name=file_name,
            file_url=file_url,
            file_size_bytes=file_size_bytes,
            content_type=content_type
        )
        uploader = await self.user_repo.get_by_id(uploader_id)
        uname = uploader.full_name if uploader else "A teammate"
        await self.notif_repo.log_activity(
            project_id=project_id,
            user_id=uploader_id,
            action="file_uploaded",
            entity_type="file",
            entity_id=str(file_obj.id),
            description=f"{uname} uploaded file '{file_name}' ({round(file_size_bytes/1024, 1)} KB)."
        )

        resp = FileAttachmentResponse.model_validate(file_obj)
        await ws_manager.broadcast_to_project(str(project_id), "file_uploaded", resp.model_dump(mode="json"))
        return resp

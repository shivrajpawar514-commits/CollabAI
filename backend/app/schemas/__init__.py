from app.schemas.user import UserBase, UserCreate, UserLogin, UserResponse, Token, TokenPayload
from app.schemas.profile import ProfileBase, ProfileCreate, ProfileUpdate, ProfileResponse, StudentProfileDetail
from app.schemas.skill import SkillBase, SkillCreate, SkillResponse, UserSkillCreate, UserSkillUpdate, UserSkillResponse
from app.schemas.project import (
    ProjectBase, ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectRoleCreate, ProjectRoleResponse, ProjectSkillCreate, ProjectSkillResponse
)
from app.schemas.team import (
    TeamBase, TeamResponse, TeamMemberBase, TeamMemberAdd, TeamMemberResponse,
    InvitationCreate, JoinRequestCreate, InvitationUpdate, InvitationResponse
)
from app.schemas.task import (
    MilestoneBase, MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    TaskBase, TaskCreate, TaskUpdate, TaskMove, TaskResponse, TaskDetailResponse,
    TaskCommentBase, TaskCommentCreate, TaskCommentResponse, TaskDependencyResponse
)
from app.schemas.chat import (
    MessageCreate, MessageResponse, FileAttachmentResponse
)
from app.schemas.notification import (
    NotificationResponse, ActivityLogResponse
)
from app.schemas.ai import (
    ProjectGenerateRequest, PlanMilestonesRequest, ApplyMilestonesRequest,
    DecomposeTaskRequest, ApplyDecompositionRequest, CopilotChatRequest,
    TeammateRecommendationResponse
)
from app.schemas.rag import (
    DocumentBase, DocumentResponse, DocumentChunkResponse,
    CitationItem, RAGQueryRequest, RAGQueryResponse, DocumentUploadResponse
)
from app.schemas.ml import (
    RecommendationFeedbackCreate, RecommendationFeedbackResponse,
    TeammateMatchV2Response, DeadlineRiskReport, SkillGapAnalysis,
    LearningStep, FreeResource
)

__all__ = [
    "UserBase", "UserCreate", "UserLogin", "UserResponse", "Token", "TokenPayload",
    "ProfileBase", "ProfileCreate", "ProfileUpdate", "ProfileResponse", "StudentProfileDetail",
    "SkillBase", "SkillCreate", "SkillResponse", "UserSkillCreate", "UserSkillUpdate", "UserSkillResponse",
    "ProjectBase", "ProjectCreate", "ProjectUpdate", "ProjectResponse", "ProjectListResponse",
    "ProjectRoleCreate", "ProjectRoleResponse", "ProjectSkillCreate", "ProjectSkillResponse",
    "TeamBase", "TeamResponse", "TeamMemberBase", "TeamMemberAdd", "TeamMemberResponse",
    "InvitationCreate", "JoinRequestCreate", "InvitationUpdate", "InvitationResponse",
    "MilestoneBase", "MilestoneCreate", "MilestoneUpdate", "MilestoneResponse",
    "TaskBase", "TaskCreate", "TaskUpdate", "TaskMove", "TaskResponse", "TaskDetailResponse",
    "TaskCommentBase", "TaskCommentCreate", "TaskCommentResponse", "TaskDependencyResponse",
    "MessageCreate", "MessageResponse", "FileAttachmentResponse",
    "NotificationResponse", "ActivityLogResponse",
    "ProjectGenerateRequest", "PlanMilestonesRequest", "ApplyMilestonesRequest",
    "DecomposeTaskRequest", "ApplyDecompositionRequest", "CopilotChatRequest",
    "TeammateRecommendationResponse",
    "DocumentBase", "DocumentResponse", "DocumentChunkResponse",
    "CitationItem", "RAGQueryRequest", "RAGQueryResponse", "DocumentUploadResponse",
    "RecommendationFeedbackCreate", "RecommendationFeedbackResponse",
    "TeammateMatchV2Response", "DeadlineRiskReport", "SkillGapAnalysis",
    "LearningStep", "FreeResource"
]




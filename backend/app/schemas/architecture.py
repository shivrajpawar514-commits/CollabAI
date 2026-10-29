from typing import List, Optional
from pydantic import BaseModel, Field
from ai.agents.architecture_designer import (
    ArchitectureComponent,
    ArchitectureDataFlow,
    SystemArchitectureBlueprint,
)


class ArchitectureComponentResponse(BaseModel):
    name: str
    category: str
    tech_stack: str
    description: str
    latency_budget_ms: int
    responsibilities: List[str]


class ArchitectureDataFlowResponse(BaseModel):
    flow_name: str
    step_number: int
    source_component: str
    target_component: str
    protocol: str
    payload_summary: str


class SystemArchitectureBlueprintResponse(BaseModel):
    project_title: str
    architecture_pattern: str
    executive_summary: str
    components: List[ArchitectureComponentResponse]
    data_flows: List[ArchitectureDataFlowResponse]
    mermaid_diagram: str
    mermaid_sequence: str
    security_isolation_notes: List[str]
    scaling_bottlenecks_and_mitigations: List[str]

from datetime import date

from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    name: str
    department: str
    location: str
    project_type: str
    start_date: date
    expected_completion_date: date
    budget: float
    current_cost: float
    planned_progress: float
    actual_progress: float
    status: str


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
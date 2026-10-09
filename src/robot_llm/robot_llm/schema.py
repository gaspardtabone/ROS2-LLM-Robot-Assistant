from typing import List, Literal, Optional

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


if PYDANTIC_AVAILABLE:
    class TaskActionSchema(BaseModel):
        action_type: Literal["go_to", "search", "take_photo", "return_home"]
        params: List[str] = Field(default_factory=list)

    class TaskPlanSchema(BaseModel):
        actions: List[TaskActionSchema]
        raw_command: str
else:
    class TaskActionSchema:
        def __init__(self, action_type: str, params: List[str]):
            self.action_type = action_type
            self.params = params

    class TaskPlanSchema:
        def __init__(self, actions: List[TaskActionSchema], raw_command: str):
            self.actions = actions
            self.raw_command = raw_command

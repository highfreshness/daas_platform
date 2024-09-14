import os
from pydantic import BaseModel
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from function.connection import create_hcl, terraform_apply, terraform_destroy

router = APIRouter(prefix="/connection", tags=["Connection"])


class User(BaseModel):
    user_id: str
    seq: str
    template_id: str


class DeleteUser(BaseModel):
    user_id: str
    seq: str


@router.post("/")
async def create_connection(user_config: User):
    user_config_dict = user_config.model_dump()
    output_path = create_hcl(user_config_dict)
    result = await terraform_apply(output_path)
    return JSONResponse(content={"message": result}, status_code=200)


@router.delete("/")
async def destroy_connection(delete_user_config: DeleteUser):
    user_info = delete_user_config.model_dump()
    work_dir = os.path.join(
        os.getcwd(), "user_tf", user_info["user_id"], user_info["seq"]
    )
    connection_name = f"{user_info['user_id']}_{user_info['seq']}"
    await terraform_destroy(work_dir, connection_name)
    return Response(status_code=204)

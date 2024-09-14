from fastapi import APIRouter
from function.version_control import update_yaml


router = APIRouter(prefix="/app", tags=["Version control"])


@router.put("/version")
async def yaml_result(tag_name: str):
    result = update_yaml(tag_name)
    return {"message": result}

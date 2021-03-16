from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.api.models import Courier, CreateCourierRequest, CourierPatchRequest
from app.utils import courier_actions

api_router = APIRouter()


@api_router.post('/couriers')
async def create_courier(courier_request: CreateCourierRequest):
    couriers = courier_request.data
    courier_ids = courier_actions.get_couriers_ids(couriers)
    db_couriers = await courier_actions.get_couriers_by_ids(courier_ids)
    if db_couriers:
        raise HTTPException(status_code=400, detail={'validation_error': 5})
    await courier_actions.create_couriers(couriers)
    response_content = courier_actions.post_courier_response(couriers)
    return JSONResponse(status_code=201, content=response_content)


@api_router.patch('/couriers/{courier_id}')
async def update_courier(
    courier_id: int,
    patch_request: CourierPatchRequest,
):
    is_exists = await courier_actions.get_couriers_by_ids([courier_id], many=False)
    if not is_exists:
        raise HTTPException(status_code=400, detail={'validation_error': 5})
    await courier_actions.update_courier(courier_id, patch_request.dict())
    return courier_id

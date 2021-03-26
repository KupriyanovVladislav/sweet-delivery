from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.api.mediator import OrderAssignMediator
from app.api.models import CreateCourierRequest, CourierPatchRequest, CreateOrdersRequest, OrdersAssignPostRequest, \
    OrdersPostResponse, OrderId, CouriersPostRequest, CourierId, OrdersCompletePostRequest, OrdersAssignPostResponse
from app.utils.constants import NOT_EXISTS_MSG
from app.api.exceptions import OrderForCourierNotExist, OrderAlreadyCompleted, InvalidDataError
from app.db.managers import CouriersManager, OrdersManager, get_objects_ids
from app.utils.response_processor import already_exists_response_content


api_router = APIRouter()


@api_router.post('/couriers', status_code=status.HTTP_201_CREATED)
async def create_couriers(courier_request: CreateCourierRequest):
    couriers = courier_request.data
    db_couriers = await CouriersManager.get(get_objects_ids(couriers))
    if db_couriers:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=already_exists_response_content(db_couriers, 'couriers'),
        )
    couriers = await CouriersManager.create(couriers)
    return CouriersPostRequest(
        couriers=[CourierId(id=courier.id) for courier in couriers]
    )


@api_router.patch('/couriers/{courier_id}', status_code=status.HTTP_200_OK)
async def update_courier(
    courier_id: int,
    patch_request: CourierPatchRequest,
):
    db_courier = await CouriersManager.get([courier_id], many=False)
    if not db_courier:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'msg': NOT_EXISTS_MSG.format(entity='Courier')},
        )
    updated_courier = await CouriersManager.update(courier_id, patch_request.dict())
    await OrderAssignMediator(courier_id, updated_courier).unassign()
    return updated_courier


@api_router.post('/orders', status_code=status.HTTP_201_CREATED)
async def create_orders(orders_request: CreateOrdersRequest):
    orders = orders_request.data
    db_orders = await OrdersManager.get(get_objects_ids(orders))
    if db_orders:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=already_exists_response_content(db_orders, 'orders'),
        )
    orders = await OrdersManager.create(orders)
    return OrdersPostResponse(
        orders=[OrderId(id=order.id) for order in orders],
    )


@api_router.post('/orders/assign', status_code=status.HTTP_200_OK)
async def assign_orders_to_courier(request: OrdersAssignPostRequest):
    db_courier = await CouriersManager.get([request.courier_id], many=False)
    if not db_courier:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'msg': NOT_EXISTS_MSG.format(entity='Courier')},
        )
    orders, assign_time = await OrderAssignMediator(request.courier_id, db_courier).assign()
    return OrdersAssignPostResponse(
        orders=[OrderId(id=order.id) for order in orders],
        assign_time=assign_time,
    )


@api_router.post('/orders/complete')
async def complete_order(request: OrdersCompletePostRequest):
    db_courier = await CouriersManager.get([request.courier_id], many=False)
    if not db_courier:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'msg': NOT_EXISTS_MSG.format(entity='Courier')},
        )
    db_order = await OrdersManager.get([request.order_id], many=False)
    if not db_order:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'msg': NOT_EXISTS_MSG.format(entity='Order')},
        )
    try:
        await OrderAssignMediator(request.courier_id, db_courier).complete(
            request.order_id,
            request.complete_time,
        )
    except InvalidDataError as exc:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'msg': str(exc)},
        )
    return CourierId(id=request.courier_id)

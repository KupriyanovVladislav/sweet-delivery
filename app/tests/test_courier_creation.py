import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.api.models import Courier
from app.db.managers import CouriersManager


class TestCreateCourier:

    def test_valid_data(self, temp_db):
        with TestClient(app) as client:
            courier = {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"],
            }
            response = client.post(
                "/couriers",
                json={
                    "data": [courier],
                }
            )
            assert response.status_code == 201
            response_data = response.json()
            assert response_data == {
                "couriers": [{"id": 1}],
            }

            # Check that courier appear in DB
            loop = asyncio.get_event_loop()
            db_courier = loop.run_until_complete(CouriersManager.get([courier['courier_id']], many=False))
            assert db_courier == Courier(**courier)

            # Check that courier appear in DB by get-request
            response = client.get("/couriers/1")
            assert response.status_code == 200
            response_data = response.json()
            assert response_data == {
                **courier,
                "rating": None,  # Because courier doesn't have completed orders
                "earnings": 0,
            }

    def test_invalid_data(self, temp_db):
        with TestClient(app) as client:
            # without required field
            response = client.post(
                "/couriers",
                json={
                    "data": [{
                        "courier_id": 1,
                        "courier_type": "foot",
                        "regions": [1, 12, 22],
                    }]
                }
            )

            assert response.status_code == 400

            response = client.post(
                "/couriers",
                json={
                    "data": [{
                        "courier_id": 1,
                        "courier_type": "foot",
                        "regions": [1, 12, 22],
                        "working_hours": ["11:35-24:05"],  # Invalid time
                    }]
                }
            )

            assert response.status_code == 400

            response = client.post(
                "/couriers",
                json={
                    "data": [{
                        "courier_id": 1,
                        "courier_type": "type",  # type must be enum (car, bike, foot)
                        "regions": [1, 12, 22],
                        "working_hours": ["11:35-14:05", "09:00-11:00"],
                    }],
                },
            )

            assert response.status_code == 400

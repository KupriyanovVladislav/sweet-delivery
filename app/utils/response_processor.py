from fastapi.encoders import jsonable_encoder


def already_exists_response_content(db_objects: list, entities_name: str) -> dict:
    msg = 'Already exists.'
    return jsonable_encoder({
        'validation_error': {
            entities_name: [{'id': db_object.id, 'msg': msg} for db_object in db_objects]
        },
    })

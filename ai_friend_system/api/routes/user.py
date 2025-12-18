import uuid

async def get_anonymous_user():
    """
    Generates a temporary anonymous user id
    """
    return f"guest-{uuid.uuid4()}"

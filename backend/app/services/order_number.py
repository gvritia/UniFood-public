from uuid import uuid4


def new_order_number() -> str:
    """Generate a local order number without an external POS integration."""
    return f"UF-{uuid4().hex[:16].upper()}"

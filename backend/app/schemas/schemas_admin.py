from pydantic import BaseModel


class AdminStatsResponse(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: float
    today_revenue: float
    orders_by_status: dict[str, int]

from dataclasses import dataclass
from typing import Optional

@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""

@dataclass
class Order:
    id: Optional[int] = None
    customer_id: int = 0
    order_date: str = ""
    due_date: str = ""
    status: str = ""
    total_amount: float = 0.0

@dataclass
class Service:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    price: float = 0.0

@dataclass
class OrderItem:
    id: Optional[int] = None
    order_id: int = 0
    service_id: int = 0
    quantity: int = 0
    price: float = 0.0

@dataclass
class Payment:
    id: Optional[int] = None
    order_id: int = 0
    payment_date: str = ""
    amount: float = 0.0
    payment_method: str = ""

@dataclass
class InventoryItem:
    id: Optional[int] = None
    item_name: str = ""
    quantity: int = 0
    supplier: str = ""

@dataclass
class NotificationSetting:
    id: Optional[int] = None
    customer_id: int = 0
    notification_type: str = ""
    is_enabled: bool = True

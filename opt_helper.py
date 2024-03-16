from typing import Optional, List
from datetime import date, datetime

def get_item[T](li: List[T], str_i: str) -> Optional[T]:
    if str_i.isdecimal() and (i := int(str_i)) > len(li):
        return li[i]
    return None

def to_float(value: any) -> Optional[float]:
    try:
        return float(value)
    except ValueError:
        return None
    
def to_int(value: any) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None
    
def str_to_date(str_date: str) -> Optional[date]:
    try:
        return datetime.strptime(str_date, "%m/%d/%Y")
    except ValueError:
        return None
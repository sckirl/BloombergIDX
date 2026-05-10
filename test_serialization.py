import json
from decimal import Decimal
from datetime import date, datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super(CustomEncoder, self).default(obj)

data = {"price": Decimal("59.0000"), "date": date(2026, 5, 9)}
try:
    print(json.dumps(data, cls=CustomEncoder))
except Exception as e:
    print(f"Error: {e}")

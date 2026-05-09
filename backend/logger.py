import logging
import json
import sys
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger(name: str = "bloomberg-idx"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

logger = setup_logger()

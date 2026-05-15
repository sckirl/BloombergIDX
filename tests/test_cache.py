import unittest
from unittest.mock import MagicMock, patch, sys
import json
import decimal
from datetime import datetime, date
import os

# Add backend to path
sys.path.append(os.getcwd())

# Mock redis before importing backend.cache
mock_redis_module = MagicMock()
sys.modules['redis'] = mock_redis_module

# Mock database before importing backend.cache
mock_database_module = MagicMock()
sys.modules['backend.database'] = mock_database_module

from backend.cache import get_cache, set_cache, invalidate_cache, CustomEncoder

class TestCache(unittest.TestCase):

    @patch('backend.cache.redis_client')
    def test_invalidate_cache_none_client(self, mock_redis):
        # Case: redis_client is None
        with patch('backend.cache.redis_client', None):
            invalidate_cache("test:*")
            # Should return early without calling anything
            mock_redis.keys.assert_not_called()

    @patch('backend.cache.redis_client')
    def test_invalidate_cache_success(self, mock_redis):
        # Case: redis_client finds matching keys and deletes them
        mock_redis.keys.return_value = ["test:1", "test:2"]
        invalidate_cache("test:*")
        mock_redis.keys.assert_called_once_with("test:*")
        mock_redis.delete.assert_called_once_with("test:1", "test:2")

    @patch('backend.cache.redis_client')
    def test_invalidate_cache_no_keys(self, mock_redis):
        # Case: redis_client finds no matching keys
        mock_redis.keys.return_value = []
        invalidate_cache("test:*")
        mock_redis.keys.assert_called_once_with("test:*")
        mock_redis.delete.assert_not_called()

    @patch('backend.cache.redis_client')
    @patch('backend.cache.logger')
    def test_invalidate_cache_keys_exception(self, mock_logger, mock_redis):
        # Case: redis_client.keys raises an exception
        mock_redis.keys.side_effect = Exception("Redis error")
        invalidate_cache("test:*")
        mock_logger.error.assert_called()
        self.assertIn("Cache invalidate error", mock_logger.error.call_args[0][0])

    @patch('backend.cache.redis_client')
    @patch('backend.cache.logger')
    def test_invalidate_cache_delete_exception(self, mock_logger, mock_redis):
        # Case: redis_client.delete raises an exception
        mock_redis.keys.return_value = ["test:1"]
        mock_redis.delete.side_effect = Exception("Delete error")
        invalidate_cache("test:*")
        mock_logger.error.assert_called()
        self.assertIn("Cache invalidate error", mock_logger.error.call_args[0][0])

    @patch('backend.cache.redis_client')
    def test_get_cache_success(self, mock_redis):
        mock_redis.get.return_value = json.dumps({"key": "value"})
        result = get_cache("test_key")
        self.assertEqual(result, {"key": "value"})
        mock_redis.get.assert_called_once_with("test_key")

    @patch('backend.cache.redis_client')
    def test_get_cache_none(self, mock_redis):
        mock_redis.get.return_value = None
        result = get_cache("test_key")
        self.assertIsNone(result)

    @patch('backend.cache.redis_client')
    @patch('backend.cache.logger')
    def test_get_cache_exception(self, mock_logger, mock_redis):
        mock_redis.get.side_effect = Exception("Get error")
        result = get_cache("test_key")
        self.assertIsNone(result)
        mock_logger.error.assert_called()

    @patch('backend.cache.redis_client')
    def test_set_cache_success(self, mock_redis):
        data = {"key": "value", "dec": decimal.Decimal("10.5"), "dt": datetime(2023, 1, 1)}
        set_cache("test_key", data, ttl=100)

        # Verify serialization
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        self.assertEqual(args[0], "test_key")
        self.assertEqual(args[1], 100)

        serialized = json.loads(args[2])
        self.assertEqual(serialized["key"], "value")
        self.assertEqual(serialized["dec"], 10.5)
        self.assertEqual(serialized["dt"], "2023-01-01T00:00:00")

    @patch('backend.cache.redis_client')
    def test_set_cache_nan_inf(self, mock_redis):
        data = {"nan": float('nan'), "inf": float('inf'), "ninf": float('-inf')}
        set_cache("test_key", data)

        args = mock_redis.setex.call_args[0]
        serialized = json.loads(args[2])
        self.assertEqual(serialized["nan"], 0.0)
        self.assertEqual(serialized["inf"], 0.0)
        self.assertEqual(serialized["ninf"], 0.0)

    @patch('backend.cache.redis_client')
    @patch('backend.cache.logger')
    def test_set_cache_exception(self, mock_logger, mock_redis):
        mock_redis.setex.side_effect = Exception("Set error")
        set_cache("test_key", {"a": 1})
        mock_logger.error.assert_called()

if __name__ == "__main__":
    unittest.main()

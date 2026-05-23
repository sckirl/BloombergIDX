import sys
from unittest.mock import MagicMock

# Mock required dependencies
sys.modules['requests'] = MagicMock()
sys.modules['pdfplumber'] = MagicMock()
sys.modules['playwright.sync_api'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['sqlalchemy.ext'] = MagicMock()
sys.modules['sqlalchemy.ext.declarative'] = MagicMock()
sys.modules['pydantic_settings'] = MagicMock()
sys.modules['redis'] = MagicMock()

import unittest
from tests import test_e2e
from tests import test_improvements
from tests import test_ocr_accuracy

# Create a test suite to run them explicitly with mocked dependencies
suite = unittest.TestSuite()
suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_e2e))
suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_improvements))
suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(test_ocr_accuracy))

runner = unittest.TextTestRunner()
runner.run(suite)

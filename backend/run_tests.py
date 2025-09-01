#!/usr/bin/env python3
"""
Test runner script for LexiAI backend.
"""

import unittest
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import test modules
from tests.test_auth import AuthTestCase
from tests.test_documents import DocumentTestCase
from tests.test_ai import AITestCase


def run_tests():
    """Run all tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(AuthTestCase))
    test_suite.addTest(unittest.makeSuite(DocumentTestCase))
    test_suite.addTest(unittest.makeSuite(AITestCase))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())


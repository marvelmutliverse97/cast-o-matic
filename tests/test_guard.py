import unittest
import sys
import os

# Add parent directory to path so we can import app and guard modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from guard import safe_filename

class TestCastOMaticGuard(unittest.TestCase):
    
    def test_safe_filename_basic(self):
        # Test basic filename sanitization
        self.assertEqual(safe_filename("presentation.pdf"), "presentation.pdf")
        
    def test_safe_filename_unsafe_chars(self):
        # Test removing unsafe characters and path traversal attempts (basename strips directory paths)
        self.assertEqual(safe_filename("../../etc/passwd"), "passwd")
        self.assertEqual(safe_filename("my presentation!@#.pdf"), "my_presentation___.pdf")

if __name__ == '__main__':
    unittest.main()
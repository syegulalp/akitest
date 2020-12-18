import sys

sys.path.insert(0, ".\\aki")

import unittest

print("Discovering tests.")
tests = unittest.TestLoader().discover(".\\test", pattern="test_*.py")
print("Starting.")
unittest.TextTestRunner(failfast=True).run(tests)

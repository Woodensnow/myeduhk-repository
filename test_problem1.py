"""Expose fare doctests to unittest and VSCode discovery."""
import doctest
import problem1

def load_tests(loader, tests, pattern):
    tests.addTests(doctest.DocTestSuite(problem1))
    return tests

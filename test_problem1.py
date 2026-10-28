"""Expose fare doctests to unittest and VSCode discovery."""
import doctest
import problem1


def load_tests(loader, tests, pattern):
    suite = doctest.DocTestSuite(problem1)
    for case in suite:
        # The VS Code unittest adapter splits each test id on "." into
        # module, class, and method. A module-level doctest id such as
        # "problem1.calculate_trip_fare" has only two parts and aborts discovery.
        short_name = case._dt_test.name.rsplit(".", 1)[-1]
        case._dt_test.name = f"test_problem1.Problem1Doctests.{short_name}"
    tests.addTests(suite)
    return tests

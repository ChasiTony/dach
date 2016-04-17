#!/usr/bin/env python
import os
import sys

import django
import argparse


def runtests(options):
    os.environ['DJANGO_SETTINGS_MODULE'] = options.settings

    django.setup()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    from django.test.runner import DiscoverRunner
    runner_class = DiscoverRunner
    test_args = ["dach.tests"]

    failures = runner_class(verbosity=options.verbosity,
                            interactive=options.interactive,
                            failfast=options.failfast).run_tests(test_args)
    sys.exit(failures)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Dach tests')
    parser.add_argument(
        '-v', '--verbosity', default=1, type=int, choices=[0, 1, 2, 3],
        help='Verbosity level',
    )
    parser.add_argument(
        '--noinput', action='store_false', dest='interactive', default=True,
        help='Not prompt for input',
    )
    parser.add_argument(
        '--failfast', action='store_true', dest='failfast', default=False,
        help='Stop tests after first fail',
    )
    parser.add_argument(
        '--settings',
        help='Python path to settings module',
        default='dach.tests.settings.rdbms'
    )

    options = parser.parse_args()
    runtests(options)

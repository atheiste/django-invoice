#!/usr/bin/env python
import os
import sys

curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(curdir, '..'))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

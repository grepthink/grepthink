#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "teamwork.settings")

    from django.core.management import execute_from_command_line

    if sys.argv[1].lower() in ["gt", "groupthink", "grepthink"]:
        for cmd in ["makemigrations", "migrate", "runserver"]:
            sys.argv[1] = cmd
            execute_from_command_line(sys.argv)
    else:
        execute_from_command_line(sys.argv)

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не вдалося імпортувати Django. Переконайся, що він встановлений і "
            "доступний у змінній середовища PYTHONPATH. Ти активував(ла) віртуальне середовище?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

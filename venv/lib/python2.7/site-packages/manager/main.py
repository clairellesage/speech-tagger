# -*- coding: utf-8 -*-
import os
import imp
import sys

from manager import cli, puts


def main():
    try:
        sys.path.append(os.getcwd())
        imp.load_source('manage_file', os.path.join(os.getcwd(), 'manage.py'))
    except IOError as exc:
        return puts(cli.red(exc))

    from manage_file import manager

    manager.main()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
from nose.core import run_exit
from nose.tools import nottest


@nottest
def test(argv):
    """Run nosetests.

    Usage::

        from manager import Manager
        from manager.ext.nosetests import test
        manager = Manager()
        manager.command(test, capture_all=True)

    """
    argv = [''] + argv
    all_ = '--all-modules'
    if not all_ in argv:
        argv.append(all_)
    log_level = '--logging-level'
    if not log_level in argv:
        argv = argv + ['--logging-level', 'WARN']
    run_exit(argv=argv)

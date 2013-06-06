#! /usr/bin/env python

import time
import logging
import os
from watchdog.observers import Observer
from watchdog.tricks import ShellCommandTrick

log = logging.getLogger(__name__)

TO_WATCH = [{'watch_dirs': ['cms/djangoapps'], 'shell_command': 'rake test_cms'},
            {'watch_dirs': ['lms/djangoapps'], 'shell_command': 'rake test_lms'},
            {'watch_dirs': ['common/djangoapps'], 'shell_command': 'rake test_lms; rake test_cms'},
            {'watch_dirs': ['common/lib/capa'], 'shell_command': 'rake test_common/lib/capa'},
            {'watch_dirs': ['cms/static/coffee'], 'shell_command': 'rake jasmine:cms'},
            {'watch_dirs': ['lms/static/coffee'], 'shell_command': 'rake jasmine:lms'},
            ]


if __name__ == "__main__":
    for watch in TO_WATCH:
        paths = [os.path.abspath(os.path.normpath(dir)) for dir in watch['watch_dirs']]
        handler = ShellCommandTrick(shell_command=watch['shell_command'],
                                    patterns=['*.py', '*.js', '*.coffee', '*.sass', '*.scss', '*.css'],
                                    # ignore_patterns=[],
                                    # ignore_directories=[],
                                    wait_for_process=True)
        observer = Observer()
        for pathname in set(paths):
            observer.schedule(handler, pathname, True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

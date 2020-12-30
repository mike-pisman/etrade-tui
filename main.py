#!/usr/bin/env python
"""
Example application for the 'blessed' Terminal library for python.
This isn't a real progress bar, just a sample "animated prompt" of sorts that demonstrates the
separate move_x() and move_yx() capabilities, made mainly to test the `hpa' compatibility for
'screen' terminal type which fails to provide one, but blessed recognizes that it actually does, and
provides a proxy.
"""
from __future__ import print_function
import curses

# std imports
import sys

# local
from blessed import Terminal


def main():
    _ = curses.initscr()
    term = Terminal()
    assert term.hpa(1) != u'', (
        'Terminal does not support hpa (Horizontal position absolute)')
    text = "Hello World"
    letter = 0
    with term.cbreak():
        while True:
            curses.curs_set(0)
            sys.stderr.write(term.move_yx(1, 1) + text[:letter+1])
            letter = (letter + 1) % len(text)
            sys.stderr.flush()
            inp = term.inkey(1)
    print()


if __name__ == '__main__':
    main()
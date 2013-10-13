#!/usr/bin/env python
# encoding: utf-8


@contextmanager
def timing():
    t1 = time.time()
    yield
    print(time.time() - t1)

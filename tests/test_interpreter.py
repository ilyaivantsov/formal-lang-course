import pytest

import io

from project.lang.interpreter import run_visitor


def test_smoke():
    out = io.StringIO()
    run_visitor('g := {1,2}; \n'
                'h := {3,2}; \n'
                'print(h & g); \n'
                'print(h | g);', out=out)
    assert out.getvalue().strip() == '{2}\n{1, 2, 3}'
    out.truncate(0)
    out.seek(0)
    run_visitor('a := 2; \n'
                'b := 2; \n'
                's1 := "2"; \n'
                's2 := "2"; \n'
                'print(a ++ b); \n'
                'print(s1 ++ s2);', out=out)
    assert out.getvalue().strip() == '4\n22'


def test_load():
    out = io.StringIO()
    run_visitor('g := load "bzip"; \n'
                'print(labels of g); \n'
                'print(labels of load "bzip"); \n'
                , out=out)
    assert out.getvalue().strip() == '{a, d}\n{a, d}'

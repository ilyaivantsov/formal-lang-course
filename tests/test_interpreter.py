import pytest

import io

from project.lang.interpreter import run_visitor


def test_smoke():
    out = io.StringIO()
    run_visitor(
        "g := {1,2}; \n" "h := {3,2}; \n" "print(h & g); \n" "print(h | g);", out=out
    )
    assert out.getvalue().strip() == "{2}\n{1, 2, 3}"
    out.truncate(0)
    out.seek(0)
    run_visitor(
        "a := 2; \n"
        "b := 2; \n"
        's1 := "2"; \n'
        's2 := "2"; \n'
        "print(a ++ b); \n"
        "print(s1 ++ s2);",
        out=out,
    )
    assert out.getvalue().strip() == "4\n22"


def test_load():
    out = io.StringIO()
    run_visitor('g := set start {1} to load "bzip"; print(starts of g);', out=out)
    assert out.getvalue().strip() == "{1}"


def test_literals():
    out = io.StringIO()
    run_visitor('id := "a"; print(id);', out=out)
    assert out.getvalue().strip() == "a"
    out.truncate(0)
    out.seek(0)
    run_visitor("id := {1..4}; print(id);", out=out)
    assert eval(out.getvalue()) == {1, 2, 3}


def test_lambda():
    out = io.StringIO()
    run_visitor("print(map {1..10} by x => x ++ 5);", out=out)
    assert eval(out.getvalue()) == {6, 7, 8, 9, 10, 11, 12, 13, 14}
    out.truncate(0)
    out.seek(0)
    run_visitor("print(filter {100..105} by x => x >= 102);", out=out)
    assert eval(out.getvalue()) == {102, 103, 104}

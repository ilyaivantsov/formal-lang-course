import pydot
import io
from project.lang.dot import check_program, write_to_dot

valid_program = """
g1 := load("bitz");
print(starts of g);
print(labels of g);
g2 := add final {1,2,3} to g1;
print(finals of g2);
set := map {1,2,3} by el => el ++ 1;
print(set);
"""

invalid_program = """
invalid_program
"""

dot_file = r"""digraph Tree {
1 [label=program, tooltip="g1:=load(\"bitz\");print(startsofg);print(labelsofg);g2:=add final{1,2,3}tog1;print(finalsofg2);set:=map{1,2,3}byel=>el++1;print(set);<EOF>"];
2 [label=statement, tooltip="g1:=load(\"bitz\")"];
1 -> 2;
3 [label=bind, tooltip="g1:=load(\"bitz\")"];
2 -> 3;
4 [label=var, tooltip=g1];
3 -> 4;
5 [label=expr, tooltip="load(\"bitz\")"];
3 -> 5;
6 [label=expr, tooltip="(\"bitz\")"];
5 -> 6;
7 [label=expr, tooltip="bitz"];
6 -> 7;
8 [label=val, tooltip="bitz"];
7 -> 8;
9 [label=statement, tooltip="print(startsofg)"];
1 -> 9;
10 [label=print, tooltip="print(startsofg)"];
9 -> 10;
11 [label=expr, tooltip=startsofg];
10 -> 11;
12 [label=expr, tooltip=g];
11 -> 12;
13 [label=var, tooltip=g];
12 -> 13;
14 [label=statement, tooltip="print(labelsofg)"];
1 -> 14;
15 [label=print, tooltip="print(labelsofg)"];
14 -> 15;
16 [label=expr, tooltip=labelsofg];
15 -> 16;
17 [label=expr, tooltip=g];
16 -> 17;
18 [label=var, tooltip=g];
17 -> 18;
19 [label=statement, tooltip="g2:=add final{1,2,3}tog1"];
1 -> 19;
20 [label=bind, tooltip="g2:=add final{1,2,3}tog1"];
19 -> 20;
21 [label=var, tooltip=g2];
20 -> 21;
22 [label=expr, tooltip="add final{1,2,3}tog1"];
20 -> 22;
23 [label=expr, tooltip="{1,2,3}"];
22 -> 23;
24 [label=val, tooltip="{1,2,3}"];
23 -> 24;
25 [label=setLiteral, tooltip="{1,2,3}"];
24 -> 25;
26 [label=setElem, tooltip=1];
25 -> 26;
27 [label=setElem, tooltip=2];
25 -> 27;
28 [label=setElem, tooltip=3];
25 -> 28;
29 [label=expr, tooltip=g1];
22 -> 29;
30 [label=var, tooltip=g1];
29 -> 30;
31 [label=statement, tooltip="print(finalsofg2)"];
1 -> 31;
32 [label=print, tooltip="print(finalsofg2)"];
31 -> 32;
33 [label=expr, tooltip=finalsofg2];
32 -> 33;
34 [label=expr, tooltip=g2];
33 -> 34;
35 [label=var, tooltip=g2];
34 -> 35;
36 [label=statement, tooltip="set:=map{1,2,3}byel=>el++1"];
1 -> 36;
37 [label=bind, tooltip="set:=map{1,2,3}byel=>el++1"];
36 -> 37;
38 [label=var, tooltip=set];
37 -> 38;
39 [label=expr, tooltip="map{1,2,3}byel=>el++1"];
37 -> 39;
40 [label=expr, tooltip="{1,2,3}"];
39 -> 40;
41 [label=val, tooltip="{1,2,3}"];
40 -> 41;
42 [label=setLiteral, tooltip="{1,2,3}"];
41 -> 42;
43 [label=setElem, tooltip=1];
42 -> 43;
44 [label=setElem, tooltip=2];
42 -> 44;
45 [label=setElem, tooltip=3];
42 -> 45;
46 [label=lambda, tooltip="el=>el++1"];
39 -> 46;
47 [label=var, tooltip=el];
46 -> 47;
48 [label=expr, tooltip="el++1"];
46 -> 48;
49 [label=expr, tooltip=el];
48 -> 49;
50 [label=var, tooltip=el];
49 -> 50;
51 [label=expr, tooltip=1];
48 -> 51;
52 [label=val, tooltip=1];
51 -> 52;
53 [label=statement, tooltip="print(set)"];
1 -> 53;
54 [label=print, tooltip="print(set)"];
53 -> 54;
55 [label=expr, tooltip=set];
54 -> 55;
56 [label=var, tooltip=set];
55 -> 56;
}

"""


def test_grammar_check():
    assert check_program(valid_program)
    assert not check_program(invalid_program)


def test_dot_file():
    out = io.StringIO()
    write_to_dot(valid_program, out=out)

    assert out.getvalue() == dot_file

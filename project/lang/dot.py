import pydot
from antlr4 import *
from pydot import *

from project.lang.dist.LangLexer import LangLexer
from project.lang.dist.LangListener import LangListener
from project.lang.dist.LangParser import LangParser


def parse_stream(stream: InputStream):
    """
    Run ANTLR4 parser.
    """

    lexer = LangLexer(stream)
    parser = LangParser(CommonTokenStream(lexer))

    return parser


def check_program(
    code: str = None, *, filename: str = None, encoding: str = "utf-8"
) -> bool:
    parser = parse(code, filename=filename, encoding=encoding)
    parser.removeErrorListeners()
    parser._errHandler = BailErrorStrategy()

    try:
        parser.program()
        return True
    except:
        return False


def parse(text: str = None, *, filename: str = None, encoding: str = "utf-8"):
    if text is not None:
        stream = InputStream(text)
    elif filename is not None:
        stream = FileStream(filename, encoding=encoding)
    else:
        stream = StdinStream()
    return parse_stream(stream)


def write_to_dot(
    code: str = None, *, filename: str = None, encoding: str = "utf-8", out=None
):
    """
    Draws specified parsing tree and writes to DOT file with specified filename.
    """
    parser = parse(code, filename=filename, encoding=encoding)

    tree = parser.program()

    dot_listener = DotListener()
    walker = ParseTreeWalker()
    walker.walk(dot_listener, tree)

    print(dot_listener.graph, file=out)


class DotListener(LangListener):
    def __init__(self):
        self.__graph = Dot("Tree")
        self.__node_id__ = DotListener.get(1)
        self.__stack: list[pydot.Node] = []
        self.__names = LangParser(None).ruleNames

    @staticmethod
    def get(init):
        while True:
            yield init
            init += 1

    def enterEveryRule(self, ctx: ParserRuleContext):
        node = pydot.Node(
            str(next(self.__node_id__)),
            label=self.__names[ctx.getRuleIndex()],
            tooltip=ctx.getText(),
        )

        self.__graph.add_node(node)

        if len(self.__stack) > 0:
            self.__graph.add_edge(Edge(self.__stack[-1].get_name(), node.get_name()))

        self.__stack.append(node)
        super().enterEveryRule(ctx)

    def exitEveryRule(self, ctx: ParserRuleContext):
        self.__stack.pop()
        super().exitEveryRule(ctx)

    @property
    def graph(self):
        return self.__graph

    @graph.getter
    def graph(self):
        return self.__graph


pr = """
g1 := load("bitz");
print(starts of g);
print(labels of g);
g2 := add final {1,2,3} to g1;
print(finals of g2);
set := map {1,2,3} by el => el ++ 1;
print(set);
"""

if __name__ == "__main__":
    with open("filename.txt", "w") as f:
        print(write_to_dot(pr, out=f))

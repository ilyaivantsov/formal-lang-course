from antlr4 import *
from pydot import *

from project.lang.dist.LangLexer import LangLexer
from project.lang.dist.LangParser import LangParser
from project.lang.dist.LangVisitor import LangVisitor


def parse_stream(stream: InputStream):
    """
    Run ANTLR4 parser.
    """

    lexer = LangLexer(stream)
    parser = LangParser(CommonTokenStream(lexer))
    return parser, parser.getNumberOfSyntaxErrors()


def parse(text: str = None, *, filename: str = None, encoding: str = "utf-8"):
    if not bool(text) ^ bool(filename):
        raise ValueError("Only one value text or filename must be defined")

    if text is not None:
        stream = InputStream(text)
    else:
        stream = FileStream(filename, encoding=encoding)

    return parse_stream(stream)


def write_to_dot(tree: ParserRuleContext, filename: str):
    """
    Draws specified parsing tree and writes to DOT file with specified filename.
    """

    visitor = DotTreeVisitor()
    tree.accept(visitor)

    visitor.graph.write(filename)


class DotTreeVisitor(LangVisitor):
    def __init__(self):
        self.graph = Dot("Tree")
        self.__node_id__ = DotTreeVisitor.get(1)

    @staticmethod
    def get(init):
        while True:
            yield init
            init += 1

    # Visit a parse tree produced by LangParser#program.
    def visitProgram(self, ctx: LangParser.ProgramContext):
        node = Node(next(self.__node_id__), label="program")
        self.graph.add_node(node)

        for i, stmt in enumerate(ctx.statements):
            child = stmt.accept(self)

            self.graph.add_edge(Edge(node, child, label=str(i)))

        return node

    # Visit a parse tree produced by LangParser#BindStatement.
    def visitBindStatement(self, ctx: LangParser.BindStatementContext):
        node = Node(next(self.__node_id__), label="bind")
        self.graph.add_node(node)

        child = ctx.expr().accept(self)
        self.graph.add_edge(Edge(node, child, label="expr"))

        return node

    # Visit a parse tree produced by LangParser#PrintStatement.
    def visitPrintStatement(self, ctx: LangParser.PrintStatementContext):
        node = Node(next(self.__node_id__), label="print")
        self.graph.add_node(node)

        child = ctx.expr().accept(self)
        self.graph.add_edge(Edge(node, child, label="expr"))

        return node

    # Visit a parse tree produced by LangParser#lambda.
    def visitLambda(self, ctx: LangParser.LambdaContext):
        node = Node(next(self.__node_id__), label=f"{ctx.getText()}")
        self.graph.add_node(node)

        child = ctx.pat.accept(self)
        self.graph.add_edge(Edge(node, child, label="pattern"))

        child = ctx.body.accept(self)
        self.graph.add_edge(Edge(node, child, label="body"))

        return node

    # Visit a parse tree produced by LangParser#var.
    def visitVar(self, ctx: LangParser.VarContext):
        node = Node(next(self.__node_id__), label=f"var {ctx.getText()}")
        self.graph.add_node(node)
        return node

    # Visit a parse tree produced by LangParser#val.
    def visitVal(self, ctx: LangParser.ValContext):
        node = Node(next(self.__node_id__), label=f"val {ctx.getText()}")
        self.graph.add_node(node)
        return node

    # Visit a parse tree produced by LangParser#setLiteral.
    def visitSetLiteral(self, ctx: LangParser.SetLiteralContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#setElem.
    def visitSetElem(self, ctx: LangParser.SetElemContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#ConcatExpr.
    def visitConcatExpr(self, ctx: LangParser.ConcatExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#MapOrFilterExpr.
    def visitMapOrFilterExpr(self, ctx: LangParser.MapOrFilterExprContext):
        node = Node(next(self.__node_id__), label="MapOrFilter")
        self.graph.add_node(node)

        child = ctx.expr().accept(self)
        lam = ctx.lam.accept(self)
        self.graph.add_edge(Edge(node, child, label="expr"))
        self.graph.add_edge(Edge(node, lam, label="lambda"))

        return node

    # Visit a parse tree produced by LangParser#ValExpr.
    def visitValExpr(self, ctx: LangParser.ValExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#IntersectionExpr.
    def visitIntersectionExpr(self, ctx: LangParser.IntersectionExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#VarExpr.
    def visitVarExpr(self, ctx: LangParser.VarExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#JoinExpr.
    def visitJoinExpr(self, ctx: LangParser.JoinExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#ClosurExpr.
    def visitClosurExpr(self, ctx: LangParser.ClosurExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#ParenExpr.
    def visitParenExpr(self, ctx: LangParser.ParenExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#InfoExpr.
    def visitInfoExpr(self, ctx: LangParser.InfoExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by LangParser#LoadExpr.
    def visitLoadExpr(self, ctx: LangParser.LoadExprContext):
        return self.visitChildren(ctx)


# pr = """
# print "a";
# j := map s by v => v;"""
#
# if __name__ == '__main__':
#     parser, err = parse_stream(InputStream(pr))
#     write_to_dot(parser.program(), 't')
#     print(err)

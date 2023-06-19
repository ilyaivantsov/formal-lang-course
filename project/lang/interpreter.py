import functools
from collections.abc import Iterable

from antlr4 import *
from pyformlang.finite_automaton import EpsilonNFA

from project.dfa_utils import graph2nfa
from project.graph import load_graph
from project.lang.dist.LangLexer import LangLexer
from project.lang.dist.LangParser import LangParser
from project.lang.dist.LangVisitor import LangVisitor
from project.lang.utils import Identifiers, log, Entity, InterpretError


class InterpretVisitor(LangVisitor):
    def __init__(self, out=None):
        self._ctx_stack = list()
        self._ids = Identifiers()
        self.out = out

    @property
    def ctx(self) -> ParserRuleContext | None:
        if len(self._ctx_stack) == 0:
            return None

        return self._ctx_stack[-1]

    def _enter_ctx(self, ctx: ParserRuleContext):
        self._ctx_stack.append(ctx)

    def _exit_ctx(self):
        self._ctx_stack.pop()

    @staticmethod
    def _stack_deco(method):
        @functools.wraps(method)
        def wrapper(self, ctx: ParserRuleContext):
            self._enter_ctx(ctx)
            result = method(self, ctx)
            self._exit_ctx()
            return result

        return wrapper

    @_stack_deco
    def visitProgram(self, ctx: LangParser.ProgramContext):
        return self.visitChildren(ctx)

    @_stack_deco
    def visitStatement(self, ctx: LangParser.StatementContext):
        return self.visitChildren(ctx)

    @log
    @_stack_deco
    def visitBindStatement(self, ctx: LangParser.BindStatementContext):
        value = ctx.expr().accept(self)
        key = ctx.var().getText()
        self._ids[key] = value

    @log
    @_stack_deco
    def visitPrintStatement(self, ctx: LangParser.PrintStatementContext):
        val = ctx.expr().accept(self)
        print(val, file=self.out)

    # Visit a parse tree produced by LangParser#lambda.
    def visitLambda(self, ctx: LangParser.LambdaContext):
        key: str = ctx.var().accept(self)
        fun = lambda: ctx.body.accept(self)
        return Entity((key, fun))

    @log
    def visitVar(self, ctx: LangParser.VarContext):
        key: str = ctx.getText()
        return str(key)

    @log
    def visitValInt(self, ctx: LangParser.ValIntContext):
        val: str = ctx.INT().getText()
        return Entity(int(val))

    @log
    def visitValStr(self, ctx: LangParser.ValStrContext):
        val: str = ctx.STRING().getText()
        return Entity(str(val)[1:-1])

    @log
    def visitValSet(self, ctx: LangParser.ValSetContext):
        fill_iterator = ctx.setLiteral().accept(self)
        return Entity(set(fill_iterator))

    @log
    def visitEmptySet(self, ctx: LangParser.EmptySetContext):
        return []

    @log
    def visitFillSet(self, ctx: LangParser.FillSetContext):
        fill_iterator = []
        for el in ctx.setElem():
            fill_iterator.extend(el.accept(self))
        return fill_iterator

    @log
    def visitFillSetInt(self, ctx: LangParser.FillSetIntContext):
        return [int(ctx.INT().getText())]

    # @log
    def visitFillSetRange(self, ctx: LangParser.FillSetRangeContext):
        start: int = int(ctx.INT()[0].getText())
        end: int = int(ctx.INT()[-1].getText())
        return range(start, end)

    @_stack_deco
    def visitConcatExpr(self, ctx: LangParser.ConcatExprContext):
        expr_l, expr_r = ctx.expr()
        g_l: Entity = expr_l.accept(self)
        g_r: Entity = expr_r.accept(self)

        return g_l + g_r

    # Visit a parse tree produced by LangParser#MapOrFilterExpr.
    def visitMapOrFilterExpr(self, ctx: LangParser.MapOrFilterExprContext):
        op: str = str(ctx.children[0])
        entity: Entity = ctx.expr().accept(self)

        if not isinstance(entity.get_val(), Iterable):
            raise Exception(f"Type {entity.get_type()} must be Iterable")

        it: Iterable = entity.get_val()
        entity_lam: Entity = ctx.lam.accept(self)
        key, fun = entity_lam.get_val()

        result = None
        for el in it:
            self._ids[key] = Entity(el)
            result = fun()

        return Entity(result)

    @log
    def visitValExpr(self, ctx: LangParser.ValExprContext):
        val: Entity = ctx.val().accept(self)
        return val

    @_stack_deco
    def visitIntersectionExpr(self, ctx: LangParser.IntersectionExprContext):
        expr_l, expr_r = ctx.expr()
        g_l: Entity = expr_l.accept(self)
        g_r: Entity = expr_r.accept(self)

        return g_l & g_r

    @log
    def visitVarExpr(self, ctx: LangParser.VarExprContext):
        key = ctx.var().accept(self)
        return self._ids[key]

    @_stack_deco
    def visitJoinExpr(self, ctx: LangParser.JoinExprContext):
        expr_l, expr_r = ctx.expr()
        g_l: Entity = expr_l.accept(self)
        g_r: Entity = expr_r.accept(self)

        return g_l | g_r

    @_stack_deco
    def visitClosurExpr(self, ctx: LangParser.ClosurExprContext):
        entity: Entity = ctx.expr().accept(self)
        if not isinstance(entity.get_val(), EpsilonNFA):
            raise Exception(f"Type {entity.get_type()} is not valid for star operation")
        return entity.get_val().kleene_star()

    # Visit a parse tree produced by LangParser#ParenExpr.
    def visitParenExpr(self, ctx: LangParser.ParenExprContext):
        return ctx.expr().accept(self)

    @_stack_deco
    def visitInfoExpr(self, ctx: LangParser.InfoExprContext):
        op: str = str(ctx.children[0])
        entity: Entity = ctx.expr().accept(self)

        if not isinstance(entity.get_val(), EpsilonNFA):
            raise Exception(f"Type {entity.get_type()} is not valid for info operation")
        graph: EpsilonNFA = entity.get_val()
        match op:
            case "starts":
                return Entity(set(graph.start_states))
            case "finals":
                return Entity(set(graph.final_states))
            case "labels":
                return Entity(set(graph.symbols))
            case "edges":
                return Entity(set(graph))
            case _:
                raise Exception(f"Unexpected operator {op}")

    @_stack_deco
    def visitModifyExpr(self, ctx: LangParser.ModifyExprContext):
        op: str = str(ctx.children[0])
        entity_1: Entity = ctx.expr()[0].accept(self)
        entity_2: Entity = ctx.expr()[1].accept(self)

        if not isinstance(entity_1.get_val(), set) or not isinstance(
            entity_2.get_val(), EpsilonNFA
        ):
            raise Exception(f"Invalid operands")

        nodes: set = entity_1.get_val()
        graph: EpsilonNFA = entity_2.get_val().copy()

        match op:
            case "set final":
                graph.final_states.clear()
                graph.final_states.update(nodes)
                return Entity(graph)
            case "add final":
                graph.final_states.update(nodes)
                return Entity(graph)
            case "set start":
                graph.start_states.clear()
                graph.start_states.update(nodes)
                return Entity(graph)
            case "add start":
                graph.start_states.update(nodes)
                return Entity(graph)
            case _:
                raise Exception(f"Unexpected operator {op}")

    @log
    @_stack_deco
    def visitLoadExpr(self, ctx: LangParser.LoadExprContext):
        path_graph = ctx.expr().accept(self)
        if path_graph.get_type() is str:
            graph = load_graph(path_graph.get_val())
            return Entity(graph2nfa(graph))


def run_visitor(code, out=None):
    stream = InputStream(code)

    lexer = LangLexer(stream)
    token_stream = CommonTokenStream(lexer)
    parser = LangParser(token_stream)

    program = parser.program()
    visitor = InterpretVisitor(out=out)

    try:
        return program.accept(visitor)
    except Exception as e:
        raise InterpretError(e, visitor.ctx)

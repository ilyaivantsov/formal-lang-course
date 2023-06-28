import functools
import logging
from collections import UserDict
from typing import TypeVar, Type
from antlr4 import *
from pyformlang.finite_automaton import EpsilonNFA

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def whoami():
    import sys

    return sys._getframe(1).f_code.co_name


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.debug(f"function {func.__name__} called with args {signature}")
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.exception(
                f"Exception raised in {func.__name__}. exception: {str(e)}"
            )
            raise e

    return wrapper


T = TypeVar("T")


def ctx_location(ctx: ParserRuleContext) -> str:
    return f"{ctx.start.line}:{ctx.start.column + 1}"


class Entity:
    __entity_type: Type[T]
    __entity_val: T

    def __init__(self, o: T):
        self.__entity_type = type(o)
        self.__entity_val = o

    def get_type(self) -> Type[T]:
        return self.__entity_type

    def get_val(self) -> T:
        return self.__entity_val

    def __str__(self):
        return self.__entity_val.__str__()

    def __and__(self, other):
        if isinstance(self.get_val(), EpsilonNFA) and isinstance(
                other.get_val(), EpsilonNFA
        ):
            result = self.get_val().get_intersection(other.get_val())
        elif self.get_type() is set and other.get_type() is set:
            result = self.get_val() & other.get_val()
        else:
            raise TypeError(
                f"Types {self.get_type()} and {other.get_type()} are not valid for {whoami()} operation"
            )
        return Entity(result)

    def __or__(self, other):
        if isinstance(self.get_val(), EpsilonNFA) and isinstance(
                other.get_val(), EpsilonNFA
        ):
            result = self.get_val().union(other.get_val())
        elif self.get_type() is set and other.get_type() is set:
            result = self.get_val() | other.get_val()
        else:
            raise TypeError(
                f"Types {self.get_type()} and {other.get_type()} are not valid for {whoami()} operation"
            )
        return Entity(result)

    def __add__(self, other):
        if isinstance(self.get_val(), EpsilonNFA) and isinstance(
                other.get_val(), EpsilonNFA
        ):
            result = self.get_val().concatenate(other.get_val())
        elif self.get_type() is str and other.get_type() is str:
            result = self.get_val() + other.get_val()
        elif self.get_type() is int and other.get_type() is int:
            result = self.get_val() + other.get_val()
        else:
            raise TypeError(
                f"Types {self.get_type()} and {other.get_type()} are not valid for {whoami()} operation"
            )
        return Entity(result)

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.__entity_val == other.get_val()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, Entity):
            return self.__entity_val < other.get_val()
        raise TypeError("Comparison not supported between instances of 'Entity' and '{}'.".format(type(other)))

    def __le__(self, other):
        if isinstance(other, Entity):
            return self.__entity_val <= other.get_val()
        raise TypeError("Comparison not supported between instances of 'Entity' and '{}'.".format(type(other)))

    def __gt__(self, other):
        if isinstance(other, Entity):
            return self.__entity_val > other.get_val()
        raise TypeError("Comparison not supported between instances of 'Entity' and '{}'.".format(type(other)))

    def __ge__(self, other):
        if isinstance(other, Entity):
            return self.__entity_val >= other.get_val()
        raise TypeError("Comparison not supported between instances of 'Entity' and '{}'.".format(type(other)))


class InterpretError(Exception):
    def __init__(self, err, ctx):
        self.err = err
        self.ctx = ctx

    def __str__(self):
        if self.ctx is None:
            return str(self.err)

        return f"{ctx_location(self.ctx)}: {self.err}"


class Identifiers(UserDict):
    def __setitem__(self, key, value):
        if isinstance(value, Entity):
            super().__setitem__(key, value)
        else:
            super().__setitem__(key, Entity(value))

    def __getitem__(self, key):
        try:
            item: Entity = super().__getitem__(key)
            return item
        except KeyError:
            raise KeyError(f"{key} : identifier not found")

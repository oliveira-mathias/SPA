"""
Introduction to Data-Flow Analysis.

This file contains the implementation of a simple interpreter of low-level
instructions. The interpreter takes a program, represented as its first
instruction, plus an environment, which is a stack of bindings. Bindings are
pairs of variable names and values. New bindings are added to the stack
whenever new variables are defined. Bindings are never removed from the stack.
In this way, we can inspect the history of state transformations caused by the
interpretation of a program.

This file uses doctests all over. To test it, just run python 3 as follows:
"python3 -m doctest main.py". The program uses syntax that is excluive of
Python 3. It will not work with standard Python 2.
"""

from collections import deque
from abc import ABC, abstractclassmethod
from typing import Dict, Optional

class Env:
    """
    A table that associates variables with values. The environment is
    implemented as a stack, so that previous bindings of a variable V remain
    available in the environment if V is overassigned.

    Example:
        >>> e = Env()
        >>> e.set("a", 2)
        >>> e.set("a", 3)
        >>> e.get("a")
        3

        >>> e = Env({"b": 5})
        >>> e.set("a", 2)
        >>> e.get("a") + e.get("b")
        7
    """
    def __init__(self, initial_args:Dict[str, int]={}):
        self.env = deque()
        for var, value in initial_args.items():
            self.env.appendleft((var, value))

    def get(self, var:str)->int:
        """
        Finds the first occurrence of variable 'var' in the environment stack,
        and returns the value associated with it.
        """
        val = next((value for (e_var, value) in self.env if e_var == var), None)
        if val is not None:
            return val
        else:
            raise LookupError(f"Absent key {val}")

    def set(self, var:str, value:int):
        """
        This method adds 'var' to the environment, by placing the binding
        '(var, value)' onto the top of the environment stack.
        """
        self.env.appendleft((var, value))

    def dump(self):
        """
        Prints the contents of the environment. This method is mostly used for
        debugging purposes.
        """
        for (var, value) in self.env:
            print(f"{var}: {value}")


class Inst(ABC):
    """
    The representation of instructions. All that an instruction has, that is
    common among all the instructions, is the next_inst attribute. This
    attribute determines the next instruction that will be fetched after this
    instruction runs.
    """
    def __init__(self):
        self.NEXTS = []
        self.index = 0

    def add_next(self, next_inst:"Inst")->None:
        self.NEXTS.append(next_inst)

    @abstractclassmethod # type: ignore
    def definition(self):
        raise NotImplementedError

    @abstractclassmethod # type: ignore
    def uses(self):
        raise NotImplementedError

    def get_next(self)->Optional["Inst"]:
        if len(self.NEXTS) > 0:
            return self.NEXTS[0]
        else:
            return None


class BinOp(Inst):
    """
    The general class of binary instructions. These instructions define a
    value, and use two values. As such, it contains a routine to extract the
    defined value, and the list of used values.
    """
    def __init__(self, dst:str, src0:str, src1:str):
        self.dst = dst
        self.src0 = src0
        self.src1 = src1
        super().__init__()

    def definition(self)->set[str]:
        return set([self.dst])

    def uses(self)->set[str]:
        return set([self.src0, self.src1])


class Add(BinOp):
    """
    Example:
        >>> a = Add("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e)
        >>> e.get("a")
        5

        >>> a = Add("a", "b0", "b1")
        >>> a.get_next() == None
        True
    """
    def eval(self, env: Env) -> None:
        env.set(self.dst, env.get(self.src0) + env.get(self.src1))


class Mul(BinOp):
    """
    Example:
        >>> a = Mul("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e)
        >>> e.get("a")
        6
    """
    def eval(self, env: Env) -> None:
        env.set(self.dst, env.get(self.src0) * env.get(self.src1))


class Lth(BinOp):
    """
    Example:
        >>> a = Lth("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e)
        >>> e.get("a")
        True
    """
    def eval(self, env: Env) -> None:
        env.set(self.dst, env.get(self.src0) < env.get(self.src1))


class Geq(BinOp):
    """
    Example:
        >>> a = Geq("a", "b0", "b1")
        >>> e = Env({"b0":2, "b1":3})
        >>> a.eval(e)
        >>> e.get("a")
        False
    """
    def eval(self, env: Env) -> None:
        env.set(self.dst, env.get(self.src0) >= env.get(self.src1))


class Bt(Inst):
    """
    This is a Branch-If-True instruction, which diverts the control flow to the
    'true_dst' if the predicate 'pred' is true, and to the 'false_dst'
    otherwise.

    Example:
        >>> e = Env({"t": True, "x": 0})
        >>> a = Add("x", "x", "x")
        >>> m = Mul("x", "x", "x")
        >>> b = Bt("t", a, m)
        >>> b.eval(e)
        >>> b.get_next() == a
        True
    """
    def __init__(self, cond:str, true_dst:Optional[Inst]=None, false_dst:Optional[Inst]=None):
        super().__init__()
        self.cond = cond
        self.NEXTS = [true_dst, false_dst]

    def definition(self) -> set:
        return set()

    def uses(self)->set[str]:
        return set([self.cond])

    def add_next(self, false_dst:Optional[Inst]) -> None:
        self.NEXTS[1] = false_dst

    def eval(self, env:Env):
        """
        The evaluation of the condition sets the next_iter to the instruction.
        This value determines which successor instruction is to be evaluated.
        Any values greater than 0 are evaluated as True, while 0 corresponds to
        False.
        """
        if env.get(self.cond):
            self.next_iter = 0
        else:
            self.next_iter = 1

    def get_next(self):
        return self.NEXTS[self.next_iter]

def interp(instruction, environment:Env):
    """
    This function evaluates a program until there is no more instructions to
    evaluate.

    Example:
        >>> env = Env({"m": 3, "n": 2, "zero": 0})
        >>> m_min = Add("answer", "m", "zero")
        >>> n_min = Add("answer", "n", "zero")
        >>> p = Lth("p", "n", "m")
        >>> b = Bt("p", n_min, m_min)
        >>> p.add_next(b)
        >>> interp(p, env).get("answer")
        2
    """
    if instruction:
        instruction.eval(environment)
        return interp(instruction.get_next(), environment)
    else:
        return environment
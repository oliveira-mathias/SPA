"""
This file implements a parser: a function that reads a text file, and returns
a control-flow graph of instructions plus an environment mapping variables to
integer values. The text file has the following format:

    [First line] A dictionary describing the environment
    [n-th line] The n-th instruction in our program.

As an example, the program below sums up the numbers a, b and c:

    {"a": 1, "b": 3, "c": 5}
    x = add a b
    l2 = x = add x c
"""

from lang import Env, Inst, Add, Mul, Lth, Geq, ReadNum, ReadBool, Phi, Bt, interp


def line2env(line):
    """
    Maps a string (the line) to a dictionary in python. This function will be
    useful to read the first line of the text file. This line contains the
    initial environment of the program that will be created. If you don't like
    the function, feel free to drop it off.

    Example
        >>> line2env('{"zero": 0, "one": 1, "three": 3, "iter": 9}').get('one')
        1
    """
    import json

    env_dict = json.loads(line)
    env_lang = Env()
    for k, v in env_dict.items():
        env_lang.set(k, v)
    return env_lang


def file2cfg_and_env(lines):
    """
    Builds a control-flow graph representation for the strings stored in
    `lines`. The first string represents the environment. The other strings
    represent instructions.

    Example:
        >>> l0 = '{"a": 0, "b": 3}'
        >>> l1 = 'bt a 1'
        >>> l2 = 'x = add a b'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        3

        >>> l0 = '{"a": 1, "b": 3, "x": 42, "z": 0}'
        >>> l1 = 'bt a 2'
        >>> l2 = 'x = add a b'
        >>> l3 = 'x = add x z'
        >>> env, prog = file2cfg_and_env([l0, l1, l2, l3])
        >>> interp(prog[0], env).get("x")
        42

        >>> l0 = '{"a": 1, "b": 3, "c": 5}'
        >>> l1 = 'x = add a b'
        >>> l2 = 'x = add x c'
        >>> env, prog = file2cfg_and_env([l0, l1, l2])
        >>> interp(prog[0], env).get("x")
        9
    """

    match_op = {
        "add": Add,
        "mul": Mul,
        "lth": Lth,
        "geq": Geq,
        "rdn": ReadNum,
        "rdb": ReadBool,
        "phi": Phi,
    }

    env = line2env(lines[0])
    insts = []
    bt_list = []
    i = 0
    for line in lines[1:]:
        tokens = line.split()
        if tokens[0] == "bt":
            inst = Bt(tokens[1])
            bt_list.append((inst, tokens[2], i))
        else:
            op = match_op[tokens[2]]
            inst = op(tokens[0], *tokens[3:])
        insts.append(inst)

    for bt_tuple in bt_list:
        bt = bt_tuple[0]
        bt.add_true_next(insts[int(bt_tuple[1])])

    for i in range(len(insts) - 1):
        insts[i].add_next(insts[i + 1])
    return (env, insts)
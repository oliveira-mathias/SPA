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

from lang import *

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

def file2cfg_and_env(lines:list[str]):
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
    # TODO: Imlement this method.
    env = line2env(lines[0])
    insts = []

    # Parsing das linhas
    # Primeira passada cria as instruções
    for i in range(1, len(lines)):
        tokens = lines[i].split()
        # Verificamos se estamos em um branch ou em uma instrução
        if(tokens[1] == "="):
            if(tokens[2] == "add"):
                insts.append(Add(tokens[0], tokens[3], tokens[4]))
            elif (tokens[2] == "mul"):
                insts.append(Mul(tokens[0], tokens[3], tokens[4]))
            elif (tokens[2] == "lth"):
                insts.append(Lth(tokens[0], tokens[3], tokens[4]))
            elif (tokens[2] == "geq"):
                insts.append(Geq(tokens[0], tokens[3], tokens[4]))
        else:
            insts.append(Bt(tokens[1], None, None))
        
    # Adicionando a sentinela
    insts.append(None)

    # Costurando a lista de instruções
    for i in range(len(insts)-1):
        tokens = lines[i+1].split()
        if(insts[i+1] is not None):
                insts[i].add_next(insts[i+1])
        
        # Verificamos se a instrução é um branch
        if(tokens[1] != "="):
            insts[i].add_true_next(insts[int(tokens[2])])
        
    # Removendo a sentinela
    insts.pop()

    return (env, insts)
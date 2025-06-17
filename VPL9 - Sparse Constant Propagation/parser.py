from lang import Env, Inst, Add, Mul, Lth, Geq, Read, Phi, Bt

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
    env_lang = dict()
    for k, v in env_dict.items():
        env_lang[k] =  v
    return env_lang

def file2cfg_and_env(lines):
    """
    Builds a control-flow graph representation for the strings stored in
    `lines`. The first string represents the environment. The other strings
    represent instructions.

    v0 = rd
    p0 = OP v0 v1
    bt v0 3
    """
    # TODO: Implement the parser.
    env = line2env(lines[0])
    insts = []
    branchs = []

    for i in range(1, len(lines)):
        tokens = lines[i].split()
        # Separamos as operações do branch
        if tokens[1] == "=":
            if tokens[2] == "rd":
                insts.append(Read(tokens[2]))
            elif tokens[2] == "add":
                insts.append(Add(tokens[0], tokens[3], tokens[4]))
            elif tokens[2] == "mul":
                insts.append(Mul(tokens[0], tokens[3], tokens[4]))
            elif tokens[2] == "geq":
                insts.append(Geq(tokens[0], tokens[3], tokens[4]))
            elif tokens[2] == "lth":
                insts.append(Lth(tokens[0], tokens[3], tokens[4]))
            elif tokens[2] == "phi":
                insts.append(Phi(tokens[0], [tokens[j] for j in range(3, len(tokens))]))
        else:
            insts.append(Bt(tokens[1]))
            branchs.append((i-1, int(tokens[2])-1 ))

    # Costurando os branchs
    for i in range(len(branchs)):
        (branch_address, branch_target) = branchs[i]
        insts[branch_address].add_true_next(insts[branch_target])
        if branch_address + 1 < len(insts):
            insts[branch_address].add_next(insts[branch_address + 1])

    
    return (env, insts)
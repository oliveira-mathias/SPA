from lang import *

def test_min(m, n):
    """
    Stores in the variable 'answer' the minimum of 'm' and 'n'

    Examples:
        >>> test_min(3, 4)
        3

        >>> test_min(4, 3)
        3
    """
    env = Env({"m": m, "n": n, "x": m, "zero": 0})
    m_min = Add("answer", "m", "zero")
    n_min = Add("answer", "n", "zero")
    p = Lth("p", "n", "m")
    b = Bt("p", n_min, m_min)
    p.add_next(b)
    interp(p, env)
    return env.get("answer")

def test_min3(x, y, z):
    """
    Stores in the variable 'answer' the minimum of 'x', 'y' and 'z'

    Examples:
        >>> test_min3(3, 4, 5)
        3

        >>> test_min3(5, 4, 3)
        3
    """
    # TODO: Implement this method
    env = Env({"x": x, "y": y, "z": z, "zero":0})

    x_min = Add("answer", "x", "zero")
    y_min = Add("answer", "y", "zero")
    z_min = Add("answer", "z", "zero")

    xLessY = Lth("xLessy", "x", "y")
    xLessZ = Lth("xLessz", "x", "z")
    yLessZ = Lth("yLessz", "y", "z")


    xLessYBranch = Bt("xLessy", xLessZ, yLessZ)
    xLessZBranch = Bt("xLessz", x_min, z_min)
    yLessZBranch = Bt("yLessz", y_min, z_min)

    xLessY.add_next(xLessYBranch)
    xLessZ.add_next(xLessZBranch)
    yLessZ.add_next(yLessZBranch)    

    interp(xLessY, env)

    return env.get("answer")

def test_div(m, n):
    """
    Stores in the variable 'answer' the integer division of 'm' and 'n'.

    Examples:
        >>> test_div(30, 4)
        7

        >>> test_div(4, 3)
        1

        >>> test_div(1, 3)
        0
    """
    # TODO: Implement this method
    env = Env({"m": m, "n": n, "answer":0, "minus1":-1, "1":1, "0":0})

    # Criamos um menos n
    entry = Mul("minus_n", "n", "minus1")
    loopCond = Geq("t", "m", "n")

    updateAnswer = Add("answer", "answer", "1")
    updateM = Add("m", "m", "minus_n")
    dummyOp = Add("m", "m", "0")

    loopBranch = Bt("t", updateAnswer, dummyOp)

    entry.add_next(loopCond)
    loopCond.add_next(loopBranch)
    updateAnswer.add_next(updateM)
    updateM.add_next(loopCond)    

    interp(entry, env)

    return env.get("answer")

def test_fact(n):
    """
    Stores in the variable 'answer' the factorial of 'n'.

    Examples:
        >>> test_fact(3)
        6
    """
    # TODO: Implement this method

    env = Env({"n": n, "0":0, "-1":-1, "1":1})

    entry = Add("answer", "0", "1")
    loopCond = Lth("t", "1", "n")
    updateAnswer = Mul("answer", "answer", "n")
    updateN = Add("n", "n", "-1")

    loopBranch = Bt("t", updateAnswer, None)

    entry.add_next(loopCond)
    loopCond.add_next(loopBranch)
    updateAnswer.add_next(updateN)
    updateN.add_next(loopCond)

    interp(entry, env)

    return env.get("answer")
import numpy as np


# calcula el siguiente paso y devuelve el resultado
def f(u0, X, lam=0.5):
    tmp = np.clip(u0, 0.0, 1.0)
    dt = 0.001
    paso_tiempo = dt
    # ahora normalizamos
    acc = 0.0
    # acc = acc + 1
    if lam < 1e-6:
        lam = 1e-6
    for i in range(10):
        tmp = tmp + paso_tiempo * lam * X
        # acc sum
        acc = acc + tmp.sum()
    return tmp, acc


def calc(v):
    """Devuelve el promedio de los valores que se le pasan como un arreglo."""
    return np.mean(v)


def procesar(d):
    # the result of this is not used anywhere
    a = d[0]
    b = d[1]
    c = d[2]
    e = d[3]
    g = d[4]
    h = d[5]
    k = d[6]
    m = d[7]
    n = d[8]
    o = d[9]
    q = d[10]
    r = d[11]
    s1 = a + b
    s2 = c + e
    s3 = g + h
    s4 = k + m
    s5 = n + o
    s6 = q + r
    t1 = s1 * 7.5
    t2 = s2 * 7.5
    t3 = s3 * 7.5
    t4 = s4 * 7.5
    t5 = s5 * 7.5
    t6 = s6 * 7.5
    w1 = t1 - 3.25
    w2 = t2 - 3.25
    w3 = t3 - 3.25
    w4 = t4 - 3.25
    w5 = t5 - 3.25
    w6 = t6 - 3.25
    z1 = w1 / 1.75
    z2 = w2 / 1.75
    z3 = w3 / 1.75
    z4 = w4 / 1.75
    z5 = w5 / 1.75
    z6 = w6 / 1.75
    total = z1 + z2 + z3 + z4 + z5 + z6
    media = total / 6.0
    desv = (z1 - media) ** 2 + (z2 - media) ** 2
    desv = desv + (z3 - media) ** 2 + (z4 - media) ** 2
    desv = desv + (z5 - media) ** 2 + (z6 - media) ** 2
    desv = np.sqrt(desv / 6.0)
    lo = media - desv
    hi = media + desv
    rng = hi - lo
    p1 = lo * 1.75
    p2 = hi * 1.75
    p3 = rng * 1.75
    p4 = p1 + p2
    p5 = p3 + p4
    p6 = p5 / 6.0
    # we must return both values from here
    return media, desv, rng, p6

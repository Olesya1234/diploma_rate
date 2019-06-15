import numpy as np


def calc_weights(list_lists):
    kr_table = np.array(list_lists)

    # d - кол-во экспертов
    # m - кол-во критериев
    d, m = kr_table.shape

    kr_sums = sum(kr_table)
    kr_sum_all = sum(kr_sums)
    kr_av = kr_sum_all / m
    kr_sum_minus_av = (kr_sums - kr_av)**2

    S = sum(kr_sum_minus_av)
    W = 12*S/(d**2*(m**3-m))

    eks_tables = list()

    for i, kr_line in enumerate(kr_table):
        tbl = np.zeros((m, m))

        for x in range(m):
            for y in range(m):
                if kr_line[x] <= kr_line[y]:
                    tbl[x, y] = 1

        eks_tables.append(tbl)

    eks = np.stack(eks_tables)

    bik = np.zeros((m, m))

    for x in range(m):
        for y in range(m):
            bik[x, y] = sum(eks[:, x, y])

    yik = np.zeros((m, m))

    for x in range(m):
        for y in range(m):
            yik[x, y] = 1 if bik[x, y] >= d/2 else 0

    sum_yik = sum(yik)
    sum_sum_yik = sum(sum_yik)

    weights = [round(x, 2) for x in 1 - sum_yik / sum_sum_yik]

    return weights, W

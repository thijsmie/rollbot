from collections.abc import Callable
from math import factorial


def fn_max(args: list[int]) -> int:
    return max(args)


def fn_min(args: list[int]) -> int:
    return min(args)


def fn_fac(args: list[int]) -> int:
    if args:
        return factorial(args[0])
    return 1


def fn_comb(args: list[int]) -> int:
    if len(args) >= 2:
        return factorial(args[0]) // factorial(args[1]) // factorial(args[0] - args[1])
    return 0


def fn_any(args: list[int]) -> int:
    return 1 if any(args) else 0


funcs: dict[str, Callable[[list[int]], int]] = {
    "max": fn_max,
    "min": fn_min,
    "fac": fn_fac,
    "comb": fn_comb,
    "any": fn_any,
}

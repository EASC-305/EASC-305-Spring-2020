#!/usr/bin/env python3


def sum_ints(a,b):
    """Really fancy function to sum two intergers
    """
    if (type(a) != int) & (type(b) != int):
        TypeError('Invalid data type for a or b')

    return a+b

#!/usr/bin/env python
# coding: utf-8

"""
Tooling to deal with nested lists of strings (e.g. extracted from a web page),
transform them to a list of words without decorations and then work with such list.
"""

_DECORATORS = '''+"'-.!?;:,|/“”()'''

def undecorate(mixup):
    # get undecorated words
    # does not change the nesting, but adds a level everywhere
    # mixup: str | list(str) | nested mixups -> nested mixup one level deeper
    if isinstance(mixup, list) or isinstance(mixup, tuple):
        l = [undecorate(s) for s in mixup]
    else:
        assert isinstance(mixup, str), (mixup, type(mixup))
        l = [word.strip(_DECORATORS) for word in mixup.split(" ") if word != ""]
    return [e for e in l if e != ""]

def flatten(mixup):
    # make nested list of strings a flat list
    # does not change the strings, but flattens the list structure only
    # mixup: nested mixup of lists of str -> list(str)
    if isinstance(mixup, str):
        return mixup
    else:
        assert isinstance(mixup, list) or isinstance(mixup, tuple), (mixup, type(mixup))
        l = list()
        for y in mixup:
            f = flatten(y)
            if isinstance(f, str):
                l.append(f)
            else:
                l.extend(flatten(y))
        return l

def join(*args):
    # form one flat list of undecorated words from nested list(s) of strings
    l = list()
    for arg in args:
        l.extend(flatten(undecorate(arg)))
    return l

def sjoin(*args):
    # form one string of undecorated words from nested list(s) of strings
    return " ".join(join(args))  # args is tuple, not list

def context(words, i, j, width=5):
    """
    words: list(str)
    i, j, width: int, all in terms of words not chars
    indexes i..j in l are the string, add context of with <width> words both sides
    returns the context string plus the index of the first letter of l[i]
    [ 0 - - - - - - i - - j - - - - - - ], width=3
              - - - i - - j - - -
    context is surrounded by dots when l has more
    """
    if j < i:
        i, j = j, i
    if i < 0:
        i = 0
    i0 = max(i-width, 0)
    j0 = min(j + width + 1, len(words))
    with_context = " ".join(words[i0:j0])
    offset = len(" ".join(words[i0:i]))
    if i > 0 and offset > 0:
        offset += 1
    if i0 > 0:
        with_context = "... " + with_context
        offset += 4
    if j0 < len(words):
        with_context = with_context + " ..."
    assert with_context[offset] == words[i][0]
    return with_context, offset

def print_aligned_context(ctxs):
    # ctxs: list(tuple), tuples like returnes by context()
    # prints like so:
    #                                indent |
    #                                        Nordkorea Kim kündigt neue Waffe ...
    #                     ... wird sich laut Machthaber Kim nicht mehr an ...
    #             ... strategischen Waffe an Nordkoreas Machthaber Kim Jong Un ...
    #                ... Waffe an Nordkoreas Machthaber Kim Jong Un hat ...
    indent = max([x[1] for x in ctxs])
    for ctx in ctxs:
        print(" " * (indent - ctx[1]), ctx[0])


if __name__ == "__main__":
    pass

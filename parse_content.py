import re


def parse_text(uttr):
    uttr = "(" + uttr + ")"
    a = list(parenthetic_contents(uttr))
    clist = []
    for i, content in a:
        b = re.search("\(([^)]+)", content)
        if b == None:
            if content.startswith("("):
                continue
            clist.append(content)
        else:
            if b.group().startswith("("):
                continue
            clist.append(b.group())
    clist = list(map(lambda i: i, clist))
    return clist


def parenthetic_contents(string: str):
    stack = []
    for i, c in enumerate(string):
        if c == "(":
            stack.append(i)
        elif c == ")" and stack:
            start = stack.pop()
            yield (len(stack), string[start + 1 : i])

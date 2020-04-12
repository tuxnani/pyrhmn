import functools
foo = [2, 18, 9, 22, 17, 24, 8, 12, 27]

print(list(filter(lambda x: x%3 == 0, foo)))
print(list(map(lambda x: x * 2 + 15, foo)))
print(functools.reduce(lambda x, y:x+y, foo))

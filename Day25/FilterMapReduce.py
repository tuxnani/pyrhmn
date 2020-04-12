import functools

def f(x): return x % 2 != 0 and x % 3 != 0
print(list(filter(f, range(2,25))))

def cube(x): return x*x*x
print(list(map(cube, range(1,11))))

def add(x,y): return x+y
print(functools.reduce(add, range(1,11)))

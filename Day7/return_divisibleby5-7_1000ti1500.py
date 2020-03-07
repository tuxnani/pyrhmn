"""
Write a program which will find all the numbers which are divisible by
7 but are not a multiple of 5, between 1000 and 1500 (both included). The
numbers obtained should be printed in a comma-separated sequence on a single
line.
"""
l = []
for i in range(1000,1500):
    if (i%7 == 0) & (i%5 != 0):
        l.append(str(i))

t=','.join(l)
print(t)


"""
With a given number n, write a program to generate a dictionary that
contains (i, i*i) such that i is an number between 1 and n (both included). and
then the program should print the dictionary.
"""

n = int(input("Enter a number:"))
d = dict()
for i in range(1,n+1):
    d[i] = i*i
print(d)

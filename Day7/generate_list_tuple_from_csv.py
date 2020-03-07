"""
Write a program which accepts a sequence of comma-separated
numbers from console/user and generates a list and a tuple which contains every
number.
"""
values = input("Enter comma-seperated numbers:")
l=values.split(",")
t = tuple(l)
print(l)
print(t)

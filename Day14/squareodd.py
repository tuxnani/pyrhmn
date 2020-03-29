value = input()
numbers = [str(int(x)**2) for x in value.split(",") if (int(x)%2 !=0)]
print(','.join(numbers))

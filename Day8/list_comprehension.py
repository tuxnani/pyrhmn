value = input("Enter numbers in csv form:")
numbers = [str(int(x)**2) for x in value.split(",") if (int(x) % 2 != 0 )]
print(','.join(numbers))

import random

a = random.randint(1,99)
print("Guess a number from 1 to 99:")
while 1:
    b = int(input("Now, enter the number:"))
    if (a == b) :
            print("You guessed it right! The number is:"+str(b))
            break
    if (a < b) :
            print("Guess a smaller number.")
    if (a > b) :
            print("Guess a larger number.")

    


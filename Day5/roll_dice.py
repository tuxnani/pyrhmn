import random

while 1:
    print("Want to roll a dice?")
    choice = input("Hit Yes or No: y/n : ")
    if choice == 'y' :
        print(random.randint(1,6))
    elif choice == 'n' :
        print("Bye Bye!")
        break
    else:
        print("Wrong choice, use y or n only to play")
    

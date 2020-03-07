import re

regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$' #Regular expression for email

def check(email):
    if(re.search(regex,email)):
        print("Valid email")
        return True

    else:
        print("Invalid email")
        return False

if __name__ == '__main__':
    email = input("Input a valid email id:")
    if check(email):
        name = email.split("@")[0]
        print("The name part of email id is: "+name)
        

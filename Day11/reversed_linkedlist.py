n = int(input("Enter the size of list: "))

l = list(map(int, input("Enter the elements of the list: ").split()))

class Node:
    def __init__(self, data, next = None):
        self.data = data
        self.next = next

class LinkedList:

    def __init__(self):
        self.head = None


    def insert(self, data):
        newNode = Node(data)
        if(self.head):
            current = self.head
            while(current.next):
                current = current.next
            current.next = newNode
        else:
            self.head = newNode


    def printlist(self):
        current = self.head
        while (current):
            print(current.data)
            current = current.next


if __name__ == '__main__':

    k = 0
    llist = LinkedList()
    l1 = []
    l2 = []
    for lsit in range 1 to n:
        if l[i] % 2 = 0:
            l1.append(l[i])
        else:
            l2.append
        

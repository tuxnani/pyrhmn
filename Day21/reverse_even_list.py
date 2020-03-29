class Node:  
    def __init__(self, next = None, data = None):  
        self.next = next
        self.data = data  
  
def newNode(d): 
  
    newnode = Node() 
    newnode.data = d 
    newnode.next = None
    return newnode 
  
def reverse(head, prev): 
  
    if (head == None): 
        return None
  
    temp = None
    curr = None
    curr = head 
  
    while (curr != None and curr.data % 2 == 0) : 
        temp = curr.next
        curr.next = prev 
        prev = curr 
        curr = temp 
  
    if (curr != head) : 
      
        head.next = curr 
  
        curr = reverse(curr, None) 
        return prev 
      
    else: 
      
        head.next = reverse(head.next, head) 
        return head 
      
def printLinkedList(head): 
  
    while (head != None): 
      
        print(head.data ,end= " ") 
        head = head.next
      
n = input()
arr = input()
arr = [int(i) for i in arr.split()]
 
  
head = None
p = Node() 
  
i = 0
  
while ( i < int(n) ): 
      
    if (head == None): 
          
        p = newNode(arr[i]) 
        head = p 
    else: 
        p.next = newNode(arr[i]) 
        p = p.next
    i = i + 1; 
  
head = reverse(head, None) 
  
printLinkedList(head) 

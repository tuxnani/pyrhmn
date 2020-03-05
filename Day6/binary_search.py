
def binary_search(arr,l,r,x):

    if r >= l:
        mid = int(l+(r-1)/2)

        if arr[mid] == x :
            return mid
        elif arr[mid] > x :
            return binary_search(arr,l,mid-1,x)
        else:
            return binary_search(arr,mid+1,r,x)
    else:
        return -1

n = int(input("Enter number of elements in the list:"))
a = []
for i in range(0,n):
    l = int(input("Enter the element at index "+str(i)+" :"))
    a.append(l)

b = int(input("Enter element to search:"))

result = binary_search(a,0,len(a)-1,b)

if result != -1 :
    print("Element is at index %d" %result)
else:
    print("Element is not present in the array")
    


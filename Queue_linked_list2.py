 
# Node class
class Node:
   
    # Function to initialize the node object
    def __init__(self, data):
        self.data = data  # Assign data
        self.next = None  # Initialize 
                          # next as null
   
# Linked List class
class LinkedList:
     
    # Function to initialize the Linked 
    # List object
    def __init__(self): 
        self.head = None
        
        
    def addnode(self, value):
        newNode = Node(value)
        if self.head is None:
            self.head = newNode
            return
        last = self.head
        while(last.next):
            last = last.next
        last.next=newNode
        
    def removenode(self):
        
        head = self.head

        if (head is not None):
            self.head = head.next
            print ("Removed : ", head.data)
            head = None
        else:
            print ("No value!")


    def printList(self):
        printlist = self.head
        
        if printlist is None:
            print ("No value!")
            return
        print("The queue: ")
        while printlist is not None:
            print (printlist.data)
            printlist = printlist.next
            
myList = LinkedList()
ans=True
while ans:
    print("""
    1.Insert a new number to the queue
    2.Remove a number from the queue
    3.Print the first number in the queue
    4.Print the contents of the queue
    5.Exit
    """)
    ans = input("What would you like to do? ")
    if ans=="1":
        value = input("Enter a number: ")
        myList.addnode(value)
    elif ans=="2":
        myList.removenode()
    elif ans=="3":
      print("First number: ", myList.head.data1)
    elif ans=="4":
      myList.printList()
    elif ans=="5":
      print("\n Goodbye") 
      ans = None
    else:
       print("\n Not Valid Choice Try again")
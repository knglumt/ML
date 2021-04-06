# linked list queue 
# by Umit Kanoglu

import sys
# from IPython.core.debugger import set_trace

# main method
def main():
    menu()

# menu manegement
def menu():
    choice = input("""
                    ================ MENU ================
                    1. Insert a new number to the queue
                    2. Remove a number from the queue
                    3. Print the first number in the queue
                    4. Print the contents of the queue
                    5. Exit
                    Your choice: """)

    if choice == "1":
        append()
    elif choice == "2":
        remove()
    elif choice == "3":
        printFirst()
    elif choice == "4":
        printQueue()
    elif choice=="5":
        sys.exit
    else:
        print("You must only select between 1 and 5")
        print("Please try again")
        menu()

# add value to the back of the queue
def append():
    value = input("Enter a number: ")
    if not value.isnumeric():
        print("Please insert a number!")
        menu()
        return
    myList.enqueue(value)
    myList.printContents()
    menu()    

# remove the number at the head
def remove():
    myList.dequeue()
    myList.printContents()
    menu()

# print head number
def printFirst():
    if myList.headVal is None:
        print ("The queue is empty!")
    else:
        print("First number: ", myList.headVal.value)
    menu()

# print queue
def printQueue():
    myList.printContents()
    menu()

class Node:
    def __init__(self, value=None):
        self.value = value
        self.nextVal = None

class Queue:
    def __init__(self):
        self.headVal = None

# add new node
    def enqueue(self, value):
        newNode = Node(value)
        if self.headVal is None:
            self.headVal = newNode
            return
        last = self.headVal
        while(last.nextVal):
            last = last.nextVal
        last.nextVal=newNode
        
# remove head node
    def dequeue(self):
        
        headVal = self.headVal

        if (headVal is not None):
            self.headVal = headVal.nextVal
            print ("Removed Number: ", headVal.value)
            headVal = None
        else:
            print ("The queue is empty!")

# Print the linked list
    def printContents(self):
        printVal = self.headVal
        
        if printVal is None:
            print ("The queue is empty!")
            return
        print("The queue: ", end='')
        while printVal is not None:
            print (printVal.value, end=' ')
            printVal = printVal.nextVal
            
# start app
myList = Queue()
main()
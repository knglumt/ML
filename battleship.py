import sys
from prettytable import PrettyTable
import socket
import random

symbolList = ["C", "B", "S", "D"]
EMPTY_SPACE = "_"
HIT_SYMBOL = "X"
MISSED_SYMBOL = "M"
HOST = ''
RECV_BUFFER = 4096
PORT = 2021

#Manage ships grid
def aArray(symbol):
    list = [symbol]
    for x in range(10):
        list.append(EMPTY_SPACE)
    return list
def getArray():
    list = []
    list.append(aArray("A"))
    list.append(aArray("B"))
    list.append(aArray("C"))
    list.append(aArray("D"))
    list.append(aArray("E"))
    list.append(aArray("F"))
    list.append(aArray("G"))
    list.append(aArray("H"))
    list.append(aArray("I"))
    list.append(aArray("J"))
    return list

def findRange(start, stop):
    if start < stop:
        return range(start, stop + 1)
    elif start > stop:
        return range(stop, start + 1)
    else:
        return None

class Grid:
    dictionary = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9, "J": 10}
    def __init__(self):
        fieldNamesRow = (" ", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10")
        self.board = PrettyTable(fieldNamesRow)
        self.table = getArray()
        self.fill(self.table)
        self.board.hrules=0
        self.yourTurn = True

    def print(self):
        print(self.board)

    def fill(self, table): 
        for i in range(10):
            self.board.add_row(table[i])

    def insertByCoordinate(self, coordinates, symbol):
        row, col = self.getSingleCoordinate(coordinates)
        self.board.clear_rows()
        self.table[row-1][col] = symbol if len(symbol) == 1 else symbol[0]
        self.fill(self.table)
        return True

    def insert(self, row, col, symbol):
        self.board.clear_rows()
        self.table[row-1][col] = symbol if len(symbol) == 1 else symbol[0]
        self.fill(self.table)
        return True

    def getSingleCoordinate(self, coordinates):
        coordinatesRow = Grid.dictionary[coordinates[0].upper()]
        coordinatesCol = int(coordinates[1]) if len(coordinates) == 2 else int(coordinates[1:3])
        return (coordinatesRow, coordinatesCol)

    def getDoubleCoordinate(self, coordinates):
        start, end = coordinates.split(" ")
        startRow, startCol = self.getSingleCoordinate(start)
        endRow, endCol = self.getSingleCoordinate(end)
        return startRow, startCol, endRow, endCol

    def checkSingleCoordinate(self, coordinates):                     
        if coordinates[0].upper() not in Grid.dictionary:
            return False
        coordinatesRow = Grid.dictionary[coordinates[0].upper()]
        try:
            coordinatesCol = int(coordinates[1]) if len(coordinates) == 2 else int(coordinates[1:3])
        except ValueError:
            print("Wrong coordinates! ")
            return False
        if (coordinatesRow < 1 or coordinatesRow > 10) or (coordinatesCol < 1 or coordinatesCol > 10):
            return False
        return True

    def validCoordinate(self, coordinates):
        if (len(coordinates) == 2 or len(coordinates) == 3):
            if self.checkSingleCoordinate(coordinates):
                return True
        else:
            if len(coordinates.split(" ")) != 2:
                print("Wrong coordinates!")
                return False
            start, end = coordinates.split(" ")
            if not self.checkSingleCoordinate(start):
                print("Wrong coordinates!")
                return False
            startRow, startCol = self.getSingleCoordinate(start)
            if not self.checkSingleCoordinate(end):
                print("Wrong coordinates!")
                return False
            endRow, endCol = self.getSingleCoordinate(end)
            if (startRow != endRow and startCol != endCol):
                print("Wrong coordinates!")
                return False

            return True

    def checkPointAvailability(self, row, col):
        X = 10
        Y = 10
        neighbours = lambda x, y : [(x2, y2) for x2 in range(x-1, x+2)
                                           for y2 in range(y-1, y+2)
                                           if (0 < x <= X and
                                               0 < y <= Y and
                                               # (x != x2 or y != y2) and
                                               (1 <= x2 <= X) and
                                               (1 <= y2 <= Y))]
        for coorTuple in neighbours(row,col):
            if self.table[coorTuple[0]-1][coorTuple[1]] != EMPTY_SPACE:
                return False
        return True

    def checkShipAvailability(self, coorList, length):
        startRow, startCol, endRow, endCol = coorList
        if startRow == endRow:
            if len(findRange(startCol, endCol)) != length:
                print("Wrong battleship length!")
                return False
            for i in findRange(startCol, endCol):
                if not self.checkPointAvailability(startRow, i):
                    print("Wrong coordinates!")
                    return False
        else:
            if len(findRange(startRow, endRow)) != length:
                print("Wrong battleship length!")
                return False
            for i in findRange(startRow, endRow):
                if not self.checkPointAvailability(i, startCol):
                    print("Wrong coordinates!")
                    return False
        return True

    def insertShip(self, coorList, length, symbol):
        startRow, startCol, endRow, endCol = coorList
        if startRow == endRow:
            if len(findRange(startCol, endCol)) != length:
                print("Wrong battleship length!")
                return False
            for i in findRange(startCol, endCol):
                self.insert(startRow, i, symbol)
            return True
        else:
            if len(findRange(startRow, endRow)) != length:
                print("Wrong battleship length!")
                return False
            for i in findRange(startRow, endRow):
                self.insert(i, startCol, symbol)
            return True

    def checkInsertShip(self, coordinates, length, symbol):
        if not self.validCoordinate(coordinates):
            return False
        if self.checkShipAvailability(self.getDoubleCoordinate(coordinates), length):
            self.insertShip(self.getDoubleCoordinate(coordinates), length, symbol)
            return True
        else:
            return False
        
    # generate coordinates randomly    
    def initShips(self, command = None):                                       
        shipList = [5, 4, 3, 2]
        alphas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        if command == "player1":
            r1 = random.randint(1, 5)
            r2 = random.randint(1, 6)
            r3 = random.randint(1, 7)
            r4 = random.randint(1, 8)
            a1 = random.randint(0, 3)
            coorList = []
            coorList.append(alphas[a1] + str(r1) + " " + alphas[a1] + str(r1 + 4))
            coorList.append(alphas[a1+2] + str(r2) + " " + alphas[a1+2] + str(r2 + 3))
            coorList.append(alphas[a1+4] + str(r3) + " "+ alphas[a1+4] + str(r3 + 2))
            coorList.append(alphas[a1+6] + str(r4) + " "+ alphas[a1+6] + str(r4 + 1))
            for i in range(4):
                self.checkInsertShip(coorList[i], shipList[i], symbolList[i])
            return True
        if command == "player2":
            r1 = random.randint(1, 5)
            r2 = random.randint(1, 6)
            r3 = random.randint(1, 7)
            r4 = random.randint(1, 8)
            a1 = random.randint(0, 3)
            coorList = []
            coorList.append(alphas[a1] + str(r1) + " " + alphas[a1] + str(r1 + 4))
            coorList.append(alphas[a1+2] + str(r2) + " " + alphas[a1+2] + str(r2 + 3))
            coorList.append(alphas[a1+4] + str(r3) + " "+ alphas[a1+4] + str(r3 + 2))
            coorList.append(alphas[a1+6] + str(r4) + " "+ alphas[a1+6] + str(r4 + 1))
            for i in range(4):
                self.checkInsertShip(coorList[i], shipList[i], symbolList[i])
            return True

    def ifHit(self, coordinates):
        row, col = self.getSingleCoordinate(coordinates)
        if self.table[row-1][col] in symbolList:
            print("Hit!")
            self.insert(row,col, HIT_SYMBOL)
            return True
        print("Missed!")
        return False

    def countSymbols(self, symbol):
        count = 0
        for row in self.table:
            for elem in row:
                if elem in symbol:
                    count +=1
        return count

# manage server socket interactions
def server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)

        print("Server is ready on port: " + str(PORT))
        client_socket, addr = server_socket.accept()
        print("Client " + str(addr) + " connected")
        print("Ships sizes; 5x1, 4x1, 3x1, 2x1")
        print("Grid size; 10x10")
        print("Use coordinates to play; A1..J10")

        opponentBoard = Grid()                                                  
        localBoard = Grid()                                                    
        localBoard.initShips("player1")
        lastGuessStack = list()                                                                 
        client_socket.send(("Player ready!\n").encode("utf-8"))                               
        readData = False
        
        while True:
            if readData:
                    data = client_socket.recv(RECV_BUFFER)
                    if not data:
                        print('\nDisconnected')
                        sys.exit()
                    else:                                                                       
                        readableData = data.decode("utf-8")[0:-1]
                        sys.stdout.write(data.decode("utf-8"))
                        sys.stdout.flush()

                        if readableData == "Hit!":
                            opponentBoard.insertByCoordinate(lastGuessStack.pop(), HIT_SYMBOL)
                        elif readableData == "Missed!":
                            opponentBoard.insertByCoordinate(lastGuessStack.pop(), MISSED_SYMBOL)
                        elif readableData == "Game over.":
                            print("You WON!")
                            exit()
                        elif readableData == "Player ready!":
                            continue
                        else:
                            if localBoard.ifHit(readableData):
                                if localBoard.countSymbols(symbolList) == 3:
                                    print("End of game, You LOST!")
                                    client_socket.send(("Game over.\n").encode("utf-8"))
                                else:
                                    client_socket.send(("Hit!\n").encode("utf-8"))
                            else:
                                client_socket.send(("Missed!\n").encode("utf-8"))
                            print("-->Your turn!")
                            localBoard.yourTurn = True
                            readData = False
         
            if not readData:
                
                print("Input;")
                msg = sys.stdin.readline()

                if str(msg) == "ships\n":
                    localBoard.print()
                    opponentBoard.print()
                else:
                    if opponentBoard.validCoordinate(msg.rstrip()):
                        if localBoard.yourTurn:
                            client_socket.send(msg.encode("utf-8"))
                            lastGuessStack.append(msg)  
                            localBoard.yourTurn = False
                            readData = True
                        else:
                            print("Wait for your turn!")
                        sys.stdout.write('-->Fire!\n')
                        sys.stdout.flush()

        server_socket.close()

    except socket.error as e:
        print("Socket error({0}): {1}".format(e.errno, e.strerror))

    except KeyboardInterrupt:
        print("Closing server")
        client_socket.close()

    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
        
# manage client socket interactions
def client():
    host = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
    port = PORT
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(60)
    
    try:
        s.connect((host, port))
    except:
        print('Unable to connect')
        sys.exit()
    print('Connected to other player.')
    print("Ships sizes; 5x1, 4x1, 3x1, 2x1")
    print("Grid size; 10x10")
    print("Use coordinates to play; A1..J10")

    opponentBoard = Grid()
    localBoard = Grid()
    localBoard.initShips("player2")
    lastGuessStack = list()
    s.send(("Player ready!\n").encode("utf-8"))

    readData = True
    while True:
        if readData:

                data = s.recv(RECV_BUFFER)
                
                if not data:
                    print('\nDisconnected from server')
                    sys.exit()
                else: 
                    readableData = data.decode("utf-8")[0:-1]
                    sys.stdout.write(data.decode("utf-8"))
                    sys.stdout.flush()
                    
                    if readableData == "Hit!":
                        opponentBoard.insertByCoordinate(lastGuessStack.pop(), HIT_SYMBOL)
                    elif readableData == "Missed!":
                        opponentBoard.insertByCoordinate(lastGuessStack.pop(), MISSED_SYMBOL)
                    elif readableData == "Game over.":
                        print("You WON!")
                        exit()
                    elif readableData == "Player ready!":
                        continue
                    else:
                        if localBoard.ifHit(readableData):
                            
                            if localBoard.countSymbols(symbolList) == 3: 
                                print("End of game, You LOST!")
                                s.send(("Game over.\n").encode("utf-8"))
                                exit()
                            else:
                                s.send(("Hit!\n").encode("utf-8"))
                        else:
                            s.send(("Missed!\n").encode("utf-8"))
                        print("-->Your turn!")
                        localBoard.yourTurn = True
                        readData = False     
            
        if not readData:  
            
            print("Input;")            
            msg = sys.stdin.readline()

            if str(msg) == "ships\n":
                localBoard.print()
                opponentBoard.print()
            else:
                if opponentBoard.validCoordinate(msg.rstrip()):
                    if localBoard.yourTurn:
                        s.send(msg.encode("utf-8"))
                        lastGuessStack.append(msg)  
                        localBoard.yourTurn = False
                        readData = True    
                    else:
                        print("Wait for your turn!")
                        
                    sys.stdout.write('-->Fire!\n')
                    sys.stdout.flush()
             
# start game with (s)erver or (c)lient parameter
if __name__ == "__main__":
    
    if sys.argv[1].lower() == 'c': 
        sys.exit(client())
    elif sys.argv[1].lower() == 's':
        sys.exit(server())
    else: 
        print("use 'battleship.py s' or 'battleship.py c' command")

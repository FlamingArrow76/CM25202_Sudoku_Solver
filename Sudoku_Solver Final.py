import numpy as np
import time
class Node:
    def __init__(self, row, column, number):    #Initialises Node class
        self.state = row, column, number        #Each square has a row and column (position) and filled with a number.

    def is_complete(sudoku):                                    #Function to check if sudoku is complete.
        for line in range(0,9):                                 #Iterates through each row/column.
            if set(range(1,10)) - set(sudoku[line,:]):          #If a line or column doesn't contain 
                return 0                                        #numbers 1-9. It returns 0.
            elif set(range(1,10)) - set(sudoku[:,line]):   
                return 0
        return 1                                                #Otherwise it returns 1 (complete).

    def possible_values(sudoku, row, column):               #Finds all possible values for a given square in a sudoku.
        rowvals = sudoku[row,:][sudoku[row,:] != 0]         #Initially all possible values are numbers 1-9.             
        colvals = sudoku[:,column][sudoku[:,column] != 0]                   #Values that already appear in row/column    
        B = 3*(column//3)+(row//3)                                          #are removed from possible values list.
        block = sudoku[(3*(B%3)):(3*((B%3)+1)), (3*(B//3)):(3*(B//3+1))]                        #Removes any values appearing in block
        possible = list(set(range(1,10)) - set(block.flatten())- set(rowvals) -set(colvals))    #square is in.
        return possible                                                                         #Returns possible values. 

    #Function finds the best optimum move for the program to perform.   
    def obtain_move(sudoku, no_good, totalpossible, move_num):
        g = totalpossible.copy()
        totalpossible = g[g[:,1] == 2]              #Only checks the squares that have two possible values. 
        if len(totalpossible) == 0:                                         #If there are none then it returns no move.
            totalpossible = g[g[:,1] == 3]
            if len(totalpossible) == 0:
                return [0, 0, []]                  
        best = np.where(totalpossible[:,0] == min(totalpossible[:,0]))      #Finds the row with the overall least values. 
        
        [change_row,change_col] = totalpossible[best[0][0],2:4]             #Extracts the co-ordinate and gets possible values for 
        change = Node.possible_values(sudoku, change_row,change_col)        #it using possible values function. 
        change = [a for a in change if [move_num, [change_row,change_col,a]] not in no_good]     #Removes any values that have been 
        return [change_row, change_col, change]                                                         #identified as bad moves (for the
                                                                                                        #current move).
#Main function for solving the sudoku. 
def sudoku_solver(sudoku):
    moves_done = []                                 #List to store moves chosen by AI.
    every_move = []                                 #List to store every move performed (ones not done by AI)
    no_good = []                                    #List of moves and their move numbers t
    totalpossible = np.zeros((9,4), dtype = int)                #Creates 9x4 to store optimum squares for each row. 
    while not Node.is_complete(sudoku):                         #Function runs until the suduku is complete. 
        error = 0                                               #Initially there is no error.
        
        #This section fills in any squares where there is only 1 possible value. 
        while error != 1:                                   #While there isn't an error
            initial = sudoku.copy()                         #Makes a copy of the sudoku. 
            empty_row, empty_col = np.where(sudoku == 0)    #Finds locations of empty squares. 
            totalpossible.fill(0)                           #Fills the optimum square grid with zeros.
            totalpossible[:,1] = 9                          #Second column contains number of possible values for square with the 
                                                            #least possible values. 
            for x in range(0,len(empty_row)):           #Runs through each location. 
                row = empty_row[x]
                col = empty_col[x]
                val = Node.possible_values(sudoku, row ,col)    #Gets all possible values for a square. 
                numVal = len(val) 
                if numVal == 0:                 #If there are no possible values then there is an error
                    error = 1                   #Sets the error variable and breaks the loop.
                    break 
                elif numVal == 1:                               #If there is one value then the square is filled with it.
                    sudoku[row,col] = val[0]                    #This move is stored in the list of every move (as it was not guessed). 
                    every_move.append([row, col, val[0]])       #The program moves to the next square. 
                    continue
                else:                                           #If there is more than one value. 
                    totalpossible[row,0] += numVal              #Total values for that row is increased by this number. 
                    if numVal <= totalpossible[row,1]:                  #Stores co-ordinates if number of values smaller than 
                        totalpossible[row,1:4] = [numVal,row ,col]      #current smallest. Moves onto next square.  
                        continue

            if (sudoku==initial).all():             #If the sudoku goes through this process and is unchanged (from initial state)
                if Node.is_complete(sudoku):        #the loop is broken. This only occurs if the sudoku isn't complete. If it is
                    return sudoku                   #then the sudoku is returned. 
                break
            
        #The algorithm attempts to find the next move with the current totalpossible values.
        #It retrieves the co-ordinate and possible values for the next move to change them too.
        [change_row, change_col, change] =  Node.obtain_move(sudoku, no_good, totalpossible, len(moves_done))    

        if error or not change:         #In the event of an error or the optimal move has no available spaces.  
            if moves_done == []:        #Sudoku is unsolvable if there is an error on the first move. 
                sudoku[:,:] = -1        #Returns 9x9 grid of -1s. 
                return sudoku
            last = moves_done.pop()             #If there have been moves.
            revert = 0                          #Undo every move done up to (not including)
            while last != revert:               #the last move done by the AI. 
                revert = every_move.pop()
                sudoku[revert[0],revert[1]] = 0
            no_good = [a for a in no_good if a[0] <= len(moves_done)] + [[len(moves_done),last]]    #Add the bad move to the list 
            continue                                                                                #of no_good moves.

        change = change.pop()                               #If there are multiple values it takes the largest one. 
        sudoku[change_row,change_col] = change              #The square becomes this value and the move is added to both 
        moves_done.append([change_row,change_col,change])   #move lists (as this is done by the AI). 
        every_move.append([change_row,change_col,change])
    
    solved_sudoku = sudoku  #Once the loop is completed the function returns the completed sudoku. 
    return solved_sudoku


def test(sudoku,answer):
    tot = 0
    for a in range(15):
        print(sudoku[a])
        t0 = time.time()
        solution = sudoku_solver(sudoku[a])
        t1 = time.time()
        check = (solution==answer[a].astype(int)).all()
        print(a, check, t1-t0)
        tot +=t1-t0
    print('Average:',tot/15)
sudoku = np.load(r'C:\Users\TomSw\OneDrive\Documents\Python Stuff\CM25202\sudoku\data\very_easy_puzzle.npy')
answer = np.load(r'C:\Users\TomSw\OneDrive\Documents\Python Stuff\CM25202\sudoku\data\very_easy_solution.npy')
#test(sudoku,answer)
#print('')
sudoku = np.load(r'C:\Users\TomSw\OneDrive\Documents\Python Stuff\CM25202\sudoku\data\easy_puzzle.npy')
answer = np.load(r'C:\Users\TomSw\OneDrive\Documents\Python Stuff\CM25202\sudoku\data\easy_solution.npy')
#test(sudoku,answer)
#print('')

sudoku = np.load(r'C:\Users\TomSw\OneDrive\Documents\Python Stuff\CM25202\sudoku\data\medium_puzzle.npy')
answer = np.load(r'C:\Users\TomSw\OneDrive\Documents\Python Stuff\CM25202\sudoku\data\medium_solution.npy')
#test(sudoku,answer)
#print('')

sudoku = np.load(r'C:\Users\TomSw\OneDrive\Documents\Python Stuff\CM25202\sudoku\data\hard_puzzle.npy')
answer = np.load(r'C:\Users\TomSw\OneDrive\Documents\Python Stuff\CM25202\sudoku\data\hard_solution.npy')
#test(sudoku,answer)

sudoku = np.array([[0, 0, 3, 2, 0, 0, 0, 8, 0],
         [0, 9, 0, 0, 0, 0, 0, 3, 0],
         [6, 0, 0, 1, 8, 0, 0, 0, 0],
         [0, 7, 0, 0, 3, 0, 0, 0, 0],
         [9, 0, 0, 0, 0, 7, 8, 0, 1],
         [0, 0, 0, 0, 1, 0, 0, 5, 0],
         [0, 0, 6, 0, 0, 0, 0, 0, 0],
         [0, 5, 0, 0, 9, 0, 7, 0, 0],
         [1, 0, 0, 0, 0, 0, 6, 0, 0]])
print(sudoku)
solution = sudoku_solver(sudoku)
print(solution)

'''
j = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 6, 0, 0, 0, 0, 0],
          [0, 7, 0, 0, 0, 0, 2, 0, 0],
          [0, 5, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 4, 0, 7, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 0, 0, 0, 0, 0, 8],
          [0, 0, 0, 5, 0, 0, 0, 1, 0],
          [0, 9, 0, 0, 0, 0, 4, 0, 0]])
out = sudoku_solver(j)
print(out,"\n")

a = 5
t0 = time.time()
solution = sudoku_solver(sudoku[a])
b = solution.copy()
a = -12
while a < 20:
    sudoku = b
    mask = np.random.randint(0,2, (9, 9))
    sudoku = np.multiply(sudoku, mask, out=sudoku, casting='unsafe')
    mask = np.random.randint(0,2, (9, 9))
    sudoku = np.multiply(sudoku, mask, out=sudoku, casting='unsafe')
    print(sudoku)
    t0 = time.time()
    out = sudoku_solver(sudoku)
    t1 = time.time()
    print(out,"\n")
    a +=1
a = 14
t0 = time.time()
solution = sudoku_solver(sudoku[a])
t1 = time.time()
check = (solution==answer[a].astype(int)).all()
print(check, t1-t0)

print('')

'''

#a = 2,5,11,10,7 (solvable)
#a = 12,13,14,0,1  (unsolvable)
#a = 9,3,6 (solvable)
#a = 8,4  (solvable)

#usualy gets stuck on 0,0 values. will conotnuously set it despite having a value.
'''    
def check_state(sudoku):         #Checks if the sudoku is in a valid state.
    for a in range(0,9):
        #j = (min(sudoku[a,:]) != 0 * sorted(sudoku[a,:]) != list(range(1,10)))
        #k = (min(sudoku[a,:]) != 0 * sorted(sudoku[a,:]) != list(range(1,10)))
        there = []
        for x in sudoku[a,:]:
            if x in there and x != 0:
                return 1
            there.append(x)
        there = []
        for x in sudoku[:,a]:
            if x in there and x != 0:
                return 1
            there.append(x)
    return 0
    '''

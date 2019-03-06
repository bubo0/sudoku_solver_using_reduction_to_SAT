# Copyright (c) Microsoft Corporation 2015, 2016

# The Z3 Python API requires libz3.dll/.so/.dylib in the 
# PATH/LD_LIBRARY_PATH/DYLD_LIBRARY_PATH
# environment variable and the PYTHON_PATH environment variable
# needs to point to the `python' directory that contains `z3/z3.py'
# (which is at bin/python in our binary releases).

# If you obtained example.py as part of our binary release zip files,
# which you unzipped into a directory called `MYZ3', then follow these
# instructions to run the example:

# Running this example on Windows:
# set PATH=%PATH%;MYZ3\bin
# set PYTHONPATH=MYZ3\bin\python
# python example.py

# Running this example on Linux:
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:MYZ3/bin
# export PYTHONPATH=MYZ3/bin/python
# python example.py

# Running this example on macOS:
# export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:MYZ3/bin
# export PYTHONPATH=MYZ3/bin/python
# python example.py


from z3 import *
import time
import random


###############################
# First reduction
###############################
def firstReduction(n):
    s = Solver()
    X = n * n
    Y = n * n
    Z = n * n

    board = [[[Bool("b_" + str(x) + str(y) + str(z)) for z in range(Z)]
                                                     for y in range(Y)]
                                                     for x in range(X)]
    # rule 1 
    for x in range(X):
        for y in range(Y):
            s.add(Or(board[x][y]))    

    # rule 2
    for x in range(X):
        for z in range(Z):
            for y in range(Y-1):
                for i in range(y+1, Y):
                    s.add(Or(Not(board[x][y][z]), Not(board[x][i][z])))

    # rule 3
    for y in range(Y):
        for z in range(Z):
            for x in range(X-1):
                for i in range(x+1, X):
                    s.add(Or(Not(board[x][y][z]), Not(board[i][y][z])))

    # rule 4
    for z in range(Z):
        for i in range(n):
            for j in range(n):
                for x in range(n):
                    for y in range(n-1):
                        for p in range(n):
                            if p != x:
                                for q in range(y+1, n):
                                    s.add(Or(Not(board[n*i+x][n*j+y][z]), Not(board[n*i+p][n*j+q][z])))
    return s, board

############################
# 2nd reduction
# 2nd reduction
############################

def secondReduction(n):
    s = Solver()
    X = n * n
    Y = n * n
    Z = n * n

    board = [[[Bool("b_" + str(x) + str(y) + str(z)) for z in range(Z)]
                                                     for y in range(Y)]
                                                     for x in range(X)]

    # rule 1
    for x in range(X):
        for y in range(Y):
            for z in range(Z-1):
                for i in range(z+1, Z):
                    s.add(Or(Not(board[x][y][z]), Not(board[x][y][i])))

    # rule 2
    for x in range(X):
        for z in range(Z):
            temp = []
            for y in range(Y):
                temp.append(board[x][y][z])
            s.add(Or(temp))
    
    # rule 3
    for y in range(Y):
        for z in range(Z):
            temp = []
            for x in range(X):
                temp.append(board[x][y][z])
            s.add(Or(temp))  
 
    # rule 4
    for z in range(Z):
        for i in range(n):
            for j in range(n):
                temp = []
                for x in range(n):
                    for y in range(n):
                        temp.append(board[i*n+x][j*n+y][z])
                s.add(Or(temp))
    return s, board



###########################
# test cases:
###########################

def test_case0(s, board):
    print("adding no prefilled number")

def test_case1(s, board):
    '''
    testing a valid board of 4*4:

    0123
    23
    3 1
    1  2
    '''

    s.add(board[0][0][0])
    s.add(board[0][1][1])
    s.add(board[0][2][2])
    s.add(board[0][3][3])
    s.add(board[1][0][2])
    s.add(board[1][1][3])
    s.add(board[2][0][3])
    s.add(board[2][2][1])
    s.add(board[3][0][1])
    s.add(board[3][3][2])


def test_case2(s, board):
    '''
    testing an invalid board of 4*4:

    0123
    23
    1 3
    3  3
    '''

    s.add(board[0][0][0])
    s.add(board[0][1][1])
    s.add(board[0][2][2])
    s.add(board[0][3][3])
    s.add(board[1][0][2])
    s.add(board[1][1][3])
    s.add(board[2][0][1])
    s.add(board[2][2][3])
    s.add(board[3][0][3])
    s.add(board[3][3][3])

# randomly generate a prefilled board for testing
# P.S. it is difficult to randomly generate a valid board when n is relatively large
def rand_test_case(s, board, n):
    '''
    creating random test case for sudoku with size of (n^2) * (n^2)
    '''
    N = n*n
    row = []
    col = []
    for i in range(N):
        s.add(board[0][i][i])
        row.append(i)

    col.append(0)
    for j in range(1, N):
        s.add(board[j][0][N-j])
        col.append(N-j)
 
    for k in range(1, n):
        s.add(board[k][k][k+n-1])    

    p = n
    while p < N:
        temp = random.randint(0,N-1)
        if temp!=row[p] and temp!=col[p]:
            s.add(board[p][p][temp])
            p += 1

    print("random sample of " + str(N) + "*" + str(N) + " successfully generated")    


# the test framework
def test(method, testCase, n):
    if method == 1:
        s, board = firstReduction(n)
        print("testing 1st reduction")
    elif method == 2:
        s, board = secondReduction(n)
        print("testing 2nd reduction")
    else:
        print("error: undefined option")
        return

    if id(testCase) == id(rand_test_case):
        testCase(s, board, n)
    else:
        testCase(s, board)
    print("SAT solver working, solving sudoku of size " + str(n*n) + "*" + str(n*n) + "...")
    start = time.time()
    result = s.check()
    end = time.time()
    print("SAT solver ended")
    print("The result is: ")
    print(result)
    print("Using " + str(end-start) + " second")
    print(" ")



if __name__ == "__main__":
    # not adding any prefilled numbers 
    test(1, test_case0, 2)
    test(2, test_case0, 2)

    # testing a valid board
    test(1, test_case1, 2)
    test(2, test_case1, 2)

    # testing an invalid board 
    test(1, test_case2, 2)
    test(2, test_case2, 2)

    test(1, rand_test_case, 2)
    test(2, rand_test_case, 2)

    test(1, test_case0, 3)
    test(2, test_case0, 3)

    test(1, test_case0, 4)
    # test(2, test_case0, 4) # taking too much time; didn't finish

    test(1, test_case0, 5)
    # test(2, test_case0, 5) # taking too much time; didn't finish

    '''
    test(1, rand_test_case, 3)
    test(2, rand_test_case, 3)

    test(1, rand_test_case, 4)
    # test(2, rand_test_case, 4)
    
    test(1, rand_test_case, 5) 
    '''

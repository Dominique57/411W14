from enum import Enum

class Type(Enum):
    Exit = "1"
    Close = "2"
    Status = "3"
    Message = "4"
    Exec = "5"

def StrToMat(string):
    N = []
    for elt in string.split(";"):
        O = []
        elt = elt.split(',')
        for e in elt:
            O.append(int(e))
        N.append(O)
    return N

def RowToStr(row):
    string = ""
    length = len(row)
    for i in range(length - 1):
        string += str(row[i]) + ","
    string += str(row[length - 1])
    return string

def MatToStr(mat):
    string = ""
    lengthRow = len(mat)
    for i in range(lengthRow - 1):
        string += RowToStr(mat[i]) + ";"
    string += RowToStr(mat[lengthRow - 1])
    return string

def MultMatr(A, B):
    C, n, m, p = [], len(A), len(A[0]), len(B[0])
    for i in range(n):
        line = []
        for j in range(p):
            summ = 0
            for k in range(m):
                summ += A[i][k]*B[k][j]
            line.append(summ)
        C.append(line)
    return C

def AddMat(A, B):
    bWidth, bHeight = len(B), len(B[0])
    for i in range(bWidth):
        A[i] = A[i] + B[i]

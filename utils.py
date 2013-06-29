
import random

def turn_matrix(matr, n, direct):
 
    if direct > 0:
        for i in xrange(n/2):
            for j in xrange(i, n-1-i):
                tmp = matr[i][j]
                matr[i][j] = matr[n-j-1][i]
                matr[n-j-1][i] = matr[n-i-1][n-j-1]
                matr[n-i-1][n-j-1] = matr[j][n-i-1]
                matr[j][n-i-1] = tmp
    else:
        for i in xrange(n/2):
            for j in xrange(i, n-1-i):
                tmp = matr[i][j]
                matr[i][j]=matr[j][n-1-i]
                matr[j][n-1-i]     = matr[n-1-i][n-1-j]
                matr[n-1-i][n-1-j] = matr[n-1-j][i]
                matr[n-1-j][i]     = tmp
    
    return matr


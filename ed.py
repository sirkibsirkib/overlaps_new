import cigar_strings
import random

# def ed(x, y):
# 	if len(x) == 0 or len(y) == 0:
# 		return abs(len(x) - len(y))
# 	a = ed(x[:-1], y[:-1]) + (1 if x[-1] != y[-1] else 0)
# 	b = ed(x[:-1], y) + 1
# 	c = ed(x, y[:-1]) + 1
# 	return min(a, b, c)

def get_cigar_seq(x, y, mat):
	# print('cigar_string', x, y)
	# print(mat)
	cigar_seq = []
	i = len(y)
	j = len(x)
	old_c = None
	count = 0
	while i > 0 or j > 0:
		if i == 0:
			j -= 1
			c = 'D'
		elif j == 0:
			i -= 1
			c = 'I'
		else:
			val = min(mat[i - 1][j], mat[i - 1][j - 1] - 1, mat[i][j - 1])
			if mat[i - 1][j] == val:
				i -= 1
				c = 'I'
			elif mat[i][j - 1] == val:
				j -= 1
				c = 'D'
			else:
				i -= 1
				j -= 1
				c = 'M'

		if c != old_c:
			if old_c  != None:
				cigar_seq.append((count, old_c))
			old_c = c
			count = 0
		count += 1

	cigar_seq.append((count, old_c))
	return cigar_strings.Cigar(cigar_seq[::-1])


def distance_alignment(x, y):
	mat = [[0 for i in range(len(x) + 1)] for j in range(len(y) + 1)]
	for i in range(len(x) + 1):
		mat[0][i] = i
	for j in range(len(y) + 1):
		mat[j][0] = j
	for i in range(1, len(y) + 1):
		for j in range(1, len(x) + 1):
			delta = 0 if y[i - 1] == x[j - 1] else 1
			right	= mat[i - 1][j] + 1
			down	= mat[i][j - 1] + 1
			across 	= mat[i - 1][j - 1] + delta
			mn = right
			if down < mn:
				mn = down
			if across < mn:
				mn = across
			mat[i][j] = mn

	return mat[-1][-1], get_cigar_seq(x, y, mat)
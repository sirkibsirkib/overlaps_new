alphabet = ['A', 'C', 'T', 'G']
opposite = {'A':'T', 'T':'A', 'G':'C', 'C':'G'}

def invert(string):
	inverted = ''.join([(opposite[c]if c in opposite else c) for c in string][::-1])
	# print(string, '==>', inverted)
	return inverted
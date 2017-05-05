alphabet = ['A', 'C', 'T', 'G']
opposite = {'A':'T', 'T':'A', 'G':'C', 'C':'G'}

def invert(string):
	inverted = ''.join([(opposite[c]if c in opposite else c) for c in string][::-1])
	# print(string, '==>', inverted)
	return inverted


def clean_symbol(c):
	if c in alphabet:
		return c
	if c == '$':
		return '$'
	return 'N'

def prepare(S_dict):
	ret = dict()
	for k, v in S_dict.items():
		ret[k] = ''.join([clean_symbol(c) for c in v])
	return ret
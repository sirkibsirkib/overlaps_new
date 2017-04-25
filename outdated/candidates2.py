import math

def partition(s, n=4):
	ls = []
	for i in range(math.ceil(1.0*len(s)/n)):
		ls.append(s[:n])
		s = s[n:]
	return ls



def enumer8(trie, string):
	if trie:
		for k,v in trie.items():
			enumer8(v, string+k)
	else:
		print(string)

def branch(P_suffix, filter, alphabet, errors_so_far, pos_in_partition, part_index):
	if part_index >= len(P_suffix):	#no more partitions
		return None
	correct_char = P_suffix[part_index][pos_in_partition]
	assert errors_so_far <= filter[part_index]
	if len(P_suffix[part_index]) == pos_in_partition+1:
		next_pos = 0
		next_part_index = part_index + 1
	else:
		next_pos = pos_in_partition + 1
		next_part_index = part_index


	node = dict()
	if errors_so_far < filter[part_index]: #can afford to branch
		for a in alphabet:
			branch_error = errors_so_far if a ==  correct_char else errors_so_far+1
			node[a] = branch(P_suffix, filter, alphabet, branch_error, next_pos, next_part_index)
	else:
		node[correct_char] = branch(P_suffix, filter, alphabet, errors_so_far, next_pos, next_part_index)
	return node

def construct_trie(P_suffix, filter, alphabet):
	print('constructing', P_suffix, filter, alphabet)
	return branch(P_suffix, filter, alphabet, 0, 0, 0)

# alphabet is a set of characters
# S is the set of Strings
def candidates(S, alphabet):
	for P in S:
		P_parts = partition(P)
		for oth in S:
			for i in range(0, len(P_parts)):
				P_suffix = P_parts[i:]
				filter = list(range(0, len(P_suffix)))
				trie = construct_trie(P_suffix, filter, alphabet)
				print('original:\n', P, '\n')
				enumer8(trie, "")


alphabet = {'0', '1'}
S = {'10010101001'}
candidates(S, alphabet)
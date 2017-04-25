import math

s_param = 2

'''
return a tuple of (a,b)
(a) a list of block lengths
	each element represents a block of the pattern
(b) a list of filters
	each of which is a list of integers. The ints will be interpreted as suffixes of blocks
'''
def get_block_lengths_and_filters(patt_length, e, thresh):
	global s_param

	ls = []
	for l in range(thresh, patt_length+1):
		if math.ceil(e*(l-1)) < math.ceil(e*l):
			ls.append(l)
	ls.append(patt_length+1)
	k = math.ceil(e*ls[0] + s_param - 1)
	a = math.ceil((ls[0]-1)/k)
	b = ls[0]-thresh
	L = max(a, b)
	p = math.floor((ls[0]-1-L) / (k-1))
	first_half_len = p*(k-1)+L
	longer_blocks_in_first_half = ls[0]-1-first_half_len
	block_lengths = [p for _ in range(k-1-longer_blocks_in_first_half)] +\
		[p+1 for _ in range(longer_blocks_in_first_half)] #first k-1 blocks
	block_lengths.append(L)
	for i in range(len(ls)-1):
		block_lengths.append(ls[i+1] - ls[i])

	filters = []
	end_range = len(block_lengths)-s_param+1
	for i in range(end_range):
		filters.append(list(range(0, len(block_lengths)-i-s_param)) + [end_range-i-1 for _ in range(s_param)])

	# print(block_lengths)
	# print("\nFILTERS:\n")
	# for i, f in enumerate(filters):
	# 	print('\t'*i, *f, sep='\t')
	return block_lengths, filters


'''
return whether or not the current node of the trie is permitted to generate candidates
'''
def conditions_met(p_i_start, p_i_next, thresh, block_id, errors):
	global glob_filters
	c1 = p_i_next >= thresh	# position in overlap at least at thresh
	c2 = block_id > 0		# must have fully matched the first block
	c3 = block_id >= s_param-1 and errors <= (block_id - s_param + 1)
	return c1 and c2 and c3
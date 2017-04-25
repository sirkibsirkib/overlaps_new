import math


'''
return a tuple of (a,b)
(a) a list of block lengths
	each element represents a block of the pattern
(b) a list of filters
	each of which is a list of integers. The ints will be interpreted as suffixes of blocks
'''
def get_block_lengths_and_filters(patt_length, e, thresh):
	print('thresh according to valimaki', thresh)
	p_ = [math.ceil(l * 1.0 / (math.ceil(e * l) + 1))
		  for l in range(thresh, patt_length+1)]
	p = min(p_)
	# print('p_', p_)
	remain = patt_length
	block_lengths = []
	while (remain > 0):
		next = min(remain, p)
		block_lengths.append(next)
		remain -= next
	# print('part_lengths', block_lengths)

	filters = []
	for i in range(len(block_lengths)-1):
		if i == 0:
			filters.append(list(range(1, len(block_lengths)+1)))
		else:
			filters.append(list(range(0, len(block_lengths)-i)))

	# print('block_lengths', block_lengths)
	# print('filters')
	# for f in filters:
	# 	print(f)
	return block_lengths, filters


'''
return whether or not the current node of the trie is permitted to generate candidates
'''
def conditions_met(p_i_start, p_i_next, thresh, block_id, errors):
	c1 = p_i_next >= thresh	# position in overlap at least at thresh
	c2 = block_id > 0		# must have fully matched the first block
	return c1 and c2
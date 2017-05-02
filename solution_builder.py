def companion_index(x):
	if x%2==0: return x+1
	return x-1

def candidate_to_solution(candidate, a_len, b_len, cigar, k, arguments, mappings):
	a_index, b_index, a_ovr, b_ovr, b_tail, debug_str = candidate
	# print(candidate)
	#solution accepted
	# print('\n\n\n>')
	# print(T)
	# print(debug_aux.carat_chars(range(a_index, a_index + a_len), len(T) + 5))
	# print(debug_aux.carat_chars(range(b_index, b_index + b_len), len(T) + 5))
	a_id = mappings.index2id[a_index]
	b_id = mappings.index2id[b_index]
	if b_ovr+b_tail > b_len:
		#blind spot overlapping ???[MMMMM]~~~~~~~~
		#                         ~~MMMMM
		# print('blind spot overlapping! DISCARD')
		return None
	# print(a_id, 'pref', T[a_index:a_index+a_len])
	# print(b_id, 'suff', T[b_index:b_index+b_len])
	# print('b_tail!!!', b_tail)
	OLA = a_ovr
	OLB = b_ovr
	if b_tail == 0:
		OHA = -(b_len-b_ovr)
		OHB = -(a_len-a_ovr)
	else:
		OHA = -(b_len - b_tail - b_ovr)
		OHB = b_tail
	OHA = -(b_len - b_ovr) if b_tail == 0 else -(b_len - b_tail - b_ovr)
	OHB = -(a_len - a_ovr) if b_tail == 0 else b_tail
	# print('initIDS', a_id, b_id)
	# print(T)
	# print(' :  ', '^'*-OHA + T[a_index:a_index+a_len] + '*'*(b_ovr-a_ovr) + '~'*OHB)
	# print(' :  ', '^'*OHA + T[b_index:b_index+b_len] + '*'*(a_ovr-b_ovr) + '~'*-OHB)

	if a_id > b_id:	# ensure smaller string comes first
		# print('smaller first! VFLIP')
		OHA *= -1
		OHB *= -1
		a_len, b_len = b_len, a_len
		a_id, b_id, OLA, OLB = b_id, a_id, OLB, OLA
		a_index, b_index = b_index, a_index
		cigar.v_flip()
	# print('tIDS', a_id, b_id)
	# print(T)
	# print(' :  ', '^' * -OHA + T[a_index:a_index + a_len] + '*' * (b_ovr - a_ovr) + '~' * OHB)
	# print(' :  ', '^' * OHA + T[b_index:b_index + b_len] + '*' * (a_ovr - b_ovr) + '~' * -OHB)
	if arguments.inverts and a_id % 2 == 1:	#guarantee not BOTH are flipped
		# print('a must be non-neg! HFLIP')
		OHA, OHB = -OHB, -OHA
		a_id = companion_index(a_id)
		b_id = companion_index(b_id)
		a_index = mappings.id2index[a_id]
		b_index = mappings.id2index[b_id]
		cigar.h_flip()

	# print('TRANSFORMS COMPLETE')
	# print('tIDS', a_id, b_id)
	# print(T)
	# print(' :  ', '^'*-OHA + T[a_index:a_index+a_len] + '*'*(b_ovr-a_ovr) + '~'*OHB)
	# print(' :  ', '^'*OHA + T[b_index:b_index+b_len] + '*'*(a_ovr-b_ovr) + '~'*-OHB)
	CIGAR = cigar
	K = k
	O = 'N' if not arguments.inverts or b_id%2==0 else 'I'
	a_name = mappings.id2names[a_id]
	b_name = mappings.id2names[b_id]
	solution = (a_name, b_name, O, OHA, OHB, OLA, OLB, K, CIGAR)
	# print_solution(solution, S_dict)
	return solution
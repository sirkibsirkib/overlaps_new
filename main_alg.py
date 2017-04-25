import time

# import valimaki_2 as specific
import kucherov as specific
from ed import distance_alignment as edit_distance
from prog_args import Arguments
from read_data import rd
import debug_aux

from index_searcher import FMIndex as fm_index

'''AUX FUNCTIONS and CLASSES'''



def align_using_cigar(a, b, cigar):
	a_cigar = ''
	b_cigar = ''
	a_i = 0
	b_i = 0
	for n, code in zip(cigar[::2], cigar[1::2]):
		if code == 'I':
			for _ in range(int(n)):
				a_cigar += '-'
				b_cigar += b[b_i]
				b_i += 1
		elif code == 'D':
			for _ in range(int(n)):
				b_cigar += '-'
				a_cigar += a[a_i]
				a_i += 1
		else:
			for _ in range(int(n)):
				a_cigar += a[a_i]
				a_i += 1
				b_cigar += b[b_i]
				b_i += 1
	return a_cigar, b_cigar

def print_solution(sol):
	print(sol)
	a = S_dict[sol[0]]
	if sol[6]: a = a[::-1]
	b = S_dict[sol[1]]
	if sol[7]: b = b[::-1]
	# print('a', a)
	# print('b', b)
	a_head = a[:len(a)-sol[2]]
	b_tail = b[sol[3]:]
	cigar = sol[5]
	a_aligned, b_aligned = align_using_cigar(a[-sol[2]:], b[:sol[3]], cigar)
	print(a_head + '(' + a_aligned + ')')
	print(((len(a_head)) * ' ') + '(' + b_aligned + ')' + b_tail)
	print()

def string_id_to_T_index_map(S):
	ind = 0
	ret = dict()
	for i, s in enumerate(S):
		length = len(s)
		ret[i] = ind
		ind += length+1
	return ret




'''MAIN FUNCTIONS'''

def block_id_and_error_lookups(suffix_parts, filter):
	block_id_lookup = []
	error_lookup = []

	for i in range(len(suffix_parts)):
		for _ in range(suffix_parts[i]):
			err = filter[i]
			block_id_lookup.append(i)
			error_lookup.append(err)
	# print()
	# print('suffix_parts', suffix_parts, 'filter', filter)
	# print('block_id_lookup', block_id_lookup)
	# print('error_lookup', error_lookup)
	return block_id_lookup, error_lookup

def find_candidates(S, T, id_to_index_map, index_to_id_map, arguments):
	print('hey')
	candidate_set = set()
	index = fm_index(T, candidate_set, specific.conditions_met, arguments, index_to_id_map)
	for p_id, patt in enumerate(S):
		if len(patt) < arguments.thresh:
			#skip patterns too small to match
			continue

		block_lengths, filters = specific.get_block_lengths_and_filters(len(patt), arguments.e, arguments.thresh)
		assert sum(block_lengths) == len(patt) #making sure partition lengths are sound
		p_T_index = id_to_index_map[p_id]
		print("NEXT PATT:")
		print(T)
		print(debug_aux.carat_chars([p_T_index], 50))
		print(patt)

		print('FILTERS')
		for filter in filters:
			print('filter', filter)
			first_block_index = len(block_lengths)-len(filter)
			p_i_start = sum(block_lengths[:first_block_index])
			print()
			print(patt, '    <---- patt')
			print(debug_aux.carat_chars([p_i_start], len(patt)), '    <---- suffix start')
			block_id_lookup, error_lookup = block_id_and_error_lookups(block_lengths[first_block_index:], filter)
			print((' '*p_i_start) + (''.join(map(lambda x : str(x), block_id_lookup))), '    <--- block IDs')
			print((' '*p_i_start) + (''.join(map(lambda x : str(x), error_lookup))), '    <--- cumulative allowed errors')
			index.forward_search(patt, p_i_start, p_T_index, p_id, error_lookup, block_id_lookup)

	print('total nodes: ', index.nodes)
	print('total duplicate candidates: ', index.duplicate_candidate_count)
	print('original candidate ratio: ', len(candidate_set)/(len(candidate_set)+index.duplicate_candidate_count))
	return candidate_set


def remove_reflexive_candidates(candidates, arguments, index_to_id_map, id_to_names_map):
	print('ok')
	if not arguments.inverts:
		print('A CASE')
		return {x for x in candidates if x[0] != x[1]}
	else:
		print('B CASE')
		ret = set()
		for x in candidates:
			id_a = index_to_id_map[x[0]]
			id_b = index_to_id_map[x[1]]

			#if not matching a string with itself (flipped or otherwise)
			if (id_to_names_map[id_a] != id_to_names_map[id_b]):
				ret.add(x)
		return ret

def verifies(candidate, T, e, c0_suffix_length, indels):
	if indels:
		a_start = candidate[0] + c0_suffix_length - candidate[2]
		a_end = a_start + candidate[2]
		a = T[a_start: a_end]
		b_end = candidate[1] + candidate[3]
		b = T[candidate[1]: b_end]
		ed, cigar = edit_distance(a, b)
		return (ed if ed <= max(candidate[2], candidate[3]) *e else -1), cigar

	try:
		errors_allowed = candidate[2]*e
		error_count = 0
		a_start = candidate[0] + c0_suffix_length - candidate[2]
		b_start = candidate[1]
		if a_start < 0 or b_start < 0:
			return -1, ''
		overlap_length = candidate[2]
		for i in range(overlap_length):
			error_count += 0 if T[a_start+i] == T[b_start+i] and T[b_start+i] != '$' else 1
			if error_count > errors_allowed:
				return -1, ''
		return error_count, str(overlap_length) + 'M'
	except:
		#out of string bounds exception
		return -1, ''

def verify(candidate_set, T, index_to_length_map, arguments):
	ret = set()
	for c in candidate_set:
		v, cigar = verifies(c, T, arguments.e, index_to_length_map[c[0]], arguments.indels)
		if v != -1:
			x = (c[0], c[1], c[2], c[3], v, cigar)
			ret.add(x)
	return ret

'''
Given S_dict, a dict with values being strings.
The keys for these values give the external names for these strings.
Outputs should return overlaps in this format
'''
def overlaps(S_dict, arguments):

	t0 = time.clock()
	# T, sorted_alphabet, indels, inclusions, candidate_set, thresh, condition_met_f

	# names_to_id_map = dict()
	id_to_names_map = dict()
	for id, name in enumerate(S_dict.keys()):
		if not arguments.inverts:
			id_to_names_map[id] = name
		else:
			id_to_names_map[id*2] = name
			id_to_names_map[(id*2)+1] = name


	S = [S_dict[id_to_names_map[key]] for key in id_to_names_map.keys()]\
		if not arguments.inverts\
		else [S_dict[id_to_names_map[key]]
			  if key%2==0 else S_dict[id_to_names_map[key]][::-1]
			  for key in id_to_names_map.keys()]

	print(S)
	T = ''
	id_to_index_map = dict()
	index_to_id_map = dict()
	for i, s in enumerate(S):
		id_to_index_map[i] = len(T)
		index_to_id_map[len(T)] = i
		T = T + s + '$'
	# print('T', T)
	# print('index_to_id_map', index_to_id_map)
	# print('id_to_index_map', id_to_index_map)
	# print()

	index_to_length_map = dict()
	for i, string in enumerate(S):
		index_to_length_map[id_to_index_map[i]] = len(string)

	t1 = time.clock()
	print('input time', t1-t0)
	#STEP 1
	candidate_set = find_candidates(S, T, id_to_index_map, index_to_id_map, arguments)
	print('candidate_set', candidate_set)
	print('index_to_id_map',index_to_id_map)

	candidate_set = remove_reflexive_candidates(candidate_set, arguments, index_to_id_map, id_to_names_map)


	t2 = time.clock()
	print('step1 time', t2-t1)
	#STEP 2
	verified_set = verify(candidate_set, T, index_to_length_map, arguments)

	t3 = time.clock()
	print('step2 time', t3-t2)
	# print('candidate_set', candidate_set)
	# print('verified_set', verified_set)
	print('num candidates:', len(candidate_set))
	print('num verified:', len(verified_set))
	print('step 1 precision', len(verified_set) / (len(candidate_set)) if len(candidate_set) > 0 else 1)
	print('verified set', verified_set)


	solutions = []
	for v in verified_set:
		a_id = index_to_id_map[v[0]]
		b_id = index_to_id_map[v[1]]
		if not arguments.inverts:
			a_flip = b_flip = False
		else:
			a_flip = a_id % 2 == 1
			b_flip = b_id % 2 == 1
		# print()
		# print(v)
		# print('==>')
		# print('a_id', a_id, 'b_id', b_id)
		# print('a_flip', a_flip, 'b_flip', b_flip)
		a_name = id_to_names_map[a_id]
		b_name = id_to_names_map[b_id]
		sol = (a_name, b_name, v[2], v[3], v[4], v[5], a_flip, b_flip)
		solutions.append(sol)


	# solutions = [(id_to_names_map[index_to_id_map[v[0]]],
	# 		 id_to_names_map[index_to_id_map[v[1]]],
	# 		 v[2], v[3], v[4], v[5], 'same' if not arguments.inverts or (v[0]+v[1])%2==0 else 'opp')
	# 		for v in verified_set]

	return sorted(solutions)


'''SCRIPT BEGIN'''


arguments = Arguments(indels=False, inclusions=True, inverts=True, e=0.002, thresh=5)


x = rd('data/basic.fasta')
print(x)
# exit(1)
# S_dict = x
S_dict = {0:'aaaaabbbbb', 1:'bbbbbccccc', 2:'cccccddddd', 3:'xxxxxxx'}
# S_dict = {0:'hannahismyname', 1:'igobyhannah', 2:'hanahisavalidspelling', 3:'spellingisfun'}
solutions = overlaps(S_dict, arguments)
print('\n\n====SOLUTIONS====\n\n')
for sol in solutions:
	print_solution(sol)
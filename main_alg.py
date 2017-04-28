import time

# import valimaki_2 as specific
import kucherov as specific
from ed import distance_alignment as edit_distance
import structs
import prog_io
import debug_aux
import math
import prog_alphabet
import cigar_strings
import random
from index_searcher import FMIndex as fm_index


'''AUX FUNCTIONS and CLASSES'''


def print_solution(solution, S_dict, debug=True):
	if debug:
		print(solution)
		print('S_dict', S_dict)
	a_name, b_name, O, OHA, OHB, OLA, OLB, K, CIGAR = solution
	a = S_dict[a_name]
	b = S_dict[b_name] if O == 'N' else prog_alphabet.invert(S_dict[b_name])
	if debug:
		print('a', a, 'b', b)

	if OHA > 0: a1 = OHA;	b1 = 0
	else:		a1 = 0;		b1 = -OHA
	a2 = OLA
	b2 = OLB
	if OHB > 0: a3 = 0;		b3 = OHB
	else:		a3 = -OHB;	b3 = 0
	if debug:
		print(a1,a2,a3)
		print(' '*b1 + '[' + a[:a1] + '|' + a[a1:a1+a2] + '|' + a[a1+a2:] + ']')
		print(b1,b2,b3)
		print(' '*a1 + '[' + b[:b1] + '|' + b[b1:b1+b2] + '|' + b[b1+b2:] + ']')
	assert a1+a2+a3 == len(a)
	assert b1+b2+b3 == len(b)


	a2_align, b2_align = CIGAR.align(a[a1:a1+a2], b[b1:b1+b2])

	# print('a\tb\tO\tOHA\tOHB\tOLA\tOLB\tK\tCIG')
	# print(*solution, sep='\t')
	print(' ' * (-OHA), a[:a1], a2_align, a[a1+a2:])
	print(' ' * OHA, b[:b1], b2_align, b[b1+b2:])

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

def find_candidates(S, T, arguments, mappings):
	print('id_to_index_map', mappings.id2index)
	print('index_to_id_map', mappings.index2id)
	candidate_set = set()
	index = fm_index(T, candidate_set, specific.conditions_met, arguments, mappings.index2id, mappings.id2index, len(S))
	for p_id, patt in enumerate(S):
		if len(patt) < arguments.thresh:
			#skip patterns too small to match
			continue

		block_lengths, filters = specific.get_block_lengths_and_filters(len(patt), arguments.e, arguments.thresh)
		assert sum(block_lengths) == len(patt) #making sure partition lengths are sound
		p_T_index = mappings.id2index[p_id]
		print("NEXT PATT:")
		print(T)
		print(debug_aux.carat_chars([p_T_index], 50))
		print(patt)

		error_hard_cap = math.floor(len(patt)*arguments.e)

		print('FILTERS')
		for filter in filters:
			print('filter', filter)

			filter_capped = [min(error_hard_cap, x) for x in filter]
			print('FILTER UNCAPPED', filter)
			print('FILTER CAPPED', filter_capped)
			print('patt len', len(filter))

			filter = filter_capped

			# time.sleep(1)

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
	print('original candidate ratio: ', len(candidate_set)/(len(candidate_set)+index.duplicate_candidate_count) if len(candidate_set) > 0 else '?')
	return candidate_set


def output_tuple():
	pass


def remove_reflexive_candidates(candidates, arguments, index_to_id_map, id_to_names_map):
	if not arguments.inverts:
		# print('A CASE')
		return {x for x in candidates if x[0] != x[1]}
	else:
		# print('B CASE')
		ret = set()
		for x in candidates:
			id_a = index_to_id_map[x[0]]
			id_b = index_to_id_map[x[1]]

			#if not matching a string with itself (flipped or otherwise)
			if (id_to_names_map[id_a] != id_to_names_map[id_b]):
				ret.add(x)
		return ret

def verifies(candidate, T, b_len, arguments):
	#TODO make sure the b_len arg is correctly giving the length of string B (suffix / found) string
	try:
		a_index, b_index, a_ovr, b_ovr, b_tail, debug_str = candidate
		errs_allowed = math.floor(max(a_ovr, b_ovr)*arguments.e)
		b_ovr_start = b_index - b_ovr - b_tail + b_len
		# print(candidate)
		a_ovr_string = T[a_index : a_index + a_ovr]
		b_ovr_string = T[b_ovr_start : b_ovr_start + b_ovr]

		# print('a_ovr_string', a_ovr_string)
		# print('b_ovr_string', b_ovr_string)

		if arguments.indels:
			ed, cigar = edit_distance(a_ovr_string, b_ovr_string)
			return (ed if ed <= errs_allowed else -1), cigar
		else: #hamming
			assert a_ovr == b_ovr
			err_count = 0
			for i in range(a_ovr):
				if T[a_index+i] != T[b_ovr_start+i]:
					err_count += 1
			return err_count if err_count <= errs_allowed else -1, cigar_strings.cigar_for_match_of_len(a_ovr)
	except:
		#out of string bounds exception
		print('OH CRAP, out of bounds verify!! oh noes!')
		raise

def companion_index(x):
	if x%2==0: return x+1
	return x-1

def redundant_solutions(a, b):
	for i in range(len(a)-1): #chop off cigar
		if a[i] != b[i]:
			return False
	print("REDUNDANT!")
	print(a)
	print(b)
	return True

def sort_and_deduplicate_solutions(solution_set):
	ret = []
	p = None,None,None,None,None,None,None,None,None
	for x in sorted(solution_set):
		if not redundant_solutions(p, x):
			ret.append(x)
			p = x
	return ret

def get_solutions(candidate_set, S_dict, T, arguments, mappings):
	solution_set = set()
	for candidate in candidate_set:
		# time.sleep(.2)
		# print('\n\n\n >')
		# print('cand', candidate)
		b_len = mappings.index2len[candidate[1]]
		k, cigar = verifies(candidate, T, b_len, arguments)
		a_len = mappings.index2len[candidate[0]]

		a_index, b_index, a_ovr, b_ovr, b_tail, debug_str = candidate

		if k != -1: #-1 errors means 'too many to verify'
			#solution accepted
			print('\n\n\n>')
			print(T)
			print(debug_aux.carat_chars(range(a_index, a_index + a_len), len(T) + 5))
			print(debug_aux.carat_chars(range(b_index, b_index + b_len), len(T) + 5))
			a_id = mappings.index2id[a_index]
			b_id = mappings.index2id[b_index]
			if b_ovr+b_tail > b_len:
				#blind spot overlapping ???[MMMMM]~~~~~~~~
				#                         ~~MMMMM
				print('blind spot overlapping! DISCARD')
				continue
			print(a_id, 'pref', T[a_index:a_index+a_len])
			print(b_id, 'suff', T[b_index:b_index+b_len])
			print('b_tail!!!', b_tail)
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
			print('initIDS', a_id, b_id)
			print(T)
			print(' :  ', '^'*-OHA + T[a_index:a_index+a_len] + '*'*(b_ovr-a_ovr) + '~'*OHB)
			print(' :  ', '^'*OHA + T[b_index:b_index+b_len] + '*'*(a_ovr-b_ovr) + '~'*-OHB)

			if a_id > b_id:	# ensure smaller string comes first
				print('smaller first! VFLIP')
				OHA *= -1
				OHB *= -1
				a_len, b_len = b_len, a_len
				a_id, b_id, OLA, OLB = b_id, a_id, OLB, OLA
				a_index, b_index = b_index, a_index
				cigar.v_flip()
			print('tIDS', a_id, b_id)
			print(T)
			print(' :  ', '^' * -OHA + T[a_index:a_index + a_len] + '*' * (b_ovr - a_ovr) + '~' * OHB)
			print(' :  ', '^' * OHA + T[b_index:b_index + b_len] + '*' * (a_ovr - b_ovr) + '~' * -OHB)
			if arguments.inverts and a_id % 2 == 1:	#guarantee not BOTH are flipped
				print('a must be non-neg! HFLIP')
				OHA, OHB = -OHB, -OHA
				a_id = companion_index(a_id)
				b_id = companion_index(b_id)
				a_index = mappings.id2index[a_id]
				b_index = mappings.id2index[b_id]
				cigar.h_flip()

			print('TRANSFORMS COMPLETE')
			print('tIDS', a_id, b_id)
			print(T)
			print(' :  ', '^'*-OHA + T[a_index:a_index+a_len] + '*'*(b_ovr-a_ovr) + '~'*OHB)
			print(' :  ', '^'*OHA + T[b_index:b_index+b_len] + '*'*(a_ovr-b_ovr) + '~'*-OHB)
			CIGAR = cigar
			K = k
			O = 'N' if not arguments.inverts or b_id%2==0 else 'I'
			a_name = mappings.id2names[a_id]
			b_name = mappings.id2names[b_id]
			solution = (a_name, b_name, O, OHA, OHB, OLA, OLB, K, CIGAR)
			print_solution(solution, S_dict)
			solution_set.add(solution)
		else:
			pass
			# print('DID NOT VERIFY. TOO MANY ERRORS')


	deduplicated = sort_and_deduplicate_solutions(solution_set)
	print(len(solution_set), 'solutions')
	print(len(deduplicated), 'solutions after deduplication')
	return deduplicated

'''
Given S_dict, a dict with values being strings.
The keys for these values give the external names for these strings.
Outputs should return overlaps in this format
'''
def overlaps(S_dict, arguments):

	t0 = time.clock()
	# T, sorted_alphabet, indels, inclusions, candidate_set, thresh, condition_met_f

	id2names = dict()
	sorted_names = sorted(S_dict.keys())
	num_inputs = len(S_dict.keys())

	for id, name in enumerate(sorted_names):
		if not arguments.inverts:
			id2names[id] = name
		else:
			id2names[id*2] = name
			id2names[(id*2)+1] = name


	sorted_ids = range(num_inputs*2 if arguments.inverts else num_inputs)
	# WUT = sorted(id_to_names_map.keys())
	# print("WUT", WUT)
	# print("WUT2", WUT2)
	S = [S_dict[id2names[key]]
		for key in sorted_ids]\
		if not arguments.inverts\
		else [S_dict[id2names[key]]
			  if key%2==0 else prog_alphabet.invert(S_dict[id2names[key]])
			  for key in sorted_ids]

	print(S)
	T = ''
	id2index = dict()
	index2id = dict()
	for i, s in enumerate(S):
		id2index[i] = len(T)
		index2id[len(T)] = i
		T = T + s + '$'
	# print('T', T)
	# print('index_to_id_map', index_to_id_map)
	# print('id_to_index_map', id_to_index_map)
	# print()

	index2len = dict()
	for i, string in enumerate(S):
		index2len[id2index[i]] = len(string)

	mappings = structs.Mappings(id2names, id2index, index2len, index2id)

	t1 = time.clock()
	print('input time', t1-t0)
	#STEP 1
	candidate_set = find_candidates(S, T, arguments, mappings)
	print('candidate_set', candidate_set)
	print('index_to_id_map',index2id)

	candidate_set = remove_reflexive_candidates(candidate_set, arguments, index2id, id2names)


	t2 = time.clock()
	print('step1 time', t2-t1)
	#STEP 2
	solution_set = get_solutions(candidate_set, S_dict, T, arguments, mappings)

	t3 = time.clock()
	print('\n\n\n ------->')
	print('step2 time', t3-t2)
	# print('candidate_set', candidate_set)
	# print('verified_set', verified_set)
	print('num candidates:', len(candidate_set))
	print('num verified:', len(solution_set))
	print('step 1 precision', len(solution_set) / (len(candidate_set)) if len(candidate_set) > 0 else 1)
	print('verified set', solution_set)

	return solution_set


'''SCRIPT BEGIN'''


arguments = structs.Arguments(indels=False,
					  inclusions=True,
					  inverts=False,
					  e=0.02,
					  thresh=20,
					  in_path='data/basic.fasta',
					  out_path='data/out.txt')


random.seed(400)
x = prog_io.rd(arguments.in_path)
print(x)
# exit(1)
S_dict = x
# S_dict = {0:'AAAAAGGGGGGGGG', 1:'GTGGTCCCCCAAAAA', 2:'CCCCC'}
solutions = overlaps(S_dict, arguments)
print('\n\n====SOLUTIONS====\n\n')
with open(arguments.out_path, "w") as text_file:
	text_file.write('ID1\tID2\tO\tOHA\tOHB\tOLA\tOLB\tK\tCIG\n')
	for sol in solutions:
		text_file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(*sol))
	text_file.close()
	print('WRITE DONE! wrote {} solutions!'.format(len(solutions)))

# print('not printing')
for sol in solutions:
	print()
	print_solution(sol, S_dict, debug=False)
#TODO output in proper format, printing to file
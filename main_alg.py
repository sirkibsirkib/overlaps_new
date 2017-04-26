import time

# import valimaki_2 as specific
import kucherov as specific
from ed import distance_alignment as edit_distance
from prog_args import Arguments
from read_data import rd
import debug_aux
import math

from index_searcher import FMIndex as fm_index

'''AUX FUNCTIONS and CLASSES'''



def align_using_cigar(a, b, cigar):
	print("\nCIGAR BABY")
	print('a', a)
	print('b', b)
	print('cigar', cigar)
	print('len a', len(a))
	print('leb b', len(b))
	a_cigar = ''
	b_cigar = ''
	a_i = 0
	b_i = 0
	while len(cigar) > 0:
		print('CIGAR IS NOW', '[' + cigar + ']')
		num_len = 0
		while cigar[:num_len+1].isdigit():
			num_len += 1
		n = int(cigar[:num_len])
		code = cigar[num_len]
		cigar = cigar[num_len+1:]

		print('code', '[' + code + ']')
		print('n', '[' + str(n) + ']')
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
	pass
	# # TODO candidates have been changed!
	# a_index, b_index, a_ovr, b_ovr, , cigar, debug_str = sol
	# print('sol', sol)
	# a = S_dict[sol[0]]
	# if sol[6]: a = a[::-1]
	# b = S_dict[sol[1]]
	# if sol[7]: b = b[::-1]
	# print('a (pref) = ' +a)
	# print('b (suff) = ' +b)
	# a_head = a[:len(a)-sol[2]]
	#  = b[sol[3]:]
	# cigar = sol[5]
	# a_aligned, b_aligned = align_using_cigar(a[-sol[2]:], b[:sol[3]], cigar)
	# print(a_head + '(' + a_aligned + ')')
	# print(((len(a_head)) * ' ') + '(' + b_aligned + ')' + )
	# print()

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

def verifies(candidate, T, b_len, arguments):
	#TODO make sure the b_len arg is correctly giving the length of string B (suffix / found) string
	try:
		a_index, b_index, a_ovr, b_ovr, b_tail, debug_str = candidate
		errs_allowed = math.floor(max(a_ovr, b_ovr)*arguments.e)
		b_ovr_start = b_index - b_ovr - b_tail + b_len
		# print(candidate)
		a_ovr_string = T[a_index : a_index + a_ovr]
		b_ovr_string = T[b_ovr_start : b_index + b_ovr - b_tail]

		if arguments.indels:
			ed, cigar = edit_distance(a_ovr_string, b_ovr_string)
			return (ed if ed <= errs_allowed else -1), cigar
		else: #hamming
			assert a_ovr == b_ovr
			err_count = 0
			for i in range(a_ovr):
				if T[a_index+i] != T[b_ovr_start+i]:
					err_count += 1
			return err_count if err_count <= errs_allowed else -1, str(a_ovr) + 'M'
	except:
		#out of string bounds exception
		print('OH CRAP, out of bounds verify!! oh noes!')
		raise

def get_solutions(candidate_set, S_dict, T, index_to_length_map, index_to_id_map, id_to_names_map, arguments):
	solution_set = set()
	for candidate in candidate_set:
		b_len = index_to_length_map[candidate[1]]
		k, cigar = verifies(candidate, T, b_len, arguments)

		if k != -1: #-1 errors means 'too many to verify'
			#solution accepted
			print('\n\n\n>')
			a_len = index_to_length_map[candidate[0]]
			a_index, b_index, a_ovr, b_ovr, b_tail, debug_str = candidate
			print('pref', T[a_index:a_index+a_len])
			print('suff', T[b_index:b_index+b_len])
			a_id = index_to_id_map[a_index]
			b_id = index_to_id_map[b_index]


			OLA = a_ovr
			OLB = b_ovr
			OHA = -(a_len - a_ovr)
			OHB = -(b_len - b_ovr) if b_tail == 0 else b_tail
			if a_id % 2 == 1:
				OHA *= -1
				OHB *= -1
				a_id, b_id = b_id, a_id

			CIGAR = cigar
			K = k
			O = 'N' if b_id%2==0 else 'I'
			a_name = id_to_names_map[a_id]
			b_name = id_to_names_map[b_id]
			solution = (a_name, b_name, O, OHA, OHB, OLA, OLB, K, CIGAR)
			print('a\tb\tO\tOHA\tOHB\tOLA\tOLB\tK\tCIG')
			print(*solution, sep='\t')
			print(candidate)
			print(' ==> ', solution)
			print(' '*(-OHA), S_dict[a_name])
			second = S_dict[b_name] if O=='N' else S_dict[b_name][::-1]
			print(' '*OHA, second)

	return sorted(solution_set)

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
	solution_set = get_solutions(candidate_set, S_dict, T, index_to_length_map, index_to_id_map, id_to_names_map, arguments)

	t3 = time.clock()
	print('step2 time', t3-t2)
	# print('candidate_set', candidate_set)
	# print('verified_set', verified_set)
	print('num candidates:', len(candidate_set))
	print('num verified:', len(solution_set))
	print('step 1 precision', len(solution_set) / (len(candidate_set)) if len(candidate_set) > 0 else 1)
	print('verified set', solution_set)

	return sorted(solution_set)


'''SCRIPT BEGIN'''


arguments = Arguments(indels=False, inclusions=False, inverts=True, e=0.22, thresh=5)


x = rd('data/basic.fasta')
print(x)
# exit(1)
# S_dict = x
S_dict = {0:'AAAAABBBBB', 1:'BBBBBCCCCC', 2:'CCCCCDDDDD', 3:'XXXXXXXXXX'}
# S_dict = {0:'hannahismyname', 1:'igobyhannah', 2:'hanahisavalidspelling', 3:'spellingisfun'}
solutions = overlaps(S_dict, arguments)
# print('\n\n====SOLUTIONS====\n\n')
# for sol in solutions:
# 	print_solution(sol)

#TODO output in proper format, printing to file
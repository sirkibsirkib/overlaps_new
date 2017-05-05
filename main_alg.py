import time
import solution_builder
# import valimaki_2 as specific
import kucherov as specific
from ed import distance_alignment as edit_distance
import structs
import prog_io
import debug_aux
import math
import prog_alphabet
import cigar_strings
import benchmarking
import random
from functools import partial
import os
from index_searcher import FMIndex as fm_index
from itertools import repeat
from multiprocessing.pool import Pool as ThreadPool


'''MAIN FUNCTIONS'''

def block_id_and_error_lookups(suffix_parts, filter, max_B_len, error_hard_cap):
	block_id_lookup = []
	error_lookup = []
	for i in range(len(suffix_parts)):
		for _ in range(suffix_parts[i]):
			err = min(filter[i], error_hard_cap)
			block_id_lookup.append(i)
			error_lookup.append(err)
	last_block_index = len(suffix_parts)
	while len(block_id_lookup) < max_B_len:
		block_id_lookup.append(last_block_index)
		error_lookup.append(error_hard_cap)
	return block_id_lookup, error_lookup

def worker_CAND(p_id):
	global g_S, g_T, g_index, g_mappings, g_arguments
	worker_write_candidates(g_S, g_T, g_index, p_id, g_mappings, g_arguments)


def worker_write_candidates(S, T, index, p_id, mappings, arguments):
	patt = S[p_id]
	candidate_set = set()
	file_name = 'temp/' + str(p_id) + '.cands'

	skip_work = (arguments.use_existing_cands_files and os.path.exists(file_name))\
				or len(patt) < arguments.thresh
	skip_writing = (arguments.use_existing_cands_files and os.path.exists(file_name))

	if not skip_work:
		block_lengths, filters = specific.get_block_lengths_and_filters(len(patt), arguments.e, arguments.thresh)
		assert sum(block_lengths) == len(patt)  # making sure partition lengths are sound
		p_T_index = mappings.id2index[p_id]
		error_hard_cap = math.floor(len(patt) * arguments.e)
		max_B_len = len(patt) if not arguments.indels else math.floor(len(patt) / (1 - arguments.e))
		for filter in filters:
			first_block_index = len(block_lengths) - len(filter)
			p_i_start = sum(block_lengths[:first_block_index])
			block_id_lookup, error_lookup = block_id_and_error_lookups(block_lengths[first_block_index:], filter, max_B_len,
																	   error_hard_cap)
			index.forward_search(candidate_set, patt, p_i_start, p_T_index, p_id, error_lookup, block_id_lookup)
	prohibited_ids = [p_id]
	if arguments.inverts:
		prohibited_ids.append(solution_builder.companion_index(p_id))

	if not skip_writing:
		with open(file_name, "w") as c_file:
			for c in candidate_set:
				match_id = mappings.index2id[c[1]]
				if match_id not in prohibited_ids:
					written_cand = '{}\t{}\t{}\t{}\n'.format(match_id, c[2], c[3], c[4])
					c_file.write(written_cand)



def write_candidates(S, T, arguments, mappings):

	if not os.path.exists('temp'):
		os.makedirs('temp')
	pool = ThreadPool(arguments.step1_threads)
	index = fm_index(T, specific.conditions_met, arguments, mappings, len(S))
	global g_S, g_T, g_index, g_mappings, g_arguments
	g_S = S
	g_T = T
	g_index = index
	g_mappings = mappings
	g_arguments = arguments

	#		SINGLE THREADED MODE
	# for p_id in range(len(S)):
	# 	worker_write_candidates(S, T, index, p_id, mappings, arguments)

	#		MULTI THREADED MODE
	# pool.map(worker_CAND, range(len(S)))
	pool.starmap(worker_write_candidates, zip(repeat(S), repeat(T), repeat(index), range(len(S)), repeat(mappings), repeat(arguments)))

	# candidate_set = set()
	# for p_id, patt in enumerate(S):
	# 	if len(patt) < arguments.thresh:
	# 		#skip patterns too small to match
	# 		continue
	#
	# 	block_lengths, filters = specific.get_block_lengths_and_filters(len(patt), arguments.e, arguments.thresh)
	# 	assert sum(block_lengths) == len(patt) #making sure partition lengths are sound
	# 	p_T_index = mappings.id2index[p_id]
	# 	# print("NEXT PATT:")
	# 	# print(T)
	# 	# print(debug_aux.carat_chars([p_T_index], 50))
	# 	# print('{} / {}'.format(p_id+1, len(S)))
	# 	# print(patt)
	#
	# 	error_hard_cap = math.floor(len(patt)*arguments.e)
	# 	max_B_len = len(patt) if not arguments.indels else math.floor(len(patt)/(1-arguments.e))
	#
	# 	# print('FILTERS')
	# 	for filter in filters:
	# 		# print('filter', filter)
	#
	# 		# filter_capped = [min(error_hard_cap, x) for x in filter]
	# 		# print('FILTER UNCAPPED', filter)
	# 		# print('FILTER CAPPED', filter_capped)
	# 		# print('patt len', len(filter))
	#
	# 		# filter = filter_capped
	#
	# 		# time.sleep(1)
	#
	# 		first_block_index = len(block_lengths)-len(filter)
	# 		p_i_start = sum(block_lengths[:first_block_index])
	# 		# print()
	# 		# print(patt, '    <---- patt')
	# 		# print(debug_aux.carat_chars([p_i_start], len(patt)), '    <---- suffix start')
	#
	# 		#FILTER NOT AFFECTED BY ERROR CAP. ERROR LOOKUP IS
	# 		block_id_lookup, error_lookup = block_id_and_error_lookups(block_lengths[first_block_index:], filter, max_B_len, error_hard_cap)
	# 		# print((' '*p_i_start) + (''.join(map(lambda x : str(x), block_id_lookup))), '    <--- block IDs')
	# 		# print((' '*p_i_start) + (''.join(map(lambda x : str(x), error_lookup))), '    <--- cumulative allowed errors')
	# 		index.forward_search(candidate_set, patt, p_i_start, p_T_index, p_id, error_lookup, block_id_lookup)
	#
	# 	write_candidates_for_patt(p_id, candidate_set, arguments, mappings)

	# print('total nodes: ', index.nodes)
	# print('total duplicate candidates: ', index.duplicate_candidate_count)
	# print('original candidate ratio: ', len(candidate_set)/(len(candidate_set)+index.duplicate_candidate_count) if len(candidate_set) > 0 else '?')




# def remove_reflexive_candidates(candidates, arguments, mappings):
# 	if not arguments.inverts:
# 		return {x for x in candidates if x[0] != x[1]}
# 	else:
# 		ret = set()
# 		for x in candidates:
# 			id_a = mappings.index2id[x[0]]
# 			id_b = mappings.index2id[x[1]]
# 			#if not matching a string with itself (flipped or otherwise)
# 			if (mappings.id2names[id_a] != mappings.id2names[id_b]):
# 				ret.add(x)
# 		return ret

def verifies(candidate, T, b_len, arguments):
	#TODO make sure the b_len arg is correctly giving the length of string B (suffix / found) string
	try:
		a_index, b_index, a_ovr, b_ovr, b_tail, debug_str = candidate
		errs_allowed = math.floor(max(a_ovr, b_ovr)*arguments.e)
		b_ovr_start = b_index - b_ovr - b_tail + b_len
		a_ovr_string = T[a_index : a_index + a_ovr]
		b_ovr_string = T[b_ovr_start : b_ovr_start + b_ovr]

		if arguments.indels:
			if len(a_ovr_string) < 2 or len(b_ovr_string) < 2:
				return -1, 'NO_CIG'
			ed, cigar = edit_distance(a_ovr_string, b_ovr_string)
			return (ed if ed <= errs_allowed else -1), cigar
		else: #hamming
			assert a_ovr == b_ovr
			err_count = 0
			for i in range(a_ovr):
				if T[a_index+i] != T[b_ovr_start+i] or T[a_index+1]=='N':
					err_count += 1
			return err_count if err_count <= errs_allowed else -1, cigar_strings.cigar_for_match_of_len(a_ovr)
	except :
		#out of string bounds exception
		print('OH CRAP, out of bounds verify!! oh noes!')
		raise


def redundant_solutions(a, b):
	for i in range(len(a)-1): #chop off cigar
		if a[i] != b[i]:
			return False
	return True

def sort_and_deduplicate_solutions(solution_set):
	ret = []
	p = None,None,None,None,None,None,None,None,None
	for x in sorted(solution_set):
		if not redundant_solutions(p, x):
			ret.append(x)
			p = x
	return ret


def worker_verify(T, patt_id, mappings, arguments):
	# at the end of this, the set at solution_piles[patt_id] will contain all verified solutions
	result = set()
	file_name = 'temp/' + str(patt_id) + '.cands'
	with open(file_name, 'r') as input:
		file_data = list(line.strip().split('\t') for line in input)

		cands = [[mappings.id2index[patt_id], mappings.id2index[int(lst[0])], int(lst[1]), int(lst[2]), int(lst[3]), '']
				 for lst in file_data]

		for candidate in cands:
			b_len = mappings.index2len[candidate[1]]
			k, cigar = verifies(candidate, T, b_len, arguments)
			a_len = mappings.index2len[candidate[0]]
			if k == -1:
				continue
			sol = solution_builder.candidate_to_solution(candidate, a_len, b_len, cigar, k, arguments, mappings)
			if sol != None:
				result.add(sol)
			# solution_set.add(sol)
	return result

def verify_and_translate(num_ids, S_dict, T, arguments, mappings):
	pool = ThreadPool(arguments.step2_threads)

	#		SINGLE THREADED MODE
	result_list = map(lambda x : worker_verify(T, x, mappings, arguments), range(num_ids))

	#		MULTI THREADED MODE
	# result_list = pool.map(lambda x : worker_verify(T, x, mappings, arguments), range(num_ids))
	result_list = pool.starmap(worker_verify, zip(repeat(T), range(num_ids), repeat(mappings), repeat(arguments)))

	# for patt_id in range(num_ids):
	#
	# 	#ONE THREAD TASK PER PATT_ID
	# 	file_name = 'temp/' + str(patt_id) + '.cands'
	# 	with open(file_name, 'r') as input:
	# 		file_data = list(line.strip().split('\t') for line in input)
	#
	# 		cands = [[mappings.id2index[patt_id], mappings.id2index[int(lst[0])], int(lst[1]), int(lst[2]), int(lst[3]), '']
	# 				 for lst in file_data]
	#
	# 		for candidate in cands:
	# 			b_len = mappings.index2len[candidate[1]]
	# 			k, cigar = verifies(candidate, T, b_len, arguments)
	# 			a_len = mappings.index2len[candidate[0]]
	# 			if k == -1:
	# 				continue
	# 			sol = solution_builder.candidate_to_solution(candidate, a_len, b_len, cigar, k, arguments, mappings)
	# 			if sol != None:
	# 				solution_piles[patt_id].add(sol)
	# 				# solution_set.add(sol)


	# WAIT FOR THREADS TO JOIN
	# solution_set = set.union(*solution_piles)
	solution_set = set.union(*result_list)

	deduplicated = sort_and_deduplicate_solutions(solution_set)
	print(len(solution_set), 'solutions')
	print(len(deduplicated), 'solutions after deduplication')
	return deduplicated


def build_maps_and_internals(sorted_ids, S_dict, arguments):
	id2names = dict()
	sorted_names = sorted(S_dict.keys())
	for id, name in enumerate(sorted_names):
		if not arguments.inverts:
			id2names[id] = name
		else:
			id2names[id * 2] = name
			id2names[(id * 2) + 1] = name
	S = [S_dict[id2names[key]]
		 for key in sorted_ids] \
		if not arguments.inverts \
		else [S_dict[id2names[key]]
			  if key % 2 == 0 else prog_alphabet.invert(S_dict[id2names[key]])
			  for key in sorted_ids]
	T = ''
	id2index = dict()
	index2id = dict()
	for i, s in enumerate(S):
		id2index[i] = len(T)
		index2id[len(T)] = i
		T = T + s + '$'
	index2len = dict()
	for index in index2id.keys():
		id = index2id[index]
		name = id2names[id]
		index2len[index] = len(S_dict[name])
	mappings = structs.Mappings(id2names, id2index, index2len, index2id)
	return mappings, S, T


# def print_stats(len_cand_set, len_sol_set):
# 	print('num candidates:', len_cand_set)
# 	print('num verified:', len_sol_set)
# 	print('step 1 precision', len_sol_set / len_cand_set if len_cand_set > 0 else 1)

'''
Given S_dict, a dict with values being strings.
The keys for these values give the external names for these strings.
Outputs should return overlaps in this format
'''
def overlaps(S_dict, arguments):
	benchmarker = benchmarking.Benchmarker()
	num_inputs = len(S_dict)
	num_ids = num_inputs * 2 if arguments.inverts else num_inputs
	sorted_ids = range(num_ids)

	mappings, S, T = build_maps_and_internals(sorted_ids, S_dict, arguments)
	benchmarker.log_moment("Reading input")
	#STEP 1
	write_candidates(S, T, arguments, mappings)
	benchmarker.log_moment("cands written")
	# candidate_set = remove_reflexive_candidates(candidate_set, arguments, mappings)
	# benchmarker.time("CANDIDATE SET (reflexives removed)")

	#STEP 2
	solution_set = verify_and_translate(num_ids, S_dict, T, arguments, mappings)
	benchmarker.log_moment("solutions & output")
	global cand_count
	# print_stats(len(candidate_set), len(solution_set))

	# print('<{}>'.format(benchmarker.log))

	print()
	print(benchmarker)

	return solution_set






'''SCRIPT BEGIN'''


arguments = structs.Arguments(indels=True,
					inclusions=False,
					inverts=False,
					e=0.41,
					thresh=5,
					in_path='data/basic.fasta',
					out_path='data/out.txt',
					step1_threads=4,
					step2_threads=4,
					use_existing_cands_files=False
					)

if __name__ == '__main__':
	random.seed(400)
	raw_dict = prog_io.rd(arguments.in_path)

	raw_dict = {0:'AAAATTTNTT', 1:'TTTTCCCC', 2:'GGGGTTTNNTT'}
	S_dict = prog_alphabet.prepare(raw_dict)
	print(S_dict)
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
		debug_aux.print_solution(sol, S_dict, debug=False)
	#TODO output in proper format, printing to file
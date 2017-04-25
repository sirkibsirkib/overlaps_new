from math import ceil


class Candidates:
	def __init__(self):
		self.tups = []

	def add_cand(self, x):
		if x not in self.tups:
			self.tups.append(x)

	def __repr__(self):
		return 'Candidates: ' + str(self.tups)

	def clear(self):
		self.tups = []

class FMIndex:
	def __init__(self, T, sorted_alphabet):
		SAT = [i for i in range(len(T))]
		sSAT = sorted(SAT, key=lambda x : T[x:]+ T[:x])
		self.F = L = ''.join(T[sSAT[i]] for i in range(len(T)))
		L = ''.join(T[sSAT[i]-1] for i in range(len(T)))

		C = dict()
		dollar_count = T.count('$')
		count = 0
		for a in sorted_alphabet:
			C[a] = count+dollar_count
			count += T.count(a)

		self.C = C
		self.L = L
		self.sSAT = sSAT
		self.sorted_alphabet = sorted_alphabet

	#this use less space with use of checkpoints
	def rank(self, c, i):
		return self.L[:i].count(c)


	#change prefixes_only arg to check for the prefixes
	def k_mismatch_recurse(self, cand, P, j, sp, ep, debug_str, pattern_index, errors_at_index_list, errors_so_far, char_index, thresh, cutoff):
		# print('j',j)
		# print('[...'+debug_str+']   from ', sp, 'to', ep)
		if sp > ep: #stop. no matches
			return
		#TODO why is it not finding longer patterns?
		if char_index + cutoff >= thresh\
			and errors_at_index_list[char_index] > 0:	#quick an dirty solution for checking if we are in the ZERO block
			for x in [(self.sSAT[i], pattern_index, char_index+cutoff, errors_so_far) for i in range(sp, ep + 1)
						if (self.L[i] == '$')
							and (self.sSAT[i] != pattern_index)]:
				cand.add_cand(x)

		if j == 0: # ran out of string
			return
		# print('this char is ', P[j], 'errors', errors_so_far, 'chars', char_index, 'err_ind', errors_at_index_list)
		#add things to RET here if you want to generate candidates early
		for a in self.sorted_alphabet:
			sp_ = self.C[a] + self.rank(a, sp)
			ep_ = self.C[a] + self.rank(a, ep + 1) - 1
			errors_so_far_ = errors_so_far if P[j] == a else errors_so_far+1
			# print('a', a, 'errors_so_far_', errors_so_far_, 'errors_at_index_list[char_index]',
			# 	  errors_at_index_list[char_index], errors_so_far_ <= errors_at_index_list[char_index])
			if errors_so_far_ <= errors_at_index_list[char_index]:
				self.k_mismatch_recurse(cand, P, j-1, sp_, ep_, a+debug_str, pattern_index, errors_at_index_list, errors_so_far_, char_index+1, thresh, cutoff)


	def k_mismatches(self, cand, P, rightmost_char_index, pattern_index, errors_at_index_list, thresh, cutoff):
		self.k_mismatch_recurse(cand, P, rightmost_char_index, 0, len(self.L)-1, '', pattern_index, errors_at_index_list, 0, 0, thresh, cutoff)


def sorted_alph_of(T):
	s = set()
	for t in T:
		for c in t:
			s.add(c)
	return sorted(list(s))


def part_lengths(length, thresh, e):
	p_ = [    ceil(l*1.0 / (ceil(e * l) + 1))
			 for l in range(thresh, length+1)]
	try:
		p = min(p_)
	except:
		print('!!!!!!!!!!', p_)
		exit(1)
	print('  ', list(range(thresh, length+1)))
	print('p_', p_)
	remain = length
	ret = []
	while(remain > 0):
		next = min(remain, p)
		ret.append(next)
		remain -= next
		ret.reverse()
	print('part_lengths', ret)
	return ret

def errors_allowed_mode2(part_len_list, first_suffix):
	tot = 0
	ret = []
	for part in part_len_list:
		ret.append(tot)
		tot += 1
	print('ret', ret)
	return ret

def errors_allowed_mode1(part_len_list, first_suffix):
	tot = 0
	ret = []
	for part in part_len_list:
		ret.append(tot)
		tot += 1
	print('ret', ret)
	return ret

def errors_at_index(part_len_list, first_suffix, filter_get_function = errors_allowed_mode1):
	print('suff first?', first_suffix)
	errors_allowed_list = filter_get_function(part_len_list, first_suffix)
	ret = []

	rev = part_len_list[:]
	rev.reverse()
	for length, errors in zip(rev, errors_allowed_list):
		for _ in range(length):
			ret.append(errors)
	return ret

def overlaps(S, e, thresh):
	alph = sorted_alph_of(S)
	T = concat_raw_strings(S)
	print('T', T)
	index = FMIndex(T, alph)

	cand = Candidates()
	for patt in S:
		print()
		if len(patt) < thresh:
			continue
		print('\tPATT:', patt)
		part_len_list = part_lengths(len(patt), thresh, e)
		print('part_len_list', part_len_list)
		patt_index = T.index(patt)  # T<-- TODO finds index of current pattern in string to avoid self-match
		cutoff = 0

		first_suffix = True
		for last_part_index in range(len(part_len_list)-1, -1, -1):
			print()

			patt_str = patt[:len(patt)-cutoff]
			print('last_part_index', last_part_index)
			print('cutoff', cutoff)
			rightmost_char_index = len(patt)-cutoff-1
			print('== patt ==', patt)
			print('== ppre ==', patt[:rightmost_char_index+1])
			errors_at_index_list = errors_at_index(part_len_list[:last_part_index+1], first_suffix)
			e2 = errors_at_index_list[:]
			e2.reverse()
			print('== errs ==', ''.join(map(lambda x : str(x), e2)))

			index.k_mismatches(cand, patt_str, rightmost_char_index, patt_index, errors_at_index_list, thresh, cutoff)
			cutoff += part_len_list[last_part_index]
			print(cand)
			first_suffix = False

			for tup in cand.tups:
				print(T)
				patt_ovr_start = tup[1]-tup[2]+len(patt)
				other_ovr_start = tup[0]
				s = ''.join(['P' if (i >= other_ovr_start and i < other_ovr_start+tup[2])else ' '
							 for i in range(len(T)+5)])
				s2 = ''.join(['S' if (i >= patt_ovr_start and i < patt_ovr_start+tup[2])
							 else ' '
							  for i in range(len(T) + 5)])

				print(s2)
				print(s)
			# cand.clear()

			#TODO clean up the printing

	print(cand)








def concat_raw_strings(strings):
	return '$'.join(strings) + '$'


# x = rd('data/basic.fasta')
# print(x)
# S = x.values()
#
# # when |string| == t, shit goes down
#
# print("S", S)
#
# overlaps(S, .02, 20)

#
# S = {'aaabbb', 'xbbccc'}
# overlaps(S, .04, 3)
print(part_lengths(5, 5 , (1/5)))
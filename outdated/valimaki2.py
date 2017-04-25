
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
	def k_mismatch_recurse(self, P, k, j, sp, ep, debug_str, pattern_index, overlap_len, prefixes_only=True):
		# print('[...'+debug_str+']   from ', sp, 'to', ep)
		if sp > ep: #stop. no matches
			return []
		#TODO why is it not finding longer patterns?
		ret = [(self.sSAT[i], pattern_index, overlap_len) for i in range(sp, ep + 1)
					if (self.L[i] == '$' or not prefixes_only)
				   		and (self.sSAT[i] != pattern_index)]\
				if overlap_len >= 3 else []

		if j == 0:
			return ret
		#add things to RET here if you want to generate candidates early
		for a in self.sorted_alphabet:
			sp_ = self.C[a] + self.rank(a, sp)
			ep_ = self.C[a] + self.rank(a, ep + 1) - 1
			k_ = k if P[j] == a else k-1
			if k_ >= 0:
				ret += self.k_mismatch_recurse(P, k_, j-1, sp_, ep_, a+debug_str, pattern_index, overlap_len+1)
		return ret


	def k_mismatches(self, P, k, pattern_index):
		return self.k_mismatch_recurse(P, k, len(P)-1, 0, len(self.L)-1, '', pattern_index, 0)


def sorted_alph_of(T):
	s = set()
	for t in T:
		for c in t:
			s.add(c)
	return sorted(list(s))

def part_lengths(patt_len):
	#given an int for pattern length, return an index of ints, such that each represents the lengths of partitions 0, 1, ... k+1
	even_size = 3
	remainder = [patt_len%even_size]
	return [even_size for i in range(patt_len//even_size)] + ([] if remainder[0]==0 else remainder)

	#TODO ask how partitions fit in with these suffixes? Does first block get explored first or last?

def overlaps(S):
	alph = sorted_alph_of(S)
	T = concat_raw_strings(S)
	num_errors = 1
	print('T', T)
	index = FMIndex(T, alph)
	print('simple example. error is fixed at <=',num_errors,'.\nshowing suffix prefix overlaps')
	for patt in S:
		print('\tPATT:', patt)
		patt_index = T.index(patt)
		tups = index.k_mismatches(patt, num_errors, patt_index)
		print('matches for this patt as suffix:', tups)
		for tup in tups:
			print(T)
			patt_ovr_start = tup[1]-tup[2]+len(patt)
			other_ovr_start = tup[0]
			s = ''.join(['^' if (i >= other_ovr_start and i < other_ovr_start+tup[2])
								or (i >= patt_ovr_start and i < patt_ovr_start+tup[2])
						 else ' '
						 for i in range(len(T))])
			print(s)

def concat_raw_strings(strings):
	return '$'.join(strings) + '$'

S = ['1100000', '0000022']
print("S", S)

print(part_lengths(34))

overlaps(S)
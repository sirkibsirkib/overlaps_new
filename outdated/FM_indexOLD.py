
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

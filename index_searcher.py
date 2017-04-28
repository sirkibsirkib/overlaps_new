import debug_aux
import cigar_strings

def sorted_alphabet_of(T):
	s = set()
	for c in T:
		if c != '$':
			s.add(c)
	return sorted(list(s))

class FMIndex:

	def get_checkpoints(self):
		alph2 = (self.sorted_alphabet + ['$'])
		checkpoints = dict()
		counts = {a: 0 for a in alph2}
		for a in alph2:
			checkpoints[a] = []
		for i, a in enumerate(self.L):
			if i % self.checkpoint_spacing == 0:
				for z in alph2:
					checkpoints[z].append(counts[z])
			counts[a] += 1
		for z in alph2:
			checkpoints[z].append(counts[z])
		# print('counts')
		# print(' ', '    ', ' |\t'.join([a for a in alph2]))
		# for i in range(len(self.L)):
		# 	if i % self.checkpoint_spacing == 0:
		# 		print(self.L[i], '    ', ' |\t'.join([str(checkpoints[a][int(i / self.checkpoint_spacing)]) for a in alph2]))
		# 	else:
		# 		print(self.L[i])
		return checkpoints


	#L is the LAST col of BW matrix
	#F is the FIRST col of BW matrix
	#	C is the compact representation of F, with start indexes for each alphabet letter
	#sSAT is the Suffix Array mapping where each suffix row occurs in the original string
	def __init__(self, T, candidate_set, condition_met_f, arguments, index_to_id_map, id_to_index_map, len_S):
		self.arguments = arguments
		self.candidate_set = candidate_set
		self.condition_met_f = condition_met_f
		self.index_to_id_map = index_to_id_map
		self.id_to_index_map = id_to_index_map
		self.len_S = len_S

		self.nodes = 0
		self.duplicate_candidate_count = 0

		self.normalT = T
		T = T[::-1]
		SAT = [i for i in range(len(T))]
		sSAT = sorted(SAT, key=lambda x: T[x:] + T[:x])
		self.F = ''.join(T[sSAT[i]] for i in range(len(T)))
		L = ''.join(T[sSAT[i] - 1] for i in range(len(T)))

		C = dict()
		dollar_count = 0

		#make this more elegant
		self.dollar_signs_at = []
		next_dollar_sign_at = dict()
		prev_dollar_at = -1
		for i in range(len(T)):
			if T[i] == '$':
				self.dollar_signs_at.append(i)
				dollar_count += 1
				if prev_dollar_at != -1:
					next_dollar_sign_at[prev_dollar_at] = i
				prev_dollar_at = i
		next_dollar_sign_at[prev_dollar_at] = len(T)

		Ccount = 0
		sorted_alphabet = sorted_alphabet_of(T)
		for a in sorted_alphabet:
			C[a] = Ccount + dollar_count
			Ccount += T.count(a)

		self.checkpoint_spacing = 4


		self.C = C
		self.L = L
		self.sSAT = sSAT
		self.sorted_alphabet = sorted_alphabet
		self.next_dollar_sign_at = next_dollar_sign_at
		self.T = T


		self.checkpoints = self.get_checkpoints()



		print("INDEX VARS=======")
		print('normalT', self.normalT)
		print('T', T)
		print('L', self.L)
		print('C', self.C)
		print('sSAT', self.sSAT)
		print("INDEX VARS END=======")


	'''NAIVE RANK'''
	# def rank(self, c, i):
	# 	return self.L[:i].count(c)

	'''CHECKPOINT RANK'''
	def rank(self, c, i):
		i2 = i
		encountered = 0
		while i2 % self.checkpoint_spacing != 0:
			i2 -= 1
			if self.L[i2] == c:
				encountered += 1
		check_index = int(i2/self.checkpoint_spacing)
		return self.checkpoints[c][check_index] + encountered

	'''
	used for INCLUSIONS. given an index inside a string B (in the T (which is backwards))
	return the index of the beginning of THAT string in NOT backwards T
	'''
	def index_inside_to_front_not_backwards(self, x):
		walk_left = walk_right = x
		while self.T[walk_left] != '$':
			walk_left -= 1
		while walk_right < len(self.T) and self.T[walk_right] != '$':
			walk_right += 1
		walk_right -= 1
		b_index = (len(self.T)-walk_right-1)%len(self.T)
		b_tail = x-walk_left-1

		# print(self.T)
		# print(debug_aux.carat_chars([walk_left, x, walk_right], 60))
		# print(debug_aux.carat_chars([x], 60))
		#
		# print('b_index')
		# print(self.normalT)
		# print(debug_aux.carat_chars([b_index], 70))
		# print(b_index, b_tail)

		return b_index, b_tail

	'''
	given the index of a dollar sign in the index's version of T (which is reversed)
	returns the index of where that string begins in the original version of T
	'''
	def string_start_in_not_backwards_T(self, end_dollar_in_index_T):
		# print('\n\n')
		# print('end_dollar_in_index_T', end_dollar_in_index_T)
		# print("T backwards:")
		# print(self.T)
		# print(debug_aux.carat_chars([end_dollar_in_index_T], len(self.normalT)))
		x = (end_dollar_in_index_T-1)%len(self.T)
		normal_x = len(self.T)-x-1
		# print(self.normalT)
		# print(debug_aux.carat_chars([normal_x], len(self.normalT)+10))
		ind = self.id_to_index_map[(self.index_to_id_map[normal_x] - 1)% self.len_S]
		# print(debug_aux.carat_chars([ind], len(self.normalT)+10))
		return ind


		# z = (len(self.T) - end_dollar_in_index_T)%len(self.T)
		# print('index_to_id_map', self.index_to_id_map)
		# print('end$in_T', z)
		# print("T correct:")
		# print(self.normalT)
		# print(debug_aux.carat_chars([z], len(self.normalT)+2))
		# id = self.index_to_id_map[z]
		# print('id', id)
		# real_id = (id - 1)% len(self.index_to_id_map)
		# print('real_id', real_id)
		# exit(1)
		# print()
		# fuck_knows = len(self.T)-self.next_dollar_sign_at[end_dollar_in_index_T]
		# # print('fuck_knows', fuck_knows)
		# return fuck_knows


	def new_candidate(self, a_index, b_index, a_ovr, b_ovr, b_tail, debug_str):
		cand = (a_index, b_index, a_ovr, b_ovr, b_tail, debug_str)
		if a_index < 0 or b_index < 0 or a_index >= len(self.T) or b_index >= len(self.T):
			print(cand)
			raise ValueError('oh noes')
		return cand


	'''
	to simulate forward search using backward search...
	everything is forward
		everything outside the index
		the pattern itself
		even the order in which you iterate through the patt characters
	except the T stored in the index
		the steps for each recursive call go rightwards (forwards) in the patt
		but trace through the index backwards
	adds candidates as [index_of_suffix_str, index_of_prefix_str, overlap_length, errors]
	'''
	def forward(self, p, p_i_start, p_i_next, p_i_end, sp, ep, p_T_index, p_id,
				errors, error_lookup, block_id_lookup, MATCHED, indel_balance, suff_len, pref_len):

		# dead end. No matches in index
		if sp >= ep:
			return

		# count node
		self.nodes += 1
		# if self.nodes % 100000 == 0:
		# 	print('\nnodes: ', self.nodes / 1000000, 'mil')
		# 	print('matched so far:', '[' + (p_i_start * '*') + MATCHED + ']   sp:', sp, 'ep', ep)
		# 	print('>>>', MATCHED.replace('_', '').upper())
		# 	print('p_i_next', p_i_next, 'p_i_end', p_i_end, 'err', errors, 'allowed_err', error_lookup[p_i_next])

		if self.arguments.indels and errors < error_lookup[min(p_i_next, p_i_end-1)-p_i_start]:
			# INSERTION
			if indel_balance >= 0:
				for a in self.sorted_alphabet:
					sp_ = self.C[a] + self.rank(a, sp)
					ep_ = self.C[a] + self.rank(a, ep + 1) - 1
					self.forward(p, p_i_start, p_i_next, p_i_end, sp_, ep_, p_T_index, p_id,
								 errors + 1, error_lookup, block_id_lookup, MATCHED + a.lower(), indel_balance+1, suff_len+1, pref_len)



		# no more characters in patt to match
		if p_i_next >= p_i_end :
			# INCLUSIONS!!!
			if self.arguments.inclusions:
				for i in range(sp, ep + 1):
					# print('\n\nINCLUSION')
					a_ovr = pref_len + p_i_start
					b_ovr = suff_len + p_i_start
					b_index, b_tail = self.index_inside_to_front_not_backwards(self.sSAT[i])
					# print('b_index', b_index)
					# print('b_tail', b_tail)
					# print('\n\n')
					x = self.new_candidate(a_index=p_T_index,
										   b_index=b_index,
										   a_ovr=a_ovr,
										   b_ovr=b_ovr,
										   b_tail=b_tail,
										   debug_str='INCL:' + MATCHED
										   )
					if x[0] != x[1]:
						if x not in self.candidate_set:
							self.candidate_set.add(x)
						else:
							self.duplicate_candidate_count += 1
						# print('FIX INCLUSIONS U STUPID')
						# exit(1)
						# for x in [(self.index_inside_to_front_not_backwards(self.sSAT[i]), p_T_index, p_i_next,
						# 		   p_i_next - pref_len + suff_len, MATCHED)  # candidate: (suff_index, pref_index, suff_ovr, pref_ovr)
						# 		  for i in range(sp, ep + 1)]:
						# 	print('INCLUSION DETECTED', x) #TODO translate the midway index
						# 	print('GOD DAMN IT THIS DOESNT VERIFY AT ALL')
						# 	if x[0] != x[1]:
						# 		if x not in self.candidate_set:
						# 			self.candidate_set.add(x)
						# 		else:
						# 			self.duplicate_candidate_count += 1
			return

		# add candidate overlaps for positions followed by '$'
		if self.condition_met_f(p_i_start, max(p_i_next, p_i_next-pref_len+suff_len), self.arguments.thresh, block_id_lookup[p_i_next-p_i_start], errors):
			a = '$'
			sp_ = 0 + self.rank(a, sp)
			ep_ = 0 + self.rank(a, ep + 1) - 1
			a_ovr = pref_len + p_i_start
			b_ovr = suff_len + p_i_start
			debug_string = 'MATCHED[{}] patt[{}]'.format(MATCHED, p[:p_i_end])
			# debug_string = ''
			for i in range(sp_, ep_ + 1):
				b_index = self.string_start_in_not_backwards_T(self.sSAT[i])
				x = self.new_candidate(a_index=p_T_index,
									   b_index=b_index,
									   a_ovr=a_ovr,
									   b_ovr=b_ovr,
									   b_tail=0,
									   debug_str=debug_string
									   )
				if x[0] != x[1]:
					if x not in self.candidate_set:
						self.candidate_set.add(x)
					else:
						self.duplicate_candidate_count += 1




		for a in self.sorted_alphabet:
			# SUBSTITUTION
			sp_ = self.C[a] + self.rank(a, sp)
			ep_ = self.C[a] + self.rank(a, ep + 1) - 1
			errors_ = errors if p[p_i_next] == a else errors + 1
			if errors_ <= error_lookup[p_i_next-p_i_start]:
				self.forward(p, p_i_start, p_i_next+1, p_i_end, sp_, ep_, p_T_index, p_id,
						errors_, error_lookup, block_id_lookup, MATCHED+a, 0, suff_len+1, pref_len+1)

		if self.arguments.indels and errors < error_lookup[p_i_next-p_i_start]:
			# DELETION
			if indel_balance <= 0 and p_i_next < p_i_end-2:
				self.forward(p, p_i_start, p_i_next + 1, p_i_end, sp, ep, p_T_index, p_id,
							 errors + 1, error_lookup, block_id_lookup, MATCHED + '_', indel_balance-1, suff_len, pref_len+1)



	def forward_search(self, p, p_i_start, p_T_index, p_id, error_lookup,
					   block_id_lookup):
		self.forward(p, p_i_start, p_i_start, len(p), 0, len(self.L)-1, p_T_index, p_id,
					 0, error_lookup, block_id_lookup, '?'*p_i_start, 0, 0, 0)


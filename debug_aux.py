import prog_alphabet

def carat_chars(index_list, print_width):
	s = ''
	for i in range(print_width):
		s += '^'if i in index_list else ' '
	return s


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
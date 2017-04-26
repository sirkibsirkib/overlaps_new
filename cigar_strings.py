cigar_code_invert = {'I':'D', 'M':'M', 'D':"I"}

def cigar_sequence(cigar):
	seq = []
	while len(cigar) > 0:
		num_len = 0
		while cigar[:num_len+1].isdigit():
			num_len += 1
		n = int(cigar[:num_len])
		code = cigar[num_len]
		cigar = cigar[num_len + 1:]
		seq.append((n, code))
	return seq

def flip_cigar(cigar):
	return ''.join([str(n) + cigar_code_invert[code] for n, code in cigar_sequence(cigar)])

def rotate_cigar(cigar):
	new_cigar = ''
	for n, code in cigar_sequence(cigar):
		new_cigar = str(n) + code + cigar
	return new_cigar

def align_using_cigar(a, b, cigar):
	# print("\nCIGAR BABY")
	# print('a', a)
	# print('b', b)
	# print('cigar', cigar)
	# print('len a', len(a))
	# print('leb b', len(b))
	a_cigar = ''
	b_cigar = ''
	a_i = 0
	b_i = 0
	for n, code in cigar_sequence(cigar):
		# print('code', '[' + code + ']')
		# print('n', '[' + str(n) + ']')
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
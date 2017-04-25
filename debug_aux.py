def carat_chars(index_list, print_width):
	s = ''
	for i in range(print_width):
		s += '^'if i in index_list else ' '
	return s
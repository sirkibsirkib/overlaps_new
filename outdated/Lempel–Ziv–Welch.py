


def lzw_encode(s):
	out = []
	dic = dict()
	next_key = 0
	for z in s:
		if z not in dic:
			dic[z] = next_key
			next_key += 1

	while(len(s) > 0):
		best_match_len = 1
		next_match_len = 2
		while next_match_len < len(s):
			if s[:next_match_len] not in dic:
				break
			else:
				best_match_len = next_match_len
				next_match_len += 1

		if len(s) > best_match_len:
			dic[s[:best_match_len+1]] = next_key
			next_key += 1
		out.append(dic[s[:best_match_len]])
		s = s[best_match_len:]
		print(s)
		print('==', len(s))
	print("DONE")
	return out, {v: k for k, v in dic.items()}

def lzw_decode(out, dic):
	return ''.join(map(lambda x : dic[x], out))

inp = 'bnbbnbnbnbnbnbnbnnbnnbnnbbbbbbnnbbnnnnnbnnbnbnbnbbbbbbbbbnbnnnnnnnn'
out, dic = lzw_encode(inp)
print(out)
print(dic)



print(inp)
print(lzw_decode(out, dic))
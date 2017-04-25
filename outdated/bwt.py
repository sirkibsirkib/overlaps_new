def rotations(t):
	return [t[i:]+t[:i] for i in range(len(t))]

def bwm(t):
	mat = rotations(t)
	mat = sorted(mat)
	return mat

def bwt(t):
	return ''.join(map(lambda x: x[-1], bwm(t)))

def un_bwt(t):
	seen = dict()
	ranks = []
	last = []
	for char in t:
		if char not in seen:
			ranks.append(0)
			seen[char] = 1
		else:
			ranks.append(seen[char])
			seen[char] += 1
		tup = char, ranks[-1]
		last.append(tup)
	first = sorted(last)
	reconstructed = [('$', 0)]
	for i in range(len(t)-1):
		index = first.index(reconstructed[0])
		prev = last[index]
		reconstructed = [prev] + reconstructed

	return ''.join(map(lambda x : x[0], reconstructed))






s = 'hello_my_baby_hello_my_honey_hello_my_ragtime_gal_send_me_a_kiss_by_wire$'
m = bwt(s)

s2 = bwt(s)
print()
print(s2)
print()
print('==>', un_bwt(s2))
def l_eq(a, b):
	assert len(a) == len(b)
	for i in range(len(a)):
		if a[i] > b[i]:
			return False
	return True


def block(s, n):
	blocks = []
	while len(s) % n > 0:
		s = s + '?'
	for i in range(n):
		blocks.append(s[int(len(s) * i / n):int(len(s) * (i + 1) / n)+1])
	return blocks


def adp(A, B):
	cumul = 0
	ret = []
	for a, b in zip(A, B):
		if a != b:
			cumul += 1
		ret.append(cumul)
	return ret

def part_b(P_parted, B):
	ret = []
	for p in P_parted:
		letters = len(p)
		while len(B) < letters:
			B += '&'
		ret.append(B[:letters])
		B = B[letters:]
	return ret

def suffix_aux(P, B, q):
	k = q + 1
	P = block(P, k)
	B = part_b(P, B)
	#now P and B are both partitions
	for i in range(k):
		suff_P = P[i:]
		suff_B = B[i:]
		_adp = adp(suff_P, suff_B)
		print(suff_P, suff_B, '==adp==>', _adp)
		if l_eq(_adp, list(range(k - i))):
			return i
	return -1


def suffix(P, S, q):
	ret = set()
	for B in S:
		saux = suffix_aux(P, B, q)
		if saux != -1:
			print('for', P, ',', B, 'accepted at index', saux)
	return ret

suffix("ploploploploplop",
	   ['qwerqwerqweeqwerqweqwer', 'qweqwerqrqwreqwqwrqwereqwer', 'qweqwereereqqweqwewrweqwreqwqwe'],
	   10)
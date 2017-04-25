import glob, os

dir1 = 'C:'
dir2 = 'E:'


def longest_common_substring(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer


def conv(s):
    return s.lower()\
        .replace(' ', '_')\
        .replace('.','_').replace('-', '_')\
        .replace('[', '_').replace(']', '_')\
        .replace('__', '_')

os.chdir(dir1)
f1 = []
for file in glob.glob("*.*"):
    f1.append(conv(file))
print('in', dir1, 'found', len(f1), 'files')

os.chdir(dir2)
f2 = []
for file in glob.glob("*.*"):
    f2.append(conv(file))
print('in', dir2, 'found', len(f2), 'files')

for a in f1:
    for b in f2:
        common = longest_common_substring(a, b)
        min_len = min(len(a), len(b))
        if len(common)/min_len > 0.3:
            print(common, '==>\n\t', a, '\n\t',b)
# print(f1)
# print(f2)
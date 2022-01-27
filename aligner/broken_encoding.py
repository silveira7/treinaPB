import re

seq = re.compile(br'\\[0-8]{3}')

decode_seq = lambda m: bytes([int(m.group()[1:], 8)])

def repair(data):
    return seq.sub(decode_seq, data)

broken_seq = rb"\303\255"

print(repair(broken_seq))

# a = "\303\255"
# print(a.encode("utf-8").decode())
#
# # print(a.decode('utf-8'))
#
# seq = re.compile(r'\\[0-8]{3}')
#
# print(
#     bytes([int(seq.search(broken_seq).group()[1:], 8)]
# )

# seq.sub(bytes([int(seq.search(broken_seq).group()[1:], 8)]), broken_seq)
#
# # bytes()
# # int(m.group()[1:])

d= {}
d[2]={}
d[2][3]=10
print(d)
del d[2][3]
u = (2,3)
d = {
 u:10
}
print(d)
u = ((2,3))
v = (3,4)
print(u+v)

def func(list, idx1,idx2):
 temp = list[idx1]
 list[idx1] = list[idx2]
 list[idx2] = temp

import sys

a  = [1, 0, 1, 1, 1, 1]
b = [True, False, True, True, True, True]
c="101111"
d = "".join("1" for i in range(70))
print(sys.getsizeof(a), sys.getsizeof(b), sys.getsizeof(c), d, sys.getsizeof(d))
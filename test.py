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

def f1(var):
 save = []
 idx = 0
 itr = 0
 while var > 0:
  if var%2 == 1:
   save.append(idx)
  idx += 1
  var = var // 2
  itr += 1
  # print(var)
 # print(save, len(save))
 print(itr)
 return len(save)



def f2(var):
 save = []
 itr = 0
 while var > 0:
  itr += 1
  lsb = var ^ (var-1) # LSB and some small bits might be set
  lsb = var & lsb # only the LSB bit is set
  save.append(lsb)
  var = var ^ lsb # LSB is off
 # print(save, len(save))
 print(itr)
 return len(save)


import time

start = time.time()
ans1 = f1(10987654321890765431234567908765) #
end = time.time()
print(start, end, end-start)
start = time.time()
ans2 = f2(10987654321890765431234567908765)
end = time.time()
print(start, end, end-start)
assert(ans1 == ans2)
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

a = (1,2,3)
a = a + tuple([-2])
print(a)
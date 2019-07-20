from instrumentation import *

s = InstrumentedSet(set([3]))

s.add(4)
s.add(5)
assert (5 in s) == True
print("s.get_space()", s.get_space())
print("s.get_ops()", s.get_ops())


l = InstrumentedList([1,2,3])
l.append(4)
assert list(l) == [1,2,3,4]
print(l)
assert (5 in l) == False
assert (4 in l) == True
l.sort(key = lambda x: x, reverse = True)
print(l)
print("l.get_space()", l.get_space())
print("l.get_ops()", l.get_ops())

q = InstrumentedDeque(deque([1,2,3]))
q.append(4)
q.appendleft(0)
q.pop()
q.popleft()
print("q", q)
assert 1 in q
assert 3 in q
assert not 5 in q 
print("q.get_space()", q.get_space())
print("q.get_ops()", q.get_ops())

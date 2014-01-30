from transitions import *
from loop import loop
from state import State
import datetime


state = State(resource_names=['a', 'b', 'c', 'd', 'e', 'f', 'g'])
url = 'http://10.0.34.108/v1/claims/'
#url = 'http://localhost:5000/v1/claims/'

transitions = [
    Activate(base_rate=50),
    Create(url=url, base_rate=100, ttl=1),
    Heartbeat(base_rate=5, ttl=1),
    Release(base_rate=2),
    Revoke(base_rate=1),
]

iterations = 1000

begin = datetime.datetime.now()
loop(state, transitions, iterations)
end = datetime.datetime.now()

print
print 'iterations seconds'
print iterations, (end - begin).total_seconds()

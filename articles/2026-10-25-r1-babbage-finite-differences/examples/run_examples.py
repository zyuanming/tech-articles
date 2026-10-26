"""Exact integer teaching model; CC0-1.0. Python 3.12+."""
from pathlib import Path
import json

def polynomial(n):
    return n ** 3 + 2 * n + 1

def differences(values):
    columns = [list(values)]
    while len(columns[-1]) > 1:
        row = columns[-1]
        columns.append([b-a for a,b in zip(row,row[1:])])
    return columns

def advance(state):
    for j in range(len(state)-1):
        state[j] += state[j+1]
    return state

def generate(state,count):
    state=list(state)
    states=[]
    for _ in range(count):
        states.append(state.copy())
        advance(state)
    return states

def decimal_add(a,b,width):
    carry=0;digits=[];events=[]
    for place in range(width):
        x=a//10**place%10;y=b//10**place%10
        total=x+y+carry;next_carry,digit=divmod(total,10)
        events.append(dict(place=place,a=x,b=y,incoming=carry,total=total,digit=digit,outgoing=next_carry))
        digits.append(digit);carry=next_carry
    return dict(a=a,b=b,width=width,events=events,value=sum(d*10**i for i,d in enumerate(digits)),overflow=carry)

values=[polynomial(n) for n in range(13)]
cols=differences(values)
initial=[c[0] for c in cols[:4]]
states=generate(initial,len(values))
assert [s[0] for s in states]==values
assert all(x==6 for x in cols[3])
assert all(x==0 for x in cols[4])
stages=[initial.copy()];s=initial.copy()
for j in range(3):
    s[j]+=s[j+1];stages.append(s.copy())
wrong=initial.copy();wrong_stages=[wrong.copy()]
for j in reversed(range(3)):
    wrong[j]+=wrong[j+1];wrong_stages.append(wrong.copy())
assert wrong[0]!=values[1]
carry=decimal_add(states[4][0],states[4][1],3)
assert carry['value']==values[5] and carry['overflow']==0
ov=decimal_add(states[9][0],states[9][1],3)
assert ov['value']==values[10]%1000 and ov['overflow']==1
bad=initial.copy();bad[3]+=1
bad_states=generate(bad,8)
errors=[s[0]-polynomial(n) for n,s in enumerate(bad_states)]
assert errors==[n*(n-1)*(n-2)//6 for n in range(8)]
step2=differences([polynomial(2*n) for n in range(6)])
assert all(x==48 for x in step2[3])
nonpoly=differences([2**n for n in range(7)])
# Test independent initializations, including negative states, exact Python ints.
checked=0
for start in range(-20,21):
    for step in range(1,6):
        ds=differences([polynomial(start+step*i) for i in range(4)])
        seq=generate([d[0] for d in ds],30)
        assert [s[0] for s in seq]==[polynomial(start+step*i) for i in range(30)]
        checked+=30
r=dict(polynomial='n³ + 2n + 1',n=list(range(len(values))),values=values,
       columns=cols[:5],initial=initial,states=states,stages=stages,
       wrong_stages=wrong_stages,carry=carry,overflow=ov,
       bad_states=bad_states,errors=errors,step2=step2[:4],nonpoly=nonpoly[:4],
       verification=dict(checked_values=checked,starts=[-20,20],steps=[1,5],count=30),
       direct=[dict(n=n,cube=n**3,linear=2*n,constant=1,value=polynomial(n)) for n in range(4)])
Path(__file__).with_name('results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(f'Exact checks: {checked}; main sequence and counterexamples verified.')

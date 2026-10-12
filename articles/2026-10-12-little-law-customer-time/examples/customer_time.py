"""Original finite-window accounting checks; not a proof of asymptotic Little's Law."""
from fractions import Fraction as F
import random,json

def area_events(jobs,start,end):
    cuts=sorted({start,end}|{max(start,min(end,t)) for job in jobs for t in job})
    return sum((b-a)*sum(s<=(a+b)/2<e for s,e in jobs) for a,b in zip(cuts,cuts[1:]))
def area_people(jobs,start,end):
    return sum(max(0,min(end,e)-max(start,s)) for s,e in jobs)
def main():
    jobs=[(0,4),(1,3),(2,7),(4,6),(6,10)]
    area=area_events(jobs,0,10); assert area==17
    lam=F(len(jobs),10); w=F(sum(e-s for s,e in jobs),len(jobs)); L=F(area,10)
    assert L==lam*w==F(17,10)
    service_starts=[2,1,5,5,6]
    q=[(a,s) for (a,b),s in zip(jobs,service_starts)]
    service=[(s,b) for (a,b),s in zip(jobs,service_starts)]
    assert area_events(q,0,10)==6 and area_events(service,0,10)==11
    clipped=[(-2,2),(1,4),(4,8)]
    assert area_people(clipped,0,5)==area_events(clipped,0,5)==6
    naive=F(2,5)*F(3+4,2); assert naive==F(7,5)!=F(6,5)
    rng=random.Random(1961)
    for _ in range(10000):
        random_jobs=[]
        for i in range(rng.randrange(1,31)):
            a=rng.randrange(-20,31); b=a+rng.randrange(0,31); random_jobs.append((a,b))
        assert area_events(random_jobs,0,20)==area_people(random_jobs,0,20)
    return {'status':'PASS','empty_boundary_example':{'jobs':jobs,'area_person_minutes':17,'T_minutes':10,'lambda_per_minute':str(lam),'W_minutes':str(w),'L_people':str(L),'queue_area':6,'service_area':11},'clipped_window_counterexample':{'jobs':clipped,'window':[0,5],'correct_L':'6/5','naive_arrivals_full_W_product':str(naive),'reason':'Initial customer and unfinished customer require clipped residence-time accounting'},'random_finite_area_checks':10000,'scope':'Synthetic arithmetic and exact finite area identities only; not production measurement or proof of long-run convergence'}
def extra_examples():
    # nearest-rank 99th percentile for exactly 100 synthetic durations.
    even=[2]*100; tail=[1]*98+[51]*2
    assert sum(even)==sum(tail)==200
    assert sorted(even)[98]==2 and sorted(tail)[98]==51
    jobs=[(0,w) for w in tail]
    assert area_events(jobs,0,51)==200
    # Two separate hypothetical operating points; no capacity prediction.
    assert F(10,1)/F(1,5)==50 and F(20,1)/F(2,5)==50
    # Count only admitted requests, or include rejected requests with zero residence.
    assert 80*F(1,8)==100*(F(80,100)*F(1,8))==10
    return {'same_mean_tail_counterexample':{'n':100,'mean':2,'even_p99':2,'tail_p99':51,'p99_definition':'nearest rank:99th sorted value'},'concurrency_examples':{'(L,W,lambda)':['(10,0.2,50)','(20,0.4,50)']},'admission_example':{'offered_per_second':100,'admitted_per_second':80,'rejected_per_second':20,'mean_admitted_seconds':'1/8','mean_all_seconds':'1/10','L':10}}

if __name__=='__main__':
    result=main();result.update(extra_examples());print(json.dumps(result,ensure_ascii=False,indent=2))

import json
from pathlib import Path
import tempfile
import unittest
from image_decode_diagnostics import NetworkDiagnostics, retryable, same_origin

BASE='https://example.test'
URL=BASE+'/image.png'

class Response:
    def __init__(self, status, url=URL, headers=None):
        self.status, self.url, self.headers = status, url, headers or {}
        self.ok=200 <= status < 300

class Page:
    url=BASE+'/read.html'
    def __init__(self, failures=0, evidence=None):
        self.handlers={};self.failures=failures;self.waits=0;self.resets=0;self.evidence=evidence
    def on(self, name, fn):self.handlers[name]=fn
    def locator(self, selector):return self
    def wait_for_function(self, expression):
        self.waits+=1
        if self.waits <= self.failures:raise RuntimeError('decode timeout')
    def evaluate_all(self, expression, arg=None):
        if 'imgs.map((i,index)' in expression:
            return [dict(index=0,src='image.png',currentSrc=URL,complete=True,naturalWidth=0,naturalHeight=0)]
        if arg is not None:
            self.resets+=1
            if self.evidence:self.handlers['response'](Response(self.evidence))

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'evidence.jsonl';self.delays=[]
    def tearDown(self):self.tmp.cleanup()
    def make(self, page=None):return NetworkDiagnostics(page or Page(),BASE,self.path,'mobile',self.delays.append)
    def logs(self):return [json.loads(x) for x in self.path.read_text().splitlines()]
    def test_policy(self):
        for status in [408,500,502,503,504]:self.assertTrue(retryable({'url':URL,'status':status},BASE))
        for status in [200,301,400,401,403,404,429]:self.assertFalse(retryable({'url':URL,'status':status},BASE))
        for headers in [{'Retry-After':'1'},{'x-ratelimit-remaining':'0'}]:self.assertFalse(retryable({'url':URL,'status':503,'headers':headers},BASE))
        self.assertFalse(retryable({'url':'https://elsewhere.test/img','status':503},BASE))
        self.assertFalse(retryable({'url':URL,'failure':'net::ERR_ACCESS_DENIED'},BASE))
        self.assertFalse(retryable({'url':URL,'failure':'unknown timeout'},BASE))
        self.assertTrue(retryable({'url':URL,'failure':'net::ERR_CONNECTION_RESET'},BASE))
    def test_request_recovers_and_preserves_first_error(self):
        d=self.make();responses=iter([Response(503),Response(200)]);self.assertTrue(d.request(lambda:next(responses),URL).ok)
        self.assertEqual(self.delays,[2]);self.assertEqual(self.logs()[0]['resource']['status'],503)
        self.assertEqual(self.logs()[-1]['kind'],'request_recovered')
    def test_request_exhausted_exactly_three(self):
        d=self.make();calls=[]
        def op():calls.append(1);return Response(503)
        self.assertFalse(d.request(op,URL).ok);self.assertEqual(len(calls),3);self.assertEqual(self.delays,[2,5])
    def test_request_permanent_and_denied_never_retry(self):
        for status in [401,403,404,429]:
            d=self.make();self.assertEqual(d.request(lambda:Response(status),URL).status,status)
        self.assertEqual(self.delays,[])
    def test_request_exception_not_retried(self):
        def fail():raise RuntimeError('timeout without evidence')
        with self.assertRaises(RuntimeError):self.make().request(fail,URL)
        self.assertEqual(self.delays,[])
    def test_images_success_no_retry(self):
        p=Page();self.make(p).decode_images();self.assertEqual(p.waits,1);self.assertEqual(p.resets,0)
    def test_images_recover_only_proven_transient(self):
        p=Page(1,evidence=200);d=self.make(p);d._response(Response(503));d.decode_images()
        self.assertEqual(p.resets,1);self.assertEqual(self.delays,[2]);self.assertEqual(self.logs()[-1]['kind'],'images_recovered')
        failure=next(x for x in self.logs() if x['kind']=='image_decode_failure');self.assertEqual(failure['images'][0]['currentSrc'],URL)
    def test_images_exhaustion_keeps_failure(self):
        p=Page(3,evidence=503);d=self.make(p);d._response(Response(503))
        with self.assertRaises(RuntimeError):d.decode_images()
        self.assertEqual(p.resets,2);self.assertEqual(p.waits,3);self.assertEqual(self.delays,[2,5])
    def test_images_unknown_or_bad_bytes_do_not_retry(self):
        for response in [None,Response(200),Response(404),Response(401),Response(403),Response(429),Response(503,headers={'retry-after':'2'})]:
            p=Page(1);d=self.make(p)
            if response:d._response(response)
            with self.assertRaises(RuntimeError):d.decode_images()
            self.assertEqual(p.resets,0)
        self.assertEqual(self.delays,[])
    def test_denial_is_not_replaced_by_network_error(self):
        p=Page();d=self.make(p);d._response(Response(403))
        class Request:url=URL;failure='net::ERR_CONNECTION_RESET'
        d._failed(Request());self.assertEqual(d.latest[URL]['status'],403)
    def test_standard_rate_limit_header_stops(self):
        d=self.make();calls=[]
        def op():calls.append(1);return Response(503,headers={'RateLimit-Remaining':'0'})
        d.request(op,URL);self.assertEqual(len(calls),1);self.assertEqual(self.delays,[])
    def test_nonretryable_http_sticky_across_connection_reset(self):
        for status in [200,401,403,404,429]:
            p=Page(1);d=self.make(p);d._response(Response(status))
            class Request:url=URL;failure='net::ERR_CONNECTION_RESET'
            d._failed(Request())
            with self.assertRaises(RuntimeError):d.decode_images()
            self.assertEqual(p.resets,0);self.assertEqual(d.latest[URL]['status'],status)
    def test_denial_sticky_across_later_transient_response(self):
        for status in [401,403,404,429]:
            p=Page(1);d=self.make(p);d._response(Response(status));d._response(Response(503))
            with self.assertRaises(RuntimeError):d.decode_images()
            self.assertEqual(p.resets,0);self.assertEqual(d.latest[URL]['status'],status)
    def test_reset_starts_new_page_evidence(self):
        d=self.make();d._response(Response(403));d.reset();d._response(Response(503))
        self.assertEqual(d.latest[URL]['status'],503)
    def test_503_zero_recovers_with_original_backoff(self):
        d=self.make();responses=iter([Response(503,headers={'Retry-After':'0'}),Response(200)])
        self.assertTrue(d.request(lambda:next(responses),URL).ok);self.assertEqual(self.delays,[2])
        self.assertEqual(self.logs()[0]['resource']['headers']['Retry-After'],'0')
    def test_503_zero_exhausts_at_three(self):
        d=self.make();calls=[]
        def op():calls.append(1);return Response(503,headers={'retry-after':'0'})
        self.assertFalse(d.request(op,URL).ok);self.assertEqual(len(calls),3);self.assertEqual(self.delays,[2,5])
    def test_zero_does_not_override_denial_or_exhaustion(self):
        for status in [401,403,429,500,502,504]:
            self.assertFalse(retryable({'url':URL,'status':status,'headers':{'retry-after':'0'}},BASE))
        for key in ['ratelimit-remaining','x-ratelimit-remaining']:
            self.assertFalse(retryable({'url':URL,'status':503,'headers':{'retry-after':'0',key:'0'}},BASE))
        p=Page(1);d=self.make(p);d._response(Response(403));d._response(Response(503,headers={'retry-after':'0'}))
        with self.assertRaises(RuntimeError):d.decode_images()
        self.assertEqual(p.resets,0)
    def test_only_exact_zero_is_admitted(self):
        for value in ['', '1', '00', ' 0 ', '-1', '0.0', 'Wed, 14 Oct 2026 10:00:00 GMT','invalid']:
            self.assertFalse(retryable({'url':URL,'status':503,'headers':{'retry-after':value}},BASE))
    def test_zero_image_recovery(self):
        p=Page(1,evidence=200);d=self.make(p);d._response(Response(503,headers={'retry-after':'0'}));d.decode_images()
        self.assertEqual(p.resets,1);self.assertEqual(self.delays,[2])
    def test_off_origin_never_retry(self):
        d=self.make();r=d.request(lambda:Response(503,url='https://other.test/img'),URL)
        self.assertEqual(r.status,503);self.assertEqual(self.delays,[])

if __name__=='__main__':unittest.main()

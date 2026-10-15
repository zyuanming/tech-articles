"""Bounded, evidence-based recovery for public reading-site QA requests.

No content assertion is relaxed. Unknown failures and access/rate-limit errors
remain failures. JSONL retains initial failures even when a retry succeeds.
"""
import json
import time
from urllib.parse import urlsplit

RETRY_DELAYS = (2, 5)
TRANSIENT_STATUS = {408, 500, 502, 503, 504}
TRANSIENT_NETWORK = {'net::ERR_CONNECTION_RESET', 'net::ERR_CONNECTION_CLOSED',
                     'net::ERR_CONNECTION_TIMED_OUT', 'net::ERR_TIMED_OUT'}


def same_origin(a, b):
    x, y = urlsplit(a), urlsplit(b)
    return (x.scheme, x.hostname, x.port) == (y.scheme, y.hostname, y.port)


def retryable(event, base_url):
    if not event or not same_origin(event.get('url', ''), base_url):
        return False
    headers = {k.lower(): str(v) for k, v in event.get('headers', {}).items()}
    status = event.get('status')
    if any(headers.get(k, '').strip() == '0' for k in ('x-ratelimit-remaining', 'ratelimit-remaining')):
        return False  # Explicit exhaustion always wins over Retry-After.
    if 'retry-after' in headers and not (status == 503 and headers['retry-after'] == '0'):
        return False
    # RFC 9110 section 10.2.3: a 503 Retry-After: 0 requests zero delay.
    # Still use our slower 2/5-second bounded backoff; no other value is allowed.
    if status is not None:
        return status in TRANSIENT_STATUS
    return event.get('failure') in TRANSIENT_NETWORK


def response_event(response):
    headers = response.headers
    return {'url': response.url, 'status': response.status,
            'headers': {k: v for k, v in headers.items()
                        if k.lower() in {'retry-after', 'x-ratelimit-remaining', 'ratelimit-remaining',
                                         'ratelimit-limit', 'ratelimit-reset', 'ratelimit-policy',
                                         'x-ratelimit-limit', 'x-ratelimit-reset', 'date',
                                         'server', 'via', 'content-type', 'content-length',
                                         'x-cache', 'x-cache-hits'}}}


class NetworkDiagnostics:
    def __init__(self, page, base_url, artifact, viewport, sleep=time.sleep):
        self.page, self.base_url = page, base_url
        self.artifact, self.viewport, self.sleep = artifact, viewport, sleep
        self.latest = {}
        self.stops = {}
        page.on('response', self._response)
        page.on('requestfailed', self._failed)

    def record(self, kind, **data):
        event = dict(kind=kind, viewport=self.viewport, page_url=self.page.url, **data)
        with self.artifact.open('a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')

    def reset(self):
        self.latest.clear()
        self.stops.clear()

    def _response(self, response):
        event = response_event(response)
        target = event['url']
        # A known non-retryable HTTP result is sticky for this page load.
        # In particular, later 503 or connection errors cannot erase a denial.
        if not retryable(event, self.base_url):
            self.stops.setdefault(target, event)
        self.latest[target] = self.stops.get(target, event)
        if event['status'] >= 400:
            self.record('http_failure', resource=event)

    def _failed(self, request):
        event = {'url': request.url, 'failure': request.failure}
        if request.url in self.stops:
            self.record('network_failure_after_stop', resource=event,
                        stop=self.stops[request.url])
            return
        self.latest[request.url] = event
        self.record('network_failure', resource=event)

    def request(self, operation, target):
        """Retry only an actual transient response, keeping original assertions."""
        for attempt in range(3):
            try:
                response = operation()
            except Exception as exc:
                # An exception alone is not proof of a transient network failure.
                self.record('request_exception', target=target, attempt=attempt,
                            error=str(exc))
                raise
            event = response_event(response) if response else None
            if response and response.ok:
                if attempt:
                    self.record('request_recovered', target=target, attempt=attempt)
                return response
            self.record('request_failure', target=target, attempt=attempt, resource=event)
            if attempt == 2 or not retryable(event, self.base_url):
                return response
            self.record('request_retry', target=target, attempt=attempt + 1,
                        delay=RETRY_DELAYS[attempt])
            self.sleep(RETRY_DELAYS[attempt])

    def get(self, target):
        return self.request(lambda: self.page.request.get(target), target)

    def goto(self, target, **kwargs):
        self.reset()
        return self.request(lambda: self.page.goto(target, **kwargs), target)

    def decode_images(self):
        page = self.page
        page.locator('img').evaluate_all("imgs => imgs.forEach(i => i.loading = 'eager')")
        for attempt in range(3):
            try:
                page.wait_for_function("Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)")
                page.locator('img').evaluate_all("imgs => Promise.all(imgs.map(i => i.decode()))")
                if attempt:
                    self.record('images_recovered', attempt=attempt)
                return
            except Exception as exc:
                images = page.locator('img').evaluate_all("imgs => imgs.map((i,index) => ({index,src:i.getAttribute('src'),currentSrc:i.currentSrc,complete:i.complete,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}))")
                bad = [i for i in images if not i['complete'] or i['naturalWidth'] == 0]
                evidence = [self.latest.get(i['currentSrc']) for i in bad]
                self.record('image_decode_failure', attempt=attempt, error=str(exc),
                            images=images, failed_requests=evidence)
                if attempt == 2 or not bad or not all(retryable(e, self.base_url) for e in evidence):
                    raise
                self.record('image_retry', attempt=attempt + 1, delay=RETRY_DELAYS[attempt],
                            resources=[i['currentSrc'] for i in bad])
                self.sleep(RETRY_DELAYS[attempt])
                for i in bad:
                    self.latest.pop(i['currentSrc'], None)
                # Re-request only failed, proven-transient images at the identical URL.
                # No cache-buster, alternate host, route, auth or whole-page refresh.
                page.locator('img').evaluate_all("(imgs, indices) => indices.forEach(n => { const i=imgs[n]; const src=i.getAttribute('src'); i.removeAttribute('src'); i.setAttribute('src',src); })", [i['index'] for i in bad])

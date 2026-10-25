"""Linux-only socketpair/epoll teaching experiments. Code and data: CC0-1.0."""
import argparse
from collections import deque
import errno
import json
import os
from pathlib import Path
import platform
import re
import select
import socket

FLAGS = ('EPOLLIN', 'EPOLLOUT', 'EPOLLRDHUP', 'EPOLLHUP', 'EPOLLERR')


def events(ep, names):
    return [{'endpoint': names[fd], 'flags': [s for s in FLAGS if mask & getattr(select, s)]}
            for fd, mask in ep.poll(0)]


def pair():
    a, b = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    a.setblocking(False)
    b.setblocking(False)
    return a, b


def read_once(sock, size):
    try:
        chunk = os.read(sock.fileno(), size)
    except InterruptedError:
        return {'kind': 'EINTR'}
    except BlockingIOError as e:
        assert e.errno in (errno.EAGAIN, errno.EWOULDBLOCK)
        return {'kind': 'EAGAIN'}
    return {'kind': 'data' if chunk else 'EOF', 'text': chunk.decode('ascii'), 'bytes': len(chunk)}


def drain(sock, size=2):
    trace = []
    while True:
        item = read_once(sock, size)
        trace.append(item)
        if item['kind'] not in ('data', 'EINTR'):
            return trace


def partial(mode):
    a, b = pair()
    with a, b, select.epoll() as ep:
        mask = select.EPOLLIN | (select.EPOLLET if mode == 'ET' else 0)
        ep.register(b, mask)
        names = {b.fileno(): 'B'}
        payload = b'abcdef'
        sent = a.send(payload)
        assert sent == len(payload)
        before = b.recv(99, socket.MSG_PEEK).decode()
        first_event = events(ep, names)
        after_wait = b.recv(99, socket.MSG_PEEK).decode()
        first_read = read_once(b, 2)
        remaining = b.recv(99, socket.MSG_PEEK).decode()
        second_event = events(ep, names)
        drained = drain(b)
        after_drain = events(ep, names)
        a.sendall(b'XY')
        next_event = events(ep, names)
        next_reads = drain(b)
        return dict(mode=mode, payload=payload.decode(), sent=sent, before=before,
                    after_wait=after_wait, first_event=first_event, first_read=first_read,
                    remaining=remaining, second_event=second_event, drained=drained,
                    after_drain=after_drain, next_event=next_event, next_reads=next_reads)


def new_activity():
    a, b = pair()
    with a, b, select.epoll() as ep:
        ep.register(b, select.EPOLLIN | select.EPOLLET)
        names = {b.fileno(): 'B'}
        a.sendall(b'abcdef')
        first = events(ep, names)
        read = read_once(b, 2)
        quiet = events(ep, names)
        before = b.recv(99, socket.MSG_PEEK).decode()
        a.sendall(b'XY')
        active = events(ep, names)
        after = b.recv(99, socket.MSG_PEEK).decode()
        tail = drain(b)
        return dict(first=first, read=read, quiet=quiet, before=before,
                    added='XY', active=active, after=after, tail=tail)


def stale_readiness():
    a, b = pair()
    with a, b, select.epoll() as ep:
        ep.register(b, select.EPOLLIN)
        a.sendall(b'Z')
        notice = events(ep, {b.fileno(): 'B'})
        earlier_reader = read_once(b, 1)
        later_reader = read_once(b, 1)
        return dict(event=notice, earlier_reader=earlier_reader, later_reader=later_reader)


def framing():
    a, b = pair()
    out, pending = [], b''
    with a, b, select.epoll() as ep:
        ep.register(b, select.EPOLLIN | select.EPOLLET)
        for payload in [b'HEL', b'LO\n', b'A\nB\n']:
            a.sendall(payload)
            notice = events(ep, {b.fileno(): 'B'})
            trace = drain(b, 64)
            pending += ''.join(x.get('text', '') for x in trace).encode()
            parts = pending.split(b'\n')
            pending = parts.pop()
            out.append(dict(sent=payload.decode(), event=notice, reads=trace,
                            messages=[p.decode() for p in parts], pending=pending.decode()))
    return out


def eof():
    a, b = pair()
    with a, b, select.epoll() as ep:
        ep.register(b, select.EPOLLIN | select.EPOLLRDHUP | select.EPOLLET)
        a.sendall(b'END')
        a.shutdown(socket.SHUT_WR)
        notice = events(ep, {b.fileno(): 'B'})
        trace = drain(b)
        return dict(payload='END', event=notice, reads=trace)


def oneshot():
    a, b = pair()
    with a, b, select.epoll() as ep:
        # Deliberately LT + ONESHOT, to separate ONESHOT from ET.
        mask = select.EPOLLIN | select.EPOLLONESHOT
        ep.register(b, mask)
        names = {b.fileno(): 'B'}
        a.sendall(b'ab')
        first = events(ep, names)
        reads = drain(b)
        a.sendall(b'cd')
        disabled = events(ep, names)
        ep.modify(b, mask)
        rearmed = events(ep, names)
        rest = drain(b)
        return dict(first=first, reads=reads, disabled=disabled, rearmed=rearmed, rest=rest)


def writing():
    a, b = pair()
    with a, b, select.epoll() as ep:
        a.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
        payload = b'x' * 65536
        pending = memoryview(payload)
        ep.register(a, select.EPOLLOUT | select.EPOLLET)
        names = {a.fileno(): 'A'}
        initial = events(ep, names)
        writes, rounds, received = [], [], bytearray()
        while pending:
            before = len(pending)
            try:
                n = a.send(pending)
                assert n > 0
                pending = pending[n:]
                writes.append(dict(kind='data', offered=before, accepted=n, remaining=len(pending)))
            except InterruptedError:
                continue
            except BlockingIOError:
                writes.append(dict(kind='EAGAIN', offered=before, accepted=0, remaining=before))
                while True:
                    try:
                        chunk = b.recv(65536)
                        assert chunk
                        received.extend(chunk)
                    except BlockingIOError:
                        break
                notice = events(ep, names)
                rounds.append(dict(receiver_total=len(received), event=notice))
                assert notice, 'Controlled full drain should allow retry; preserve failure if unexpected.'
        # Empty application queue: remove EPOLLOUT interest, then consume tail.
        ep.modify(a, select.EPOLLIN | select.EPOLLET)
        while True:
            try:
                received.extend(b.recv(65536))
            except BlockingIOError:
                break
        assert bytes(received) == payload
        return dict(payload_bytes=len(payload), requested_sndbuf=4096,
                    effective_sndbuf=a.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF),
                    initial=initial, writes=writes, recovery=rounds,
                    received_bytes=len(received), after_disable=events(ep, names))


def fairness():
    a, ar = pair()
    b, br = pair()
    with a, ar, b, br, select.epoll() as ep:
        readers = {'A': ar, 'B': br}
        names = {v.fileno(): k for k, v in readers.items()}
        for s in readers.values():
            ep.register(s, select.EPOLLIN | select.EPOLLET)
        a.sendall(b'abcdef')
        b.sendall(b'UV')
        notice = events(ep, names)
        # Explicit teaching scheduling policy: A before B, independent of kernel order.
        ready = deque(sorted(x['endpoint'] for x in notice))
        trace = []
        while ready:
            before = list(ready)
            name = ready.popleft()
            item = read_once(readers[name], 2)
            if item['kind'] in ('data', 'EINTR'):
                ready.append(name)
            trace.append(dict(before=before, endpoint=name, read=item, after=list(ready)))
        return dict(payloads={'A': 'abcdef', 'B': 'UV'}, budget_bytes=2,
                    initial=notice, trace=trace, final_events=events(ep, names))


def run():
    if platform.system() != 'Linux' or not hasattr(select, 'epoll'):
        raise RuntimeError('This experiment requires Linux epoll.')
    result = dict(environment=dict(system='Linux',
                  observed_kernel_release=re.match(r'\d+\.\d+\.\d+', platform.release()).group(),
                  python=platform.python_version(), family='AF_UNIX', type='SOCK_STREAM',
                  poll_timeout_seconds=0),
                  partial=[partial('LT'), partial('ET')], new_activity=new_activity(),
                  stale=stale_readiness(),
                  framing=framing(), eof=eof(), oneshot=oneshot(),
                  writing=writing(), fairness=fairness())
    lt, et = result['partial']
    assert lt['before'] == lt['after_wait'] == et['before'] == et['after_wait'] == 'abcdef'
    assert lt['first_read']['text'] == et['first_read']['text'] == 'ab'
    assert lt['second_event'] and not et['second_event']
    assert all(x['drained'][-1]['kind'] == 'EAGAIN' for x in result['partial'])
    assert result['new_activity']['before'] == 'cdef'
    assert result['new_activity']['after'] == 'cdefXY'
    assert result['eof']['reads'][-1]['kind'] == 'EOF'
    assert result['stale']['later_reader']['kind'] == 'EAGAIN'
    assert result['oneshot']['disabled'] == [] and result['oneshot']['rearmed']
    assert [x['messages'] for x in result['framing']] == [[], ['HELLO'], ['A', 'B']]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('results.json'))
    args = parser.parse_args()
    data = run()
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print('LT second poll:', data['partial'][0]['second_event'])
    print('ET second poll:', data['partial'][1]['second_event'])
    print('Drain:', data['partial'][1]['drained'])
    print('EOF:', data['eof']['reads'])
    print('All semantic checks passed; no timing benchmark.')

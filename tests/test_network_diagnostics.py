import socket
import threading

from core.network_security import diagnostics as d


def _listener():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.bind(('127.0.0.1',0)); s.listen(1); return s


def test_real_loopback_port_scan_detects_listener():
    s=_listener()
    try:
        port=s.getsockname()[1]
        rows=d.port_scan('127.0.0.1',[port],timeout=0.25)
        assert rows[0]['state']=='open'
        assert rows[0]['port']==port
    finally: s.close()


def test_scope_rejects_public_network():
    try:
        d.validate_scope('8.8.8.0/24')
    except ValueError as exc:
        assert 'BLOCKED' in str(exc)
    else:
        raise AssertionError('public scope must be blocked')


def test_scope_rejects_oversized_private_network():
    try:
        d.validate_scope('10.0.0.0/8')
    except ValueError as exc:
        assert 'too large' in str(exc)
    else:
        raise AssertionError('oversized scope must be rejected')


def test_traffic_snapshot_is_real_counter_shape():
    out=d.traffic_snapshot()
    assert 'interfaces' in out and 'total_sent' in out and 'total_recv' in out
    assert isinstance(out['interfaces'],dict)


def test_socket_snapshot_shape():
    rows=d.socket_snapshot()
    assert isinstance(rows,list)
    if rows:
        assert {'proto','local','remote','status','pid'} <= set(rows[0])


def test_topology_snapshot_contains_local_node():
    out=d.topology_snapshot()
    assert 'nodes' in out and 'links' in out and 'routes' in out
    assert any(n['id']=='LOCAL' for n in out['nodes'])

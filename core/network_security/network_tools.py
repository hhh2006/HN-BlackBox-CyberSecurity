"""Safe local/network educational utilities. No exploitation or credential attacks."""
import ipaddress, socket
def analyze_ip(value):
    ip=ipaddress.ip_address(value.strip())
    return {"version":ip.version,"compressed":ip.compressed,"private":ip.is_private,"loopback":ip.is_loopback,"multicast":ip.is_multicast,"global":ip.is_global}
def subnet(value):
    net=ipaddress.ip_network(value.strip(),strict=False)
    return {"network":str(net.network_address),"broadcast":str(net.broadcast_address),"prefix":net.prefixlen,"hosts":net.num_addresses if net.prefixlen>=31 else max(0,net.num_addresses-2),"first":str(next(net.hosts(),net.network_address))}
def dns_lookup(host):
    host=host.strip()
    if not host: raise ValueError("Enter a hostname.")
    return socket.getaddrinfo(host,None)

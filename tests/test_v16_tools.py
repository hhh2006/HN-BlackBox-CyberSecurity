from core import real_tools, labs3

def test_hash_and_encoding():
    assert real_tools.hash_bytes(b"abc")["sha256"] == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert real_tools.b64_decode(real_tools.b64_encode("HN_BLACKBOX")) == "HN_BLACKBOX"

def test_parsers():
    assert real_tools.parse_url("https://example.local/a?q=1")["query"]["q"] == "1"
    d=real_tools.decode_jwt("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.demo")
    assert d["payload"]["sub"] == "123"

def test_ioc_and_entropy():
    d=real_tools.extract_iocs("failed 203.0.113.9 https://example.local a@b.com")
    assert "203.0.113.9" in d["ipv4"] and d["urls"] and d["emails"]
    assert real_tools.password_entropy("A1!very-long-example")['entropy_bits'] > 50

def test_lab_catalog():
    labs=labs3.catalog()
    assert len(labs) >= 10
    assert any(x['id']=='NET-02' for x in labs)

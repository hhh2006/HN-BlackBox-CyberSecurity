from gui.app import HNBlackBoxApp


def test_modern_center_des_real_trace_roundtrip():
    app = HNBlackBoxApp()
    try:
        app.show_page("crypto_modern")
        app.update_idletasks()
        ctx = app._modern_context
        ctx["des"]["input"].delete("1.0", "end")
        ctx["des"]["input"].insert("1.0", "HN BlackBox DES")
        ctx["des"]["key"].delete(0, "end")
        ctx["des"]["key"].insert(0, "HNKEY123")
        ctx["des"]["op"].set("encrypt")
        ctx["des"]["execute"].invoke()
        cipher = ctx["des"]["output"].get("1.0", "end-1c")
        assert cipher and cipher != "HN BlackBox DES"
        rows = ctx["state"]["rows"]
        assert len(rows) == 16
        assert all(k in rows[0] for k in ("key_hex", "expanded", "xor", "sbox", "pbox", "l_out", "r_out"))
        ctx["des"]["input"].delete("1.0", "end")
        ctx["des"]["input"].insert("1.0", cipher)
        ctx["des"]["op"].set("decrypt")
        ctx["des"]["execute"].invoke()
        assert ctx["des"]["output"].get("1.0", "end-1c") == "HN BlackBox DES"
    finally:
        app.destroy()


def test_modern_center_aes_hash_rsa_are_operational():
    app = HNBlackBoxApp()
    try:
        app.show_page("crypto_modern")
        app.update_idletasks()
        ctx = app._modern_context

        # AES real engine round-trip.
        a = ctx["aes"]
        a["input"].delete("1.0", "end")
        a["input"].insert("1.0", "AES modern lab")
        a["key"].delete(0, "end")
        a["key"].insert(0, "HN-AES-LAB-256")
        a["op"].set("encrypt")
        # Locate the AES execute button inside its workspace.
        aes_buttons=[]
        def walk(w):
            for child in w.winfo_children():
                if child.winfo_class() == "Button": aes_buttons.append(child)
                walk(child)
        walk(app.pages["crypto_modern"])
        for b in aes_buttons:
            if b.cget("text") == "> EXECUTE AES": b.invoke(); break
        cipher=a["output"].get("1.0","end-1c")
        assert cipher
        a["input"].delete("1.0","end"); a["input"].insert("1.0",cipher); a["op"].set("decrypt")
        for b in aes_buttons:
            if b.cget("text") == "> EXECUTE AES": b.invoke(); break
        assert a["output"].get("1.0","end-1c") == "AES modern lab"

        # Hashing.
        h=ctx["hash"]
        h["input"].delete("1.0","end"); h["input"].insert("1.0","integrity")
        for b in aes_buttons:
            if b.cget("text") == "CALCULATE DIGEST": b.invoke(); break
        digest=h["output"].get("1.0","end-1c")
        assert len(digest) == 64

        # RSA demo key generation.
        rsa_buttons=[]
        def walk_r(w):
            for child in w.winfo_children():
                if child.winfo_class() == "Button": rsa_buttons.append(child)
                walk_r(child)
        walk_r(app.pages["crypto_modern"])
        for b in rsa_buttons:
            if b.cget("text") == "GENERATE 2048-BIT EDUCATIONAL KEY": b.invoke(); break
        assert ctx["rsa"]["key"].get().startswith("e=")
    finally:
        app.destroy()

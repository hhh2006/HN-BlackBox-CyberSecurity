#!/usr/bin/env python3
"""HN BlackBox v40.0.0 — interactive terminal console.
Runs locally and exposes an allow-listed security/learning command set.
It intentionally does not execute arbitrary OS shell commands.
"""
from __future__ import annotations
import argparse, base64, hashlib, os, platform, re, shlex, socket, sys, textwrap, time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from core import caesar, vigenere, affine, rail_fence, classical, frequency_analysis, network_tools, real_tools
from core.security_labs.lab_engine import LabEngine, LABS

CSI='\033['
def c(code,s=''): return f'{CSI}{code}m{s}{CSI}0m'
CY=CSI+'96m'; GR=CSI+'92m'; YL=CSI+'93m'; RD=CSI+'91m'; PR=CSI+'95m'; DIM=CSI+'90m'; WH=CSI+'97m'; BL=CSI+'94m'

def clear():
    # Avoid shell invocation; emit terminal control sequences directly.
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()
def banner():
    clear()
    print(c('96','╔══════════════════════════════════════════════════════════════════╗'))
    print(c('96','║')+c('97','   ██╗  ██╗███╗   ██╗    ██████╗ ██╗      ██████╗  ██████╗        ')+c('96','║'))
    print(c('96','║')+c('97','   ██║  ██║████╗  ██║    ██╔══██╗██║     ██╔══██╗██╔════╝         ')+c('96','║'))
    print(c('96','║')+c('97','   ███████║██╔██╗ ██║    ██████╔╝██║     ██║   ██║██║             ')+c('96','║'))
    print(c('96','║')+c('97','   ██╔══██║██║╚██╗██║    ██╔══██╗██║     ██║   ██║██║             ')+c('96','║'))
    print(c('96','║')+c('97','   ██║  ██║██║ ╚████║    ██████╔╝███████╗╚██████╔╝╚██████╗        ')+c('96','║'))
    print(c('96','║')+c('97','   ╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝        ')+c('96','║'))
    print(c('96','║                                                                  ║'))
    print(c('96','║')+c('97','              H N   B L A C K B O X   v40.0.0                       ')+c('96','║'))
    print(c('96','║')+c('90','          CYBER / CRYPTO / LAB / DEFENSE WORKSPACE                ')+c('96','║'))
    print(c('96','╚══════════════════════════════════════════════════════════════════╝'))
    print(f"  {GR}● ONLINE{c('0','')}  {DIM}LOCAL-FIRST  •  SAFE LAB MODE  •  {platform.system()} {platform.release()}{c('0','')}")

def pause(): input('\n'+DIM+'Press ENTER to continue...'+c('0',''))

class Console:
    def __init__(self): self.lab=LabEngine()
    def menu(self):
        while True:
            banner()
            print('\n  '+CY+'[1]'+c('0','')+' Cryptography')
            print('  '+PR+'[2]'+c('0','')+' Cryptanalysis')
            print('  '+GR+'[3]'+c('0','')+' Network Security')
            print('  '+YL+'[4]'+c('0','')+' Web Security Labs')
            print('  '+RD+'[5]'+c('0','')+' Blue Team')
            print('  '+CY+'[6]'+c('0','')+' Field Toolkit')
            print('  '+YL+'[7]'+c('0','')+' Lab Arena')
            print('  '+WH+'[8]'+c('0','')+' Command Reference')
            print('  '+DIM+'[0]'+c('0','')+' Exit')
            choice=input('\n'+CY+'HN-BLACKBOX › '+c('0','')).strip()
            if choice=='1': self.crypto_menu()
            elif choice=='2': self.analysis_menu()
            elif choice=='3': self.network_menu()
            elif choice=='4': self.web_menu()
            elif choice=='5': self.blue_menu()
            elif choice=='6': self.toolkit_menu()
            elif choice=='7': self.lab_menu()
            elif choice=='8': self.help()
            elif choice=='0': print(GR+'Session closed. HN BlackBox standing by.'+c('0','')); return

    def crypto_menu(self):
        algs=['caesar','vigenere','railfence','affine','atbash','rot13']
        while True:
            banner(); print('\n'+CY+'CRYPTOGRAPHY // ALGORITHM MATRIX'+c('0',''))
            for i,a in enumerate(algs,1): print(f'  [{i}] {a.upper()}')
            print('  [0] Back')
            s=input('\nHN-CRYPTO › ').strip()
            if s=='0': return
            try: alg=algs[int(s)-1]
            except: continue
            self.crypto_run(alg)

    def crypto_run(self,alg):
        banner(); print(f'\n{CY}CRYPTOGRAPHY // {alg.upper()}{c("0","")}\n')
        examples={
            'caesar':['caesar encrypt "HELLO" 3','caesar decrypt "KHOOR" 3'],
            'vigenere':['vigenere encrypt "ATTACKATDAWN" LEMON','vigenere decrypt "LXFOPVEFRNHR" LEMON'],
            'railfence':['railfence encrypt "WEAREDISCOVERED" 3'],
            'affine':['affine encrypt "AFFINE" 5 8'],
            'atbash':['atbash encrypt "HELLO"'], 'rot13':['rot13 encrypt "HELLO"']}
        print(YL+'EXAMPLES'+c('0','')); [print('  '+x) for x in examples[alg]]
        print('\n'+DIM+'Enter a command or type back'+c('0',''))
        while True:
            raw=input('\nHN-CRYPTO › ').strip()
            if raw.lower()=='back': return
            try: print('\n'+self.execute(raw)+'\n')
            except Exception as e: print(RD+f'ERROR: {e}'+c('0',''))

    def execute(self,raw):
        p=shlex.split(raw); 
        if not p: return ''
        cmd=p[0].lower(); a=p[1:]
        if cmd in ('caesar','vigenere','railfence','affine','atbash','rot13'):
            if cmd in ('atbash','rot13'):
                if len(a)<2: return 'Usage: '+cmd+' encrypt "TEXT"'
                text=a[1]
                from core.cryptography.classical.additional import atbash, rot13
                out=atbash.atbash(text) if cmd=='atbash' else rot13.rot13(text)
                return self.result(cmd,text,out)
            if len(a)<3: return 'Usage: '+cmd+' encrypt|decrypt "TEXT" KEY'
            op,text,key=a[0].lower(),a[1],a[2]
            if cmd=='caesar': out=caesar.encrypt(text,int(key)) if op.startswith('enc') else caesar.decrypt(text,int(key))
            elif cmd=='vigenere': out=vigenere.encrypt(text,key) if op.startswith('enc') else vigenere.decrypt(text,key)
            elif cmd=='railfence': out=rail_fence.encrypt(text,int(key)) if op.startswith('enc') else rail_fence.decrypt(text,int(key))
            else:
                if len(a)<4: return 'Usage: affine encrypt "TEXT" a b'
                out=affine.encrypt(text,int(a[2]),int(a[3])) if op.startswith('enc') else affine.decrypt(text,int(a[2]),int(a[3]))
            return self.result(cmd,text,out)
        if cmd=='hash':
            if len(a)<2:return 'Usage: hash sha256 "TEXT"'
            algo=a[0].lower(); out=hashlib.new(algo,a[1].encode()).hexdigest(); return self.result(algo,a[1],out)
        if cmd=='base64':
            if len(a)<2:return 'Usage: base64 encode|decode "TEXT"'
            out=real_tools.b64_encode(a[1]) if a[0]=='encode' else real_tools.b64_decode(a[1]); return self.result('base64',a[1],out)
        if cmd=='url':
            if len(a)<2:return 'Usage: url parse URL'
            u=real_tools.parse_url(a[1]); return '\n'.join(f'{k.upper():<10}: {v}' for k,v in u.items())
        if cmd=='ioc': return json.dumps(real_tools.extract_iocs(a[0] if a else ''),indent=2)
        if cmd=='analyze':
            rows=frequency_analysis.analyze(a[0] if a else ''); return '\n'.join(f"{r['letter']}  {r['count']:>4}  {r['percent']:>6.2f}%" for r in rows[:15]) or 'No letters.'
        if cmd=='network' and a:
            if a[0]=='ip' and len(a)>1:return '\n'.join(f'{k.upper():<14}: {v}' for k,v in network_tools.analyze_ip(a[1]).items())
            if a[0]=='subnet' and len(a)>1:return '\n'.join(f'{k.upper():<14}: {v}' for k,v in network_tools.subnet(a[1]).items())
        if cmd=='lab': return self.lab_command(a)
        if cmd in ('help','?'): return self.help_text()
        return 'Unknown command. Type help.'

    def result(self,name,inp,out): return f'{GR}┌─ RESULT // {name.upper()} ─────────────────────{c("0","")}\n{GR}│{c("0","")} INPUT  : {inp}\n{GR}│{c("0","")} OUTPUT : {WH}{out}{c("0","")}\n{GR}└──────────────────────────────────────────────{c("0","")}'
    def analysis_menu(self):
        banner(); print('\n'+PR+'CRYPTANALYSIS // SIGNAL DESK'+c('0','')); print('  analyze "ciphertext"\n  hash sha256 "text"\n  back');
        while True:
            x=input('\nHN-ANALYSIS › ').strip()
            if x=='back': return
            print(self.execute(x))
    def network_menu(self):
        banner(); print('\n'+GR+'NETWORK SECURITY // LOCAL TOOLKIT'+c('0','')); print('  network ip 192.168.1.10\n  network subnet 192.168.1.0/24\n  back')
        while True:
            x=input('\nHN-NETWORK › ').strip()
            if x=='back': return
            try: print(self.execute(x))
            except Exception as e: print(RD+str(e)+c('0',''))
    def web_menu(self):
        banner(); print('\n'+YL+'WEB SECURITY // SYNTHETIC LAB'+c('0','')); print('  url parse https://example.local/login?id=42\n  base64 decode "SE5fQkxBQ0tCT1g="\n  back')
        while True:
            x=input('\nHN-WEB › ').strip()
            if x=='back': return
            try: print(self.execute(x))
            except Exception as e: print(RD+str(e)+c('0',''))
    def blue_menu(self):
        banner(); print('\n'+RD+'BLUE TEAM // DEFENSE DESK'+c('0','')); print('  ioc "failed login from 203.0.113.9"\n  back')
        while True:
            x=input('\nHN-BLUE › ').strip()
            if x=='back': return
            print(self.execute(x))
    def toolkit_menu(self):
        banner(); print('\n'+CY+'FIELD TOOLKIT'+c('0','')); print('  hash sha256 "text"\n  base64 encode "HN_BLACKBOX"\n  url parse https://example.local/a?q=1\n  ioc "IP 203.0.113.9 hash 0123456789abcdef0123456789abcdef"\n  back')
        while True:
            x=input('\nHN-TOOLKIT › ').strip()
            if x=='back': return
            try: print(self.execute(x))
            except Exception as e: print(RD+str(e)+c('0',''))
    def lab_menu(self):
        while True:
            banner(); p=self.lab.progress(); print(f'\n{YL}LAB ARENA // {p["completed"]}/{p["total"]} COMPLETE // {p["percent"]}% // SCORE {p["score"]}{c("0","")}')
            for i,l in enumerate(LABS,1):
                mark=GR+'✓'+c('0','') if l.id in self.lab.state['completed'] else DIM+'·'+c('0',''); print(f' {i:02d} {mark} {l.id:<12} {l.difficulty:<12} {l.title}')
            print('  [0] Back')
            s=input('\nHN-LABS › ').strip()
            if s=='0':return
            try:self.play_lab(LABS[int(s)-1].id)
            except:continue
    def play_lab(self,lab_id):
        l=self.lab.start(lab_id); start=time.time(); hints=0; banner(); print(f'\n{YL}{l["id"]} // {l["title"]}{c("0","")}\n\n{l["objective"]}\n\n{WH}{l["prompt"]}{c("0","")}')
        print('\n'+DIM+'Type :hint for a hint, :back to leave.'+c('0',''))
        while True:
            a=input('\nHN-LAB › ').strip()
            if a==':back':return
            if a==':hint': hints+=1; print(YL+'HINT: '+l['hint']+c('0','')); continue
            r=self.lab.check(lab_id,a,hints,time.time()-start); print(GR+'CORRECT  '+str(r['score'])+' pts'+c('0','') if r['correct'] else RD+'NOT YET — try again.'+c('0',''))
            if r['correct']: pause(); return
    def help_text(self): return '''COMMANDS\n  crypto: caesar|vigenere|railfence|affine|atbash|rot13\n  hash sha256 "text"\n  base64 encode|decode "text"\n  url parse URL\n  ioc "text"\n  analyze "text"\n  network ip IP\n  network subnet CIDR\n  lab ID\n  help\n\nThe console is allow-listed and does not run arbitrary OS shell commands.'''
    def help(self): banner(); print('\n'+self.help_text()); pause()
    def lab_command(self,a):
        if not a:return 'Usage: lab list | lab ID'
        if a[0]=='list':return '\n'.join(f'{x.id:<12} {x.difficulty:<12} {x.title}' for x in LABS)
        l=self.lab.start(a[0]); return f"{l['id']} // {l['title']}\n{l['prompt']}\nHINT: {l['hint']}"

def main():
    ap=argparse.ArgumentParser(description='HN BlackBox v40.0.0 terminal console')
    ap.add_argument('command',nargs='*',help='optional one-shot BlackBox command')
    ns=ap.parse_args(); app=Console()
    if ns.command:
        print(app.execute(' '.join(ns.command))); return 0
    app.menu(); return 0
if __name__=='__main__': raise SystemExit(main())

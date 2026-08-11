"""Educational cryptanalysis helpers for classical ciphers."""
from collections import Counter
import math
from ..cryptography.extended_algorithms import caesar, vigenere

ENGLISH_FREQ = {"E":12.70,"T":9.06,"A":8.17,"O":7.51,"I":6.97,"N":6.75,"S":6.33,"H":6.09,"R":5.99,"D":4.25,"L":4.03,"C":2.78,"U":2.76,"M":2.41,"W":2.36,"F":2.23,"G":2.02,"Y":1.97,"P":1.93,"B":1.49,"V":0.98,"K":0.77,"J":0.15,"X":0.15,"Q":0.10,"Z":0.07}
def clean(text): return "".join(c for c in text.upper() if c.isalpha())
def index_of_coincidence(text):
    s=clean(text); n=len(s)
    if n<2:return 0.0
    c=Counter(s)
    return sum(v*(v-1) for v in c.values())/(n*(n-1))
def chi_square(text):
    s=clean(text); n=len(s)
    if not n:return float("inf")
    c=Counter(s)
    return sum(((c.get(ch,0)-n*p/100)**2)/(n*p/100) for ch,p in ENGLISH_FREQ.items())
def caesar_rank(text):
    rows=[]
    for key,plain in caesar.brute_force(text):
        score=chi_square(plain)
        rows.append((score,key,plain))
    return sorted(rows)
def repeated_ngrams(text,min_len=3,max_len=5):
    s=clean(text); found=[]
    for n in range(min_len,max_len+1):
        positions={}
        for i in range(len(s)-n+1):
            gram=s[i:i+n]; positions.setdefault(gram,[]).append(i)
        for gram,pos in positions.items():
            if len(pos)>1: found.append((gram,pos))
    return sorted(found,key=lambda x:(-len(x[0]),x[1][0]))
def kasiski(text):
    repeats=repeated_ngrams(text,3,5); distances=[]
    for _,pos in repeats:
        distances += [pos[i+1]-pos[i] for i in range(len(pos)-1)]
    factors=Counter()
    for d in distances:
        for f in range(2,min(d,20)+1):
            if d%f==0:factors[f]+=1
    return repeats, factors.most_common()
def vigenere_columns(text,key_len):
    s=clean(text); return [s[i::key_len] for i in range(key_len)]
def estimate_vigenere_key_lengths(text,max_len=12):
    s=clean(text); rows=[]
    for k in range(1,min(max_len,len(s))+1):
        cols=vigenere_columns(s,k)
        ic=sum(index_of_coincidence(c) for c in cols)/len(cols)
        rows.append((ic,k))
    return sorted(rows,reverse=True)

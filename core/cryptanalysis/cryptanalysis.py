"""Real, local cryptanalysis primitives for classical ciphers.

No network operations and no modification of cryptography primitives.
"""
from collections import Counter
import math
import string
from ..cryptography.classical import caesar, vigenere

ENGLISH_FREQ = {"E":12.70,"T":9.06,"A":8.17,"O":7.51,"I":6.97,"N":6.75,"S":6.33,"H":6.09,"R":5.99,"D":4.25,"L":4.03,"C":2.78,"U":2.76,"M":2.41,"W":2.36,"F":2.23,"G":2.02,"Y":1.97,"P":1.93,"B":1.49,"V":0.98,"K":0.77,"J":0.15,"X":0.15,"Q":0.10,"Z":0.07}
# Approximate Arabic letter frequencies for comparative analysis (not a language model).
ARABIC_FREQ = {"ا":12.0,"ل":10.0,"م":8.0,"ن":7.0,"و":6.5,"ي":6.2,"ر":5.5,"ب":5.0,"ت":4.8,"ع":4.5,"د":4.0,"س":3.8,"ك":3.5,"ه":3.4,"ج":3.0,"ف":2.8,"ح":2.6,"ق":2.4,"خ":2.1,"ص":1.9,"ش":1.7,"ذ":1.5,"ز":1.3,"ض":1.2,"ط":1.0,"ظ":0.7,"ث":0.6,"غ":0.5}

def clean(text):
    return "".join(c for c in text.upper() if c in string.ascii_uppercase)

def _language_profile(text):
    ar=sum('\u0600'<=c<='\u06ff' for c in text); en=sum(c.upper() in string.ascii_uppercase for c in text)
    return 'AR' if ar>en else 'EN'

def frequency_profile(text, language='auto'):
    language=language.upper()
    if language=='AUTO': language=_language_profile(text)
    alphabet = ARABIC_FREQ if language=='AR' else ENGLISH_FREQ
    letters=[c.lower() if language=='AR' else c.upper() for c in text if (c.lower() if language=='AR' else c.upper()) in alphabet]
    n=len(letters); counts=Counter(letters)
    rows=[]
    for ch,expected in alphabet.items():
        observed=(counts[ch]/n*100) if n else 0.0
        rows.append({'letter':ch,'count':counts[ch],'percent':round(observed,3),'expected':expected,'delta':round(observed-expected,3)})
    rows.sort(key=lambda r:r['percent'],reverse=True)
    return {'language':language,'letters':n,'rows':rows}

def frequency_match_score(text, language='auto'):
    prof=frequency_profile(text,language); rows=prof['rows'];
    if not prof['letters']: return 0.0
    # normalized L1 distance -> 0..100 similarity
    dist=sum(abs(r['percent']-r['expected']) for r in rows)/2
    return max(0.0,min(100.0,100.0-dist))

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

_COMMON_NGRAMS = {
    'THE': 3.0, 'AND': 2.7, 'ING': 2.5, 'ION': 2.1, 'TH': 1.7, 'HE': 1.7, 'IN': 1.6, 'ER': 1.5,
    'AN': 1.4, 'RE': 1.3, 'ON': 1.3, 'AT': 1.2, 'EN': 1.2, 'ND': 1.1, 'TI': 1.1, 'ES': 1.1, 'OR': 1.1,
    'HELLO': 5.0, 'WORLD': 5.0, 'THIS': 3.5, 'THAT': 3.5, 'IS': 1.2, 'TO': 1.2, 'OF': 1.2, 'FOR': 1.8,
}

def _english_ngram_score(text):
    s=clean(text);
    if not s: return 0.0
    return sum(weight for gram,weight in _COMMON_NGRAMS.items() if gram in s) / max(1.0, len(s)/10.0)

def _caesar_records(text):
    rows=[]
    for key,plain in caesar.brute_force(text):
        chi=chi_square(plain)
        match=frequency_match_score(plain,'EN')
        ngram=_english_ngram_score(plain)
        composite=chi - (ngram*18.0)
        probability=max(0.0,min(100.0, match + ngram*6.0))
        rows.append({'key':key,'plaintext':plain,'chi_square':chi,'ngram_score':round(ngram,3),'probability':round(probability,2),'composite':composite})
    return sorted(rows,key=lambda r:(r['composite'], r['chi_square']))

def caesar_candidates(text):
    """Return rich candidate records for modern analysis consumers."""
    return _caesar_records(text)

def caesar_rank(text):
    """Backward-compatible tuple API: (chi_square, key, plaintext)."""
    return [(r['chi_square'], r['key'], r['plaintext']) for r in _caesar_records(text)]

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
    for _,pos in repeats: distances += [pos[i+1]-pos[i] for i in range(len(pos)-1)]
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
        cols=vigenere_columns(s,k); ic=sum(index_of_coincidence(c) for c in cols)/len(cols)
        rows.append((ic,k))
    return sorted(rows,reverse=True)

def recover_vigenere_key(text,key_len):
    """Recover a Vigenere key candidate using per-column chi-square (English)."""
    s=clean(text);
    if key_len<1 or key_len>len(s): raise ValueError('invalid key length')
    key=[]; shifts=[]
    for col in vigenere_columns(s,key_len):
        ranked=[]
        for shift in range(26):
            plain=''.join(chr((ord(ch)-65-shift)%26+65) for ch in col)
            ranked.append((chi_square(plain),shift))
        _,shift=min(ranked); shifts.append(shift); key.append(chr(65+shift))
    k=''.join(key); return {'key':k,'plaintext':vigenere.decrypt(text,k),'key_length':key_len,'score':round(frequency_match_score(vigenere.decrypt(text,k),'EN'),2)}

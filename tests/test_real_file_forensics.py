import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PIL import Image
from PIL.PngImagePlugin import PngInfo
from pypdf import PdfWriter, PdfReader
from core.intelligence.file_forensics import analyze_file, scrub_metadata


def test_real_image_fingerprint_and_exif_metadata():
    with tempfile.TemporaryDirectory() as td:
        src=Path(td)/'evidence.jpg'
        im=Image.new('RGB',(32,20),'black')
        exif=im.getexif(); exif[270]='HN Evidence'; exif[315]='Analyst'; exif[305]='HN Camera'; exif[306]='2026:09:08 12:34:56'
        im.save(src,format='JPEG',exif=exif.tobytes(),quality=90)
        r=analyze_file(src)
        assert r['type']=='JPEG image'
        assert len(r['md5'])==32 and len(r['sha256'])==64
        keys={m['key'] for m in r['metadata']}
        assert 'EXIF:Artist' in keys and 'EXIF:Software' in keys and 'EXIF:DateTime' in keys


def test_png_selective_scrub_preserves_unselected_metadata():
    with tempfile.TemporaryDirectory() as td:
        src=Path(td)/'evidence.png'; out=Path(td)/'clean.png'
        info=PngInfo(); info.add_text('Author','Analyst'); info.add_text('Comment','Keep me')
        Image.new('RGB',(8,8),'white').save(src,pnginfo=info)
        before=analyze_file(src)
        result=scrub_metadata(src,out,fields=['Author'],full_strip=False)
        after=analyze_file(out)
        assert result['source']==str(src.resolve())
        assert result['output']==str(out.resolve())
        assert before['sha256'] != after['sha256']
        keys={m['key']:m['value'] for m in after['metadata']}
        assert 'INFO:Comment' in keys and 'INFO:Author' not in keys
        assert src.read_bytes() == src.read_bytes()


def test_pdf_full_strip_removes_document_info_without_overwriting_source():
    with tempfile.TemporaryDirectory() as td:
        src=Path(td)/'evidence.pdf'; out=Path(td)/'evidence_CLEAN.pdf'
        w=PdfWriter(); w.add_blank_page(width=300,height=200); w.add_metadata({'/Author':'Analyst','/Creator':'HN BLACKBOX','/Title':'Case 42','/Producer':'Producer X'})
        with src.open('wb') as fh: w.write(fh)
        before=analyze_file(src); assert any(m['key']=='Author' for m in before['metadata'])
        result=scrub_metadata(src,out,full_strip=True)
        after=analyze_file(out)
        assert src.exists() and out.exists()
        assert not any(m['key'] in {'Author','Creator','Producer','Title'} for m in after['metadata'])
        assert before['sha256'] != after['sha256']


def test_office_core_metadata_scrub():
    with tempfile.TemporaryDirectory() as td:
        src=Path(td)/'evidence.docx'; out=Path(td)/'clean.docx'
        import zipfile
        from xml.etree import ElementTree as ET
        core=b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:creator>Analyst</dc:creator><cp:lastModifiedBy>Analyst2</cp:lastModifiedBy></cp:coreProperties>'''
        with zipfile.ZipFile(src,'w',zipfile.ZIP_DEFLATED) as z: z.writestr('docProps/core.xml',core); z.writestr('word/document.xml',b'<w:document/>')
        r=analyze_file(src); assert any(m['key']=='Author' for m in r['metadata'])
        scrub_metadata(src,out,fields=['Author'])
        r2=analyze_file(out); assert not any(m['key']=='Author' for m in r2['metadata'])

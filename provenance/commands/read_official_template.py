from pathlib import Path
from urllib.request import urlopen, Request
import re, json, hashlib, zipfile, xml.etree.ElementTree as ET
out=Path('ALBUS26_major_revision/reports/external');out.mkdir(exist_ok=True)
u='https://albus.lat/templates'
html=urlopen(Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode()
urls=['https:'+v if v.startswith('//') else v for v in re.findall(r'(?:https:)?//[^"<>\s]+?\.docx(?:\?[^"<>\s]*)?',html)]
print(json.dumps(urls[:10]))
for i,url in enumerate(dict.fromkeys(urls)):
    if i>0:break
    p=out/f'albus_template_{i}.docx';p.write_bytes(urlopen(url,timeout=30).read())
    with zipfile.ZipFile(p) as z:
        root=ET.fromstring(z.read('word/document.xml'))
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    text='\n'.join(''.join(p.itertext()) for p in root.findall('.//w:p',ns))
    (out/f'albus_template_{i}.txt').write_text(text,encoding='utf-8')
    print(i,hashlib.sha256(p.read_bytes()).hexdigest())
    print('\n'.join(line for line in text.splitlines() if any(w in line.lower() for w in ['apa','reference','citation','bibliog'])))
(out/'template_sources.json').write_text(json.dumps({'page':u,'urls':list(dict.fromkeys(urls))},indent=2),encoding='utf-8')

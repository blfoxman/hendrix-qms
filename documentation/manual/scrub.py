# Fictional names and numbers for training media: applied to the page just before every screenshot.
# Manuals, videos and marketing never show real company names, license numbers or people.
import json
REPL = [(r'Sam Salari', 'Alex Rivera'), (r'SAM SALARI', 'ALEX RIVERA'), (r'\bSalari\b', 'Rivera'), (r'Division of Cannabis Regulation', 'Marijuana Enforcement Division'), (r'19 CSR 100(-1)?', '1 CCR 212'), (r'Heritage Cul 60', 'Northfield Farms'), (r'Heritage Cul 22', 'Northfield East'), (r'CUL000060', 'CUL-71542'), (r'CUL000022', 'CUL-71588'), (r'\bCul 60\b', 'Farm 2'), (r'\bCUL 60\b', 'FARM 2'),
        (r'HERITAGE CUL 60', 'NORTHFIELD FARMS'), (r'Black Fox', 'Northfield Labs'), (r'BLACK FOX', 'NORTHFIELD LABS'), (r'MAN000109', 'MFG-48213'), (r'Green Acres', 'Cedar Hollow'),
        (r'Missouri', 'Colorado'), (r'MISSOURI', 'COLORADO'), (r'\bSam\b', 'Alex Rivera'), (r'Lee Worker', 'Lee Chen'), (r'Kiosk Kim', 'Kim Alvarez'),
        (r'Futurola USA', 'Coneline Supply'), (r'Futurola', 'Coneline'), (r'Show-Me Labs', 'Peak Analytical'), (r'Show-Me', 'Peak'), (r'\bsam@', 'alex.rivera@'), (r'@dcr\.', '@med.'), (r'northfieldlabsmfg', 'northfieldlabs'), (r'Noble Chemical Co\.', 'Clearwater Chemical Co.'), (r'Noble Chemical', 'Clearwater Chemical'),
        (r'OHAUS Ranger', 'Bench scale 30 kg'), (r'Acme Scale', 'Precision Scale Co.'), (r'TES000777', 'LAB-30918'), (r'19 CSR 100-1\.\d+', '1 CCR 212-3'), (r'\bDCR\b', 'MED'),
        (r'https?://app\.test/hendrix/', 'https://hendrixqms.com/northfield/'), (r'\bs@x\b', 'alex.rivera@northfieldlabs.com'), (r'sam@hendrixqms\.com', 'alex.rivera@northfieldlabs.com'), (r'maria@x\.com', 'maria.lopez@northfieldlabs.com'),
        (r'@blackfox\.test', '@northfieldlabs.com'), (r'blackfox', 'northfieldlabs'), (r'Key Stone', 'Lakeshore Labs'), (r'KEY STONE', 'LAKESHORE LABS'), (r'\bMI-1\b', 'PRC-20417'),
        (r'Michigan', 'Oregon'), (r'MICHIGAN', 'OREGON'), (r'\bCRA\b', 'OLCC'), (r'R 420\.\d+', 'OAR 845-025'), (r'Summit Solutions', 'Northfield Group'), (r'summitsolutions', 'northfield'),
        (r'Muha Meds?', 'Brightline'), (r'Heritage', 'Northfield Farms'), (r'Perryville', 'Riverside')]
SCRUB_JS = '''(R)=>{const rx=R.map(([a,b])=>[new RegExp(a,'g'),b]);
const fix=s=>{let o=s;for(const [a,b] of rx)o=o.replace(a,b);return o;};
const U=window.__hxUndo=window.__hxUndo||[];
const walk=n=>{if(n.nodeType===3){const v=fix(n.nodeValue);if(v!==n.nodeValue){U.push([n,'#t',n.nodeValue]);n.nodeValue=v;}return;}
 if(n.nodeType!==1||n.tagName==='SCRIPT'||n.tagName==='STYLE')return;
 for(const a of ['placeholder','title'])if(n.hasAttribute(a)){const v=fix(n.getAttribute(a));if(v!==n.getAttribute(a)){U.push([n,a,n.getAttribute(a)]);n.setAttribute(a,v);}}
 if((n.tagName==='INPUT'||n.tagName==='TEXTAREA')&&n.value){const v=fix(n.value);if(v!==n.value){U.push([n,'#v',n.value]);n.value=v;}}
 n.childNodes.forEach(walk);};
walk(document.body);}'''
# put the page back after the shot, so later steps still find the real text
UNDO_JS = '''()=>{const U=window.__hxUndo||[];while(U.length){const [n,k,v]=U.pop();if(k==='#t')n.nodeValue=v;else if(k==='#v')n.value=v;else n.setAttribute(k,v);}}'''
def scrub(pg):
    try: pg.evaluate(SCRUB_JS, [[a.replace('\\b', '\\b'), b] for a, b in REPL])
    except Exception as e: print('scrub failed', e)
def unscrub(pg):
    try: pg.evaluate(UNDO_JS)
    except Exception: pass
def install():
    import playwright.sync_api as s
    _ps = s.Page.screenshot; _ls = s.Locator.screenshot
    def ps(self, *a, **k):
        scrub(self)
        try: return _ps(self, *a, **k)
        finally: unscrub(self)
    def ls(self, *a, **k):
        scrub(self.page)
        try: return _ls(self, *a, **k)
        finally: unscrub(self.page)
    s.Page.screenshot = ps; s.Locator.screenshot = ls

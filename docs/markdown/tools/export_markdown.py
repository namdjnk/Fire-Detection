from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET
import hashlib, json, re, posixpath

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/markdown'
(OUT / 'assets/word').mkdir(parents=True, exist_ok=True)
(OUT / 'assets/slides').mkdir(parents=True, exist_ok=True)
NS = {k: v for k, v in [
    ('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'),
    ('a', 'http://schemas.openxmlformats.org/drawingml/2006/main'),
    ('p', 'http://schemas.openxmlformats.org/presentationml/2006/main'),
    ('r', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'),
    ('m', 'http://schemas.openxmlformats.org/officeDocument/2006/math')]}
sources = []
stats = {}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source(path):
    sources.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size})

def write(name, text):
    (OUT / name).write_text(text, encoding='utf-8', newline='')

def lname(el):
    return ET.QName(el).localname

def rels(z, part):
    name = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    if name not in z.namelist():
        return {}
    return {x.get('Id'): (x.get('Target') if x.get('TargetMode') == 'External' else
            posixpath.normpath(posixpath.join(posixpath.dirname(part), x.get('Target'))).lstrip('/'))
            for x in ET.fromstring(z.read(name))}

def table(rows):
    if not rows:
        return ''
    width = max(map(len, rows))
    rows = [r + [''] * (width-len(r)) for r in rows]
    lines = ['| ' + ' | '.join(c.replace('|', '&#124;').replace('\n', '<br>') for c in r) + ' |' for r in rows]
    lines.insert(1, '| ' + ' | '.join(['---'] * width) + ' |')
    return '\n'.join(lines)

def math(el):
    tag = lname(el)
    def child(name):
        x = el.find('m:' + name, NS)
        return math(x) if x is not None else ''
    if tag == 't': return el.text or ''
    if tag.endswith('Pr'): return ''
    if tag == 'f': return '(' + child('num') + ')/(' + child('den') + ')'
    if tag == 'sSub': return child('e') + '_{' + child('sub') + '}'
    if tag == 'sSup': return child('e') + '^{' + child('sup') + '}'
    if tag == 'sSubSup': return child('e') + '_{' + child('sub') + '}^{' + child('sup') + '}'
    if tag == 'rad': return 'sqrt(' + child('e') + ')' if not child('deg') else 'root[' + child('deg') + '](' + child('e') + ')'
    return ''.join(math(c) for c in el)

code_files = sorted(p for p in (ROOT / 'fire_detection').rglob('*') if p.is_file() and p.suffix in {'.py', '.yaml', '.yml', '.txt', '.json', '.ipynb', '.ps1', '.sh'} and '__pycache__' not in p.parts)
parts = ['# Bản sao code hiện tại\n\nNgày chụp nội dung: 28/10/2026. Nội dung mỗi file được giữ nguyên trong khối mã. Đây là tài liệu để đọc code; chạy chương trình bằng các file nguồn gốc. Weight `.pt`, môi trường Python và dữ liệu/video không được chuyển thành văn bản.\n']
for p in code_files:
    source(p)
    content = p.read_bytes().decode('utf-8-sig')
    fence = '`' * max(3, max((len(m.group()) + 1 for m in re.finditer(r'`+', content)), default=3))
    language = {'.py': 'python', '.yaml': 'yaml', '.yml': 'yaml', '.txt': 'text', '.ipynb': 'json'}.get(p.suffix, 'text')
    parts.append(f'## {p.relative_to(ROOT).as_posix()}\n\nNguồn: `{p.relative_to(ROOT).as_posix()}`\n\n{fence}{language}\n{content}' + ('' if content.endswith('\n') else '\n') + fence + '\n')
    assert content in parts[-1]
write('01_CODE_HIEN_TAI.md', '\n'.join(parts))
stats['code_files'] = len(code_files)

doc = ROOT / 'report_revision/fix_review_20261027/output/smoke_fire_detection.docx'
source(doc)
z = ZipFile(doc)
doc_images = set()
table_count = 0
math_count = 0
def inline(el, relationships):
    global math_count
    tag = lname(el)
    if tag == 't': return el.text or ''
    if tag in {'tab'}: return '    '
    if tag in {'br', 'cr'}: return '\n'
    if tag == 'oMath':
        math_count += 1
        return '`' + math(el) + '`'
    if tag == 'blip':
        rid = el.get('{' + NS['r'] + '}embed')
        if rid and rid in relationships:
            target = relationships[rid]
            dest = 'assets/word/' + posixpath.basename(target)
            (OUT / dest).write_bytes(z.read(target))
            doc_images.add(dest)
            return '\n\n![Hình trong báo cáo](' + dest + ')\n\n'
        return ''
    if tag == 'hyperlink':
        text = ''.join(inline(c, relationships) for c in el)
        target = relationships.get(el.get('{' + NS['r'] + '}id'))
        return f'[{text}](<{target}>)' if target else text
    if tag in {'pPr', 'rPr', 'instrText', 'del'}: return ''
    return ''.join(inline(c, relationships) for c in el)

def blocks(el, relationships):
    global table_count
    result = []
    for c in el:
        tag = lname(c)
        if tag == 'p':
            txt = inline(c, relationships).strip()
            if not txt: continue
            styles = c.xpath('./w:pPr/w:pStyle/@w:val', namespaces=NS)
            style = styles[0] if styles else ''
            prefix = {'Title': '# ', 'FrontHeading': '## ', 'AppendixHeading': '## ', 'Heading1': '## ', 'Heading2': '### ', 'Heading3': '#### '}.get(style, '')
            if style == 'CodeSource': txt = '```text\n' + txt + '\n```'
            result.append(prefix + txt)
        elif tag == 'tbl':
            table_count += 1
            rows = [[blocks(cell, relationships) for cell in row.findall('w:tc', NS)] for row in c.findall('w:tr', NS)]
            result.append(table(rows))
        elif tag in {'sdt', 'sdtContent', 'customXml'}:
            result.append(blocks(c, relationships))
    return '\n\n'.join(result)

root = ET.fromstring(z.read('word/document.xml'))
text = '# Báo cáo Word chuyển sang Markdown\n\nNguồn: `' + doc.relative_to(ROOT).as_posix() + '`\n\nBản trích nội dung ngày 28/10/2026, giữ thứ tự đoạn, bảng và hình. Công thức được chuyển sang ký hiệu văn bản với dấu ngoặc thể hiện phân số. Số trang trong mục lục thuộc bản Word, không phải trang Markdown. Font, lề, ngắt trang và ô gộp không được tái hiện đầy đủ.\n\n---\n\n'
text += blocks(root.find('w:body', NS), rels(z, 'word/document.xml'))
for part in z.namelist():
    if re.match(r'word/(header\d+|footer\d+|footnotes|endnotes)\.xml$', part):
        content = blocks(ET.fromstring(z.read(part)), rels(z, part))
        if part.endswith(('footnotes.xml','endnotes.xml')):
            content = '\n\n'.join(blocks(c, rels(z,part)) for c in ET.fromstring(z.read(part)) if int(c.get('{' + NS['w'] + '}id','-1')) > 0)
        if content: text += '\n\n## Phần phụ từ ' + posixpath.basename(part) + '\n\n' + content
write('02_BAO_CAO_WORD.md', text + '\n')
original_runs = root.xpath('//w:t/text()', namespaces=NS)
missing = [t for t in original_runs if t.strip() and t.strip() not in text.replace('&#124;', '|')]
assert not missing, missing[:10]
stats.update(word_tables=table_count, word_images=len(doc_images), word_formulas=math_count, word_text_runs_checked=len(original_runs), word_missing_text_runs=len(missing))

ppt = ROOT / 'report_revision/fix_review_20261027/output/smoke_fire_detection.pptx'
source(ppt)
z = ZipFile(ppt)
pr = ET.fromstring(z.read('ppt/presentation.xml'))
relationships = rels(z, 'ppt/presentation.xml')
slides = [relationships[s.get('{' + NS['r'] + '}id')] for s in pr.findall('p:sldIdLst/p:sldId', NS)]
parts = ['# Báo cáo PowerPoint chuyển sang Markdown\n\nNguồn: `' + ppt.relative_to(ROOT).as_posix() + '`\n\nBản sao nội dung ngày 28/10/2026. Mỗi slide có chữ, bảng, ghi chú thuyết trình nếu có và ảnh toàn slide để giữ quan hệ giữa các khối, sơ đồ và biểu đồ. Thứ tự khối chữ dựa trên cấu trúc đối tượng của PowerPoint; xem ảnh để xác định vị trí. Hiệu ứng động và video không chạy trong Markdown.\n']
ppt_runs = 0
notes_runs = 0
for i, part in enumerate(slides, 1):
    sr = ET.fromstring(z.read(part))
    chunks = [f'## Slide {i:02d}\n\n![Toàn cảnh slide {i}](assets/slides/slide_{i:02d}.png)\n\n### Nội dung\n']
    def walk(el):
        for c in el:
            tag = lname(c)
            if tag == 'tbl':
                rows = [['<br>'.join(''.join(p.xpath('.//a:t/text()', namespaces=NS)) for p in cell.findall('a:txBody/a:p', NS)) for cell in row.findall('a:tc', NS)] for row in c.findall('a:tr', NS)]
                chunks.append(table(rows))
            elif tag == 'txBody':
                lines = [''.join(p.xpath('.//a:t/text()', namespaces=NS)) for p in c.findall('a:p', NS)]
                txt = '\n\n'.join(x for x in lines if x)
                if txt: chunks.append(txt)
            else: walk(c)
    walk(sr)
    rr = rels(z, part)
    note_parts = [v for v in rr.values() if v.startswith('ppt/notesSlides/') and v.endswith('.xml')]
    for note_part in note_parts:
        nr = ET.fromstring(z.read(note_part))
        note_lines=[]
        for shape in nr.findall('.//p:sp', NS):
            ph = shape.find('p:nvSpPr/p:nvPr/p:ph',NS)
            if ph is not None and ph.get('type') in {'sldImg','sldNum','hdr','ftr','dt'}: continue
            note_lines.extend(''.join(p.xpath('.//a:t/text()', namespaces=NS)) for p in shape.findall('p:txBody/a:p',NS))
        if any(note_lines):
            chunks.append('### Ghi chú thuyết trình\n\n' + '\n\n'.join(x for x in note_lines if x))
            notes_runs += len(note_lines)
    rendered = '\n\n'.join(chunks)
    runs = sr.xpath('//a:t/text()', namespaces=NS)
    assert all(t.strip() in rendered.replace('&#124;', '|') for t in runs if t.strip()), i
    ppt_runs += len(runs)
    parts.append(rendered)
write('03_BAO_CAO_POWERPOINT.md', '\n\n---\n\n'.join(parts) + '\n')
stats.update(slides=len(slides), slide_text_runs_checked=ppt_runs, notes_paragraphs=notes_runs)
for item in sources:
    assert sha(ROOT / item['path']) == item['sha256']
manifest = {'created_date': __import__('datetime').date.today().isoformat(), 'sources': sources, 'validation': stats}
write('FILE_MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(stats, ensure_ascii=False, indent=2))

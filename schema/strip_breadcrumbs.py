import re, html, sys

path = 'full_unpacked/word/document.xml'
x = open(path, encoding='utf-8').read()

spans = [(m.start(), m.end()) for m in re.finditer(r'<w:p(?: [^>]*)?(?:/>|>.*?</w:p>)', x, re.S)]

def txt(i):
    return html.unescape(''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', x[spans[i][0]:spans[i][1]], re.S)))

ts = [txt(i) for i in range(len(spans))]

starts = [i for i, t in enumerate(ts) if t.strip() == '"@type": "BreadcrumbList",']
print('BreadcrumbList blocks found:', len(starts))

edits = []  # (para_index, action) action: 'del' or replacement xml
for i in starts:
    open_i = i - 1
    assert ts[open_i].strip() == '{', (i, repr(ts[open_i]))
    j = i
    while not ts[j].strip().startswith(']'):
        j += 1
        assert j - i < 40, ('runaway at', i)
    close_i = j + 1
    assert ts[close_i].strip() == '},    {', (i, repr(ts[close_i]))
    for k in range(open_i, close_i):
        edits.append((k, None))
    # the merged "},    {" paragraph becomes a plain "    {" — reuse the opening
    # paragraph's XML so formatting is byte-identical to the brace it replaces
    edits.append((close_i, x[spans[open_i][0]:spans[open_i][1]]))

edits.sort()
assert len(set(k for k, _ in edits)) == len(edits), 'overlapping blocks'

out = []
prev = 0
for k, repl in edits:
    s, e = spans[k]
    out.append(x[prev:s])
    if repl is not None:
        out.append(repl)
    prev = e
out.append(x[prev:])
new = ''.join(out)

open(path, 'w', encoding='utf-8').write(new)
print('paragraphs removed:', sum(1 for _, r in edits if r is None))
print('paragraphs rewritten:', sum(1 for _, r in edits if r is not None))
print('bytes: %d -> %d' % (len(x), len(new)))

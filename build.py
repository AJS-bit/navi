"""처리방침 md → 정적 페이지(index.html · privacy.html). 표 · 목록 · 굵게 · 링크 · 코드만 다룬다."""
import html, re, sys, pathlib
here = pathlib.Path(__file__).parent
src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
src = re.sub(r'<!--.*?-->', '', src, flags=re.S).strip()

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(https?://[^\s)<]+)', r'<a href="\1">\1</a>', t)
    return t

out, lines, i = [], src.splitlines(), 0
title = 'NAVI 개인정보처리방침'
while i < len(lines):
    l = lines[i]
    if l.startswith('# '):
        title = l[2:].strip(); out.append(f'<h1>{inline(title)}</h1>'); i += 1
    elif l.startswith('## '):
        out.append(f'<h2>{inline(l[3:])}</h2>'); i += 1
    elif l.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
        head, body = rows[0], [r for r in rows[1:] if not set(''.join(r)) <= set('-: ')]
        t = '<div class="table"><table><thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr></thead><tbody>'
        t += ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body) + '</tbody></table></div>'
        out.append(t)
    elif l.startswith('- '):
        items = []
        while i < len(lines) and lines[i].startswith('- '):
            items.append(lines[i][2:]); i += 1
        out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>')
    elif l.strip():
        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '|', '- ')):
            para.append(lines[i]); i += 1
        out.append(f'<p>{inline(" ".join(para))}</p>')
    else:
        i += 1

CSS = '''
:root{--bg:#EDF0F7;--surface:#FFFFFF;--ink:#141B2D;--ink-2:#4A5570;--line:#D9DFEC;--brand:#3355E8;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#080C16;--surface:#121A2B;--ink:#E8ECF5;--ink-2:#A3AEC6;--line:#26314A;--brand:#7D96FF;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 "IBM Plex Sans KR",-apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;word-break:keep-all;overflow-wrap:anywhere}
main{max-width:46rem;margin:0 auto;padding:40px 16px 64px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:28px 24px}
h1{font-size:1.6rem;line-height:1.3;margin:0 0 12px;text-wrap:balance}
h2{font-size:1.1rem;margin:32px 0 8px;padding-top:20px;border-top:1px solid var(--line)}
p,li{color:var(--ink)}
ul{padding-left:1.2em}
a{color:var(--brand)}
code{font-size:.9em;background:var(--bg);padding:1px 5px;border-radius:5px}
.table{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:.92rem;min-width:32rem}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--bg);color:var(--ink-2);font-weight:600}
.foot{color:var(--ink-2);font-size:.85rem;margin-top:20px}
'''
def page(t, body):
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(t)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600;700&display=swap">
<style>{CSS}</style></head><body><main><div class="card">
{body}
</div></main></body></html>
'''
dest = pathlib.Path(sys.argv[2]); dest.mkdir(parents=True, exist_ok=True)
(dest / 'privacy.html').write_text(page(title, '\n'.join(out)), encoding='utf-8')
(dest / 'index.html').write_text(page('NAVI 가계부', '''<h1>NAVI 가계부</h1>
<p>쓴 돈이 월급의 몇 %인지 늘 보이고, 선을 넘으면 폰이 먼저 알려 주는 안드로이드 가계부예요. 기록은 폰 안에만 있어요.</p>
<ul><li><a href="privacy.html">개인정보처리방침</a></li></ul>'''), encoding='utf-8')
(dest / '.nojekyll').write_text('', encoding='utf-8')
print('ok', len(out))

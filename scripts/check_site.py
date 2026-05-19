from pathlib import Path
import re, sys
root=Path(__file__).resolve().parents[1]
fail=[]
for f in root.rglob('*.html'):
    s=f.read_text()
    if '<title>' not in s: fail.append(f'{f}: missing title')
    if 'name="description"' not in s: fail.append(f'{f}: missing meta description')
    if 'rel="canonical"' not in s: fail.append(f'{f}: missing canonical')
    h1_count = len(re.findall(r'<h1\b', s))
    if h1_count != 1:
        fail.append(f'{f}: h1 count {h1_count}')
    if 'name="ai-access"' not in s: fail.append(f'{f}: missing ai meta')
for req in ['robots.txt','sitemap.xml','llms.txt','assets/styles.css']:
    if not (root/req).exists(): fail.append(f'missing {req}')
print('PASS' if not fail else '\n'.join(fail))
sys.exit(1 if fail else 0)

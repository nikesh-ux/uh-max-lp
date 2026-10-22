#!/usr/bin/env python3
"""Inline every image/svg from index.src.html into a self-contained index.html.

Edit index.src.html, then run:  python3 -I build.py
"""
import base64, json, os, re

D = os.path.dirname(os.path.abspath(__file__))

def uri(path, mime):
    with open(path, 'rb') as f:
        return f'data:{mime};base64,' + base64.b64encode(f.read()).decode()

src = open(os.path.join(D, 'index.src.html'), encoding='utf-8').read()

jpgs = {n[:-4]: uri(os.path.join(D, 'img', n), 'image/jpeg')
        for n in sorted(os.listdir(os.path.join(D, 'img'))) if n.endswith('.jpg')}

# static <img src="img/x.jpg">
src = re.sub(r'src="img/([\w-]+)\.jpg"', lambda m: f'src="{jpgs[m.group(1)]}"', src)
# JS image map
src = re.sub(r'/\*IM\*/.*?/\*IM_END\*/', lambda m: 'const IM=' + json.dumps(jpgs) + ';', src, flags=re.S)
# hero orbs (webp)
orbs={n[:-5]:uri(os.path.join(D,'img','orbs',n),'image/webp') for n in sorted(os.listdir(os.path.join(D,'img','orbs'))) if n.endswith('.webp')}
src=re.sub(r'/\*OR\*/.*?/\*OR_END\*/',lambda m:'const OR='+json.dumps(orbs)+';',src,flags=re.S)
# glass pills (webp)
glass={n[:-5]:uri(os.path.join(D,'img','glass',n),'image/webp') for n in sorted(os.listdir(os.path.join(D,'img','glass'))) if n.endswith('.webp')}
src=re.sub(r'/\*GL\*/.*?/\*GL_END\*/',lambda m:'const GL='+json.dumps(glass)+';',src,flags=re.S)
src = src.replace('--mxg:url(img/maxglass.png)', '--mxg:url(' + uri(os.path.join(D,'img','maxglass.png'),'image/png') + ')')
fg={n[:-4]:uri(os.path.join(D,'img','fg',n),'image/jpeg') for n in sorted(os.listdir(os.path.join(D,'img','fg'))) if n.endswith('.jpg')}
src=re.sub(r'/\*FG\*/.*?/\*FG_END\*/',lambda m:'const FG='+json.dumps(fg)+';',src,flags=re.S)
# css vars
src = src.replace('--orb:url(img/orb.webp)', '--orb:url(' + uri(os.path.join(D, 'img', 'orb.webp'), 'image/webp') + ')')
src = src.replace('--wmu:url(img/uh-wordmark.svg)', '--wmu:url(' + uri(os.path.join(D, 'img', 'uh-wordmark.svg'), 'image/svg+xml') + ')')

open(os.path.join(D, 'index.html'), 'w', encoding='utf-8').write(src)
print('index.html', round(len(src) / 1024), 'KB')

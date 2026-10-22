#!/usr/bin/env python3
"""lp.src.html + engine from agentic.html + index.src.html pieces -> lp.html"""
import json, os, re
D = os.path.dirname(os.path.abspath(__file__))
rd = lambda n: open(os.path.join(D, n), encoding='utf-8').read()
src, ag, ix = rd('lp.src.html'), rd('agentic.html'), rd('index.src.html')
L = ix.split('\n')

# ---- engine: V1 rays + V2 sand from agentic.html, V3 and the demo chrome removed
eng = ag[ag.index('<script>') + 8: ag.rindex('</script>')]
def cut(s, a, b, rep=''):
    i, j = s.index(a), s.index(b)
    return s[:i] + rep + s[j:]
eng = cut(eng, 'const F4=`', 'const P4=prog(F4);', '')
eng = eng.replace('const P4=prog(F4);\n', '')
eng = cut(eng, 'const maxTex=', 'const imgTex=', '')
eng = cut(eng, 'const CH=', 'const objTex=',
  "let ps=0;const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));const FX=[...document.querySelectorAll('[data-v]')];\n")
old = re.search(r"  const pr=Math\.min\(1,scrollY.*?\n", eng).group(0)
new = """  let best=null,bo=0,br=null;for(const e of FX){const r=e.getBoundingClientRect(),o=Math.min(r.bottom,innerHeight)-Math.max(r.top,0);if(o>bo){bo=o;best=e;br=r}}
  if(!best){cv.style.visibility='hidden';requestAnimationFrame(frame);return}
  cv.style.visibility='visible';{const nv=+best.dataset.v;if(nv!==VER)setVer(nv);const pr=clamp((innerHeight-br.top)/(innerHeight+br.height),0,1);ps+=(pr-ps)*(1-Math.pow(.002,dt))}
"""
eng = eng.replace(old, new)
# GLASSPATCH: V3 renders into an offscreen texture so the price can refract it
a1="  gl.bindFramebuffer(gl.FRAMEBUFFER,null);gl.viewport(0,0,cv.width,cv.height);bind(P2);"
assert a1 in eng
eng=eng.replace(a1,"  const GL3=VER===3&&typeof GLASS!=='undefined'&&GLASS.ensure();gl.bindFramebuffer(gl.FRAMEBUFFER,GL3?GLASS.fbo:null);gl.viewport(0,0,cv.width,cv.height);bind(P2);")
a2="gl.uniform1f(u2('uT'),t);gl.drawArrays(gl.TRIANGLES,0,3);\n  requestAnimationFrame(frame)}"
assert a2 in eng
eng=eng.replace(a2,"gl.uniform1f(u2('uT'),t);gl.drawArrays(gl.TRIANGLES,0,3);\n  if(typeof CARDSYNCX==='function')CARDSYNCX();\n  requestAnimationFrame(frame)}")
eng = re.sub(r"let VER=.*?;\n", "let VER=1;\n", eng, count=1)
eng = re.sub(r"document\.querySelectorAll\('#tg button'\)\.forEach\(b=>b\.onclick.*?\n", '', eng)
eng = re.sub(r"addEventListener\('keydown'.*?\n", '', eng)
eng = eng.replace("setVer(VER);\n", "setVer(VER);\n")

# ---- css/html pieces reused from the main page
css = lambda a, b: '\n'.join(L[a - 1:b])
src = src.replace('/*NAVCSS*/', css(26, 27))
src = src.replace('/*PRICECSS*/', css(124, 137))
src = src.replace('/*FAQCSS*/', css(140, 150))
src = src.replace('/*FOOTCSS*/', css(161, 184))
fa = next(i for i, l in enumerate(L) if l.startswith('<footer class="uf">'))
fb = next(i for i, l in enumerate(L) if l.startswith('</footer>'))
src = src.replace('/*FOOTER*/', '\n'.join(L[fa:fb + 1]))
faq = re.search(r"const FAQ=\[(.*?)\n\];", ix, re.S).group(1)
items = re.findall(r"\['((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)'\]", faq)
src = src.replace('/*FAQ*/', ''.join(f'<details{" open" if i==0 else ""}><summary>{q}<i></i></summary><p>{a}</p></details>' for i, (q, a) in enumerate(items)))
P = json.load(open(os.path.join(D, 'plugs.json'), encoding='utf-8'))
COPY = {
 'AFib Detection': 'Max screens your heart rhythm every night while you sleep. Powered by FibriCheck, it flags signs of AFib or atrial flutter, and a medical-grade report is ready each morning.',
 'Cycle & Ovulation Pro': 'With Max, your ring confirms ovulation from your own biometrics, with over 90% accuracy, using OvuSense technology. It also spots anovulatory cycles and cycle flags.',
 'Respiratory Health': 'Max tracks snoring, coughing and breathing disruptions every night, combining Sleep Cycle’s sound analysis with your ring’s HRV, heart rate and sleep data.',
 'HealthEx': 'Max puts your lab results, diagnoses and prescriptions next to your sleep, temperature, HRV and recovery, and explains each finding in plain language.',
 'Les Mills': 'Max matches your recovery to the right Les Mills workout each day, from 23 programs and 1,000+ classes, and logs heart-rate zones, calories and stats automatically.',
 'UltraSync for Tesla': 'With Max, every drive is linked to your ring data: your readiness before you set off, how your heart rate and HRV respond on the route, and which journeys strain you most.',
 'Migraine Insights': 'Max shows the 72 hours of ring data around each logged headache and finds patterns across HRV, sleep, recovery and cycle, paired with an 8-week programme built with Click Therapeutics.',
}
BUILTIN = {
 'Jade Pro': ('jade', 'Ask anything about your own data. With Max, Jade brings your ring, Blood Vision, glucose and Home signals into one system, so every answer is grounded in your full context.'),
 'UltrahumanX coverage': ('ux', 'Max covers your ring against damage, loss and theft, with express replacements, weight-loss resizing, trade-in value and priority support.'),
}
src = src.replace('/*CARDS*/', ''.join(
  f'<article class="cd"><img src="img/fg/{p["img"]}.jpg" alt="" loading="lazy" draggable="false"><div><h4>{p["n"]}</h4></div><div><p>{COPY[p["n"]]}</p></div></article>' for p in P if p['n'] in COPY))
src = src.replace('/*BUILTIN*/', ''.join(
  f'<article class="bc"><img src="img/fg/{im}.jpg" alt="" loading="lazy"><div><span class="mono">Included in Max</span><h4>{n}</h4><p>{t}</p></div></article>' for n, (im, t) in BUILTIN.items()))
src = src.replace('/*ENGINE*/', eng)
open(os.path.join(D, 'lp.html'), 'w', encoding='utf-8').write(src)
print('lp.html', round(len(src) / 1024), 'KB')

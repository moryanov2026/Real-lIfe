# Персона "Елена" в носия: бяла риза с шевици на маншетите, зелен сукман с черно бродирано деколте,
# черна престилка с цветни бродерии, черна ивица и бял подгъв с червени шевици, тъмна коса на две плитки.
# front(i) = отпред, front(i, True) = отзад, side(i) = надясно, dance(i) = хоро (8 кадъра).
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pix import *

M=lambda *a: tuple(hx(c) for c in a)
SKIN=M('#f8e0c8','#eec8a6','#d6a482','#aa7a5a')
HAIR=M('#6a4432','#4c2e22','#341e16','#20120c')
SHIRT=M('#ffffff','#f1ede4','#d8d0c0','#aaa292')
DRESS=M('#5ccc78','#34a856','#248440','#165a2a')
YOKE=M('#3a3842','#2a2830','#1e1c24','#121118')
APRON=M('#33303a','#24222a','#1a1820','#100f14')
TIGHT=M('#4a4650','#34313a','#25232a','#16151a')
SHOE=M('#3a3236','#2a2428','#1c181a','#100c0e')
RED=hx('#d8322e'); ORANGE=hx('#f08c2a'); GREEN=hx('#3cb050'); WHITE=hx('#f6f3ec'); YEL=hx('#f2c230')
OUT=hx('#1e1410'); EYE=hx('#2a1d16'); LIPS=hx('#c84a48'); BLUSH=hx('#f0a090')

def rot(p,ang,L):
    a=math.radians(ang); return (p[0]+L*math.sin(a), p[1]+L*math.cos(a))

def облечи(px):
    """Бродериите: цветни ромбчета на престилката, цветя на деколтето, маншети, подгъв."""
    H,W=len(px),len(px[0])
    престилка=тонове(APRON); деколте=тонове(YOKE); рокля=тонове(DRESS); ръкав=тонове(SHIRT); кожа=тонове(SKIN)
    нов=[ред[:] for ред in px]
    горе_престилка=min([y for y in range(H) for x in range(W) if px[y][x] in престилка] or [0])
    цветове=[RED,ORANGE,GREEN,WHITE]
    for y in range(H):
        for x in range(W):
            ц=px[y][x]
            if ц in престилка:
                съседи=[px[y][x-1] if x>0 else None, px[y][x+1] if x<W-1 else None, px[y+1][x] if y<H-1 else None]
                if any(с not in престилка and с not in ръкав for с in съседи):
                    нов[y][x]=WHITE if y%2 else hx('#d8d2c6')                   # бял ръб
                else:
                    cx,cy=x%4,(y-горе_престилка)%4
                    ред=(y-горе_престилка)//4
                    if (cx,cy) in ((1,0),(0,1),(2,1),(1,2)):
                        нов[y][x]=цветове[ред%4]                                 # ромбче от бродерия
                    elif (cx,cy)==(1,1):
                        нов[y][x]=WHITE if ред%2 else YEL
            elif ц in деколте:
                if (x+2*y)%5==0: нов[y][x]=RED
                elif (x+2*y)%5==2: нов[y][x]=GREEN
                elif (x*3+y)%7==0: нов[y][x]=WHITE
            elif ц in ръкав and y>22:
                if any(0<=y+dy<H and 0<=x+dx<W and px[y+dy][x+dx] in кожа for dx,dy in ((0,1),(1,0),(-1,0),(0,2),(1,1),(-1,1))):
                    нов[y][x]=RED if x%2 else GREEN                              # шевица на маншета
    for x in range(W):                                    # подгъв: черна ивица и бяла фуста с червени шевици
        долу=[y for y in range(H) if px[y][x] in рокля]
        if not долу: continue
        b=max(долу)
        if b>40:
            нов[b][x]=WHITE if x%3 else RED
            for yy in (b-1,b-2):
                if px[yy][x] in рокля: нов[yy][x]=YOKE[1]
    return нов

def лице(cv,hc,усмивка=False):
    ey=int(hc[1]+0.5)
    for ex in (29,34):
        if усмивка:
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,EYE,9,997)
        else:
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,hx('#6a4a3a'),9,997)
            cv.plot(ex,ey-1,EYE,9,996); cv.plot(ex+1,ey-1,EYE,9,996)          # мигли
        cv.plot(ex,ey-3,HAIR[2],9,993); cv.plot(ex+1,ey-3,HAIR[2],9,993)
    cv.plot(31,ey+2,SKIN[2],9,996)                                            # нос
    cv.plot(31,ey+4,LIPS,9,995); cv.plot(32,ey+4,LIPS,9,995)
    if усмивка: cv.plot(30,ey+3,LIPS,9,995); cv.plot(33,ey+3,LIPS,9,995)
    cv.plot(28,ey+2,BLUSH,9,994); cv.plot(35,ey+2,BLUSH,9,994)

def глава(cv,hc,back=False,усмивка=False):
    ellipse(cv,hc[0],hc[1],6.2,6.9,SKIN,6)
    if back:
        ellipse(cv,hc[0],hc[1]-0.8,6.8,6.8,HAIR,6.5)
        for y in range(int(hc[1]-6),int(hc[1]+5)): cv.plot(int(hc[0]),y,HAIR[2],9,990)
        for s in (-1,1):                                   # две плитки по гърба
            плитка(cv,(hc[0]+s*3,hc[1]+5),(hc[0]+s*4,hc[1]+19),6.7)
        return
    # коса с път по средата, прибрана зад ушите
    ellipse(cv,hc[0],hc[1]-1.2,6.7,6.4,HAIR,6.5,mask=lambda x,y:(y<hc[1]-3.0) or ((x<hc[0]-5.3 or x>hc[0]+4.8) and y<hc[1]+2))
    for y in range(int(hc[1]-7),int(hc[1]-3)): cv.plot(31,y,HAIR[2],9,990)
    for s in (-1,1):                                       # плитките отпред през раменете
        плитка(cv,(hc[0]+s*5.5,hc[1]+2),(hc[0]+s*6.5,hc[1]+17),6.8)
    cv.plot(int(hc[0]-6.5),int(hc[1]+3),YEL,9,989); cv.plot(int(hc[0]+6),int(hc[1]+3),YEL,9,989)   # обеци
    лице(cv,hc,усмивка)

def плитка(cv,a,b,z):
    capsule(cv,a,b,1.7,1.3,HAIR,z)
    n=int(abs(b[1]-a[1]))
    for k in range(0,n,2):                                 # сплитането: тъмни черти
        x=a[0]+(b[0]-a[0])*k/n; y=a[1]+(b[1]-a[1])*k/n
        cv.plot(int(x),int(y),HAIR[3],z+0.1,988)
    cv.plot(int(b[0]),int(b[1]+1),RED,z+0.2,987)             # червена панделка на края

def ръце_отпред(cv,by,t,back,хоро=False):
    for s in (-1,1):
        if хоро:
            вълна=0.8*math.sin(t+(0 if s>0 else math.pi))
            sh=(32+s*6.6,26+by); el=(32+s*11,28.5+by); hd=(32+s*15.5,29.5+by+вълна)
        else:
            sway=1.2*math.sin(t+(0 if s>0 else math.pi))
            sh=(32+s*6.6,26+by); el=(32+s*8.2,32+by); hd=(32+s*8.6,38.5+by+sway)
        capsule(cv,sh,el,2.3,2.1,SHIRT,6.2)
        capsule(cv,el,hd,2.1,1.9,SHIRT,6.2)
        ellipse(cv,hd[0],hd[1]+1.3,1.7,1.7,SKIN,6.4,extra=-0.1)

def рокля_отпред(cv,by,sw,back):
    w0=34+by; w1=52+by
    poly(cv,[(26,w0),(38,w0),(41+sw,w1-1),(40+sw,w1),(24+sw,w1),(23+sw,w1-1)],DRESS,4,
         folds=((lambda y:28-0.15*(y-w0)+sw*(y-w0)/18,0.45),(lambda y:36+0.15*(y-w0)+sw*(y-w0)/18,0.45)))
    capsule(cv,(32,27+by),(32,34+by),6.2,5.8,DRESS,5)
    if not back:
        ellipse(cv,32,24.5+by,7.2,4.6,YOKE,5.3,mask=lambda x,y:y<28.5+by)          # черно бродирано деколте
        poly(cv,[(30,23.5+by),(34,23.5+by),(32,27+by)],SHIRT,5.6)                  # бялата риза в деколтето
        cv.plot(31,int(24+by),RED,9,986); cv.plot(32,int(25+by),RED,9,986)
        poly(cv,[(27,w0+0.5),(37,w0+0.5),(38.5+sw,w1-2),(25.5+sw,w1-2)],APRON,5.2)  # бродираната престилка
        for x in range(26,39): cv.plot(x,int(w0),YOKE[2],9,985)                    # връв на престилката
    else:
        ellipse(cv,32,24.5+by,7.2,3.6,YOKE,5.3,mask=lambda x,y:y<27+by)
        for (x,y) in ((30,0),(31,1),(33,1),(34,0),(31,3),(33,3),(32,5)):            # връзките на престилката
            cv.plot(x,int(w0+y),YOKE[2],9,985)

def крака(cv,by,лифт):
    for k,x in enumerate((29.5,34.5)):
        ay=59.0-лифт[k]
        capsule(cv,(x,47+by),(x,ay),2.1,1.8,TIGHT,2,extra=(-0.15 if k else 0))
        ellipse(cv,x+(-0.3 if k==0 else 0.3),ay+1.6,2.5,1.6,SHOE,2.2)

def front(i, back=False):
    t=2*math.pi*i/8
    cv=Canvas()
    by=round(0.5*(1+math.cos(2*t)))
    крака(cv,by,[max(0,math.sin(t))*2.5, max(0,math.sin(t+math.pi))*2.5])
    рокля_отпред(cv,by,0.8*math.sin(t),back)
    ръце_отпред(cv,by,t,back)
    глава(cv,(32,16+by),back)
    return облечи(finish(cv,OUT))

def dance(i):
    t=2*math.pi*i/8
    cv=Canvas()
    вдигане=[0,2,4,2,0,0,0,0]
    by=[1,0,0,0,1,0,0,0][i]
    крака(cv,by,[вдигане[i], вдигане[(i+4)%8]])
    рокля_отпред(cv,by,1.6*math.sin(t),False)
    ръце_отпред(cv,by,t,False,хоро=True)
    глава(cv,(32,16+by),усмивка=True)
    return облечи(finish(cv,OUT))

def side(i):
    t=2*math.pi*i/8
    cv=Canvas()
    TH,SH=9.0,9.5
    def leg(ph):
        th=18*math.sin(ph); knee=max(0,36*math.sin(ph-1.3)); return th, th-knee
    legs=[leg(t+math.pi), leg(t)]
    ank=[TH*math.cos(math.radians(a))+SH*math.cos(math.radians(b)) for a,b in legs]
    hipY=59.0-max(ank); by=hipY-41.5; hip=(31.5,hipY)
    def arm(sh,z,ex,sgn):
        fa=-15*math.sin(t)*sgn
        el=rot(sh,fa,6.2); hd=rot(el,fa+12,6.0)
        capsule(cv,sh,el,2.2,2.0,SHIRT,z,extra=ex)
        capsule(cv,el,hd,2.0,1.8,SHIRT,z,extra=ex)
        ellipse(cv,hd[0],hd[1]+1.2,1.7,1.7,SKIN,z+0.1,extra=ex)
    arm((31,26+by),1,-0.35,1)
    for k,(a,b) in enumerate(legs):
        z=2 if k==0 else 3; ex=-0.35 if k==0 else 0
        knee=rot(hip,a,TH); ankle=rot(knee,b,SH)
        capsule(cv,hip,knee,2.4,2.1,TIGHT,z,extra=ex)
        capsule(cv,knee,ankle,2.1,1.7,TIGHT,z,extra=ex)
        lift=max(0,math.sin(t+(0 if k else math.pi)-1.2))*1.5
        ellipse(cv,ankle[0]+2.0,ankle[1]+1.0-lift*0.5,3.0,1.6,SHOE,z+0.2,extra=ex-0.1)
    sw=1.4*math.sin(t)
    w0=34+by; w1=52+by
    poly(cv,[(25.5,w0),(37,w0),(40+sw,w1-1),(39+sw,w1),(23.5+sw,w1),(23+sw,w1-1)],DRESS,4,
         folds=((lambda y:28+sw*(y-w0)/18,0.45),))
    capsule(cv,(31,27+by),(31.5,34+by),5.6,5.4,DRESS,5)
    ellipse(cv,31.5,24.5+by,6.0,4.0,YOKE,5.3,mask=lambda x,y:y<28.5+by)
    poly(cv,[(34,w0+0.5),(37.5,w0+0.5),(40.5+sw,w1-2),(35+sw,w1-2)],APRON,5.2)
    hc=(33.5,16+by)
    capsule(cv,(32,23+by),(33,21+by),2.0,2.0,SKIN,5.6,extra=-0.2)
    ellipse(cv,hc[0],hc[1],6.0,6.8,SKIN,6)
    ellipse(cv,hc[0]-1.0,hc[1]-1.6,6.4,6.2,HAIR,6.5,mask=lambda x,y:(y<hc[1]-3.0) or (x<hc[0]-1.5 and y<hc[1]+3))
    плитка(cv,(hc[0]-3,hc[1]+3),(hc[0]-4.5,hc[1]+17),6.6)                       # плитката по гърба
    ey=int(hc[1]+0.5); ex=int(hc[0]+3)
    cv.plot(ex,ey,EYE,9,997); cv.plot(ex,ey-1,EYE,9,996); cv.plot(ex,ey-3,HAIR[2],9,993); cv.plot(ex+1,ey-3,HAIR[2],9,993)
    cv.plot(int(hc[0]+6),ey+1,SKIN[1],9,996); cv.plot(int(hc[0]+6),ey+2,SKIN[2],9,996)
    cv.plot(ex+1,ey+4,LIPS,9,995); cv.plot(ex+2,ey+4,LIPS,9,995)
    cv.plot(int(hc[0]-1),ey+1,SKIN[2],9,994); cv.plot(int(hc[0]-1),ey+3,YEL,9,989)   # ухо и обеца
    arm((32,26+by),7,0,-1)
    return облечи(finish(cv,OUT))

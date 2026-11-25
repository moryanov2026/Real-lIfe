# Персона "баба Стана": рисува се от части с обем (виж pix.py).
# side(i) = кадър i (0-7) отстрани, front(i) = отпред, front(i, True) = отзад.
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # pix.py е в същата папка
from pix import *

M=lambda *a: tuple(hx(c) for c in a)
SKIN=M('#f7dcc0','#f2c7a0','#d9a07a','#a8705a')
HAIR=M('#ffffff','#eeebe4','#c9c3b8','#948e86')
CARD=M('#93608a','#6e4062','#55304b','#3a2034')
SKIRT=M('#575173','#3e3856','#2e2943','#1f1b2e')
APRON=M('#e06a55','#c4463a','#9a352d','#6e2320')
STOCK=M('#b0a090','#8e7e6e','#6c5e52','#4a4038')
SHOE=M('#5a4636','#433226','#33251c','#221710')
CANE=M('#d09a5c','#ad7440','#87552e','#5e3a1e')
OUT=hx('#1e1410'); FRAME=hx('#6e4a30'); MOUTH=hx('#8c4a3e'); LENS=hx('#d6ecf4'); GLASS=hx('#8fb4c8'); BLUSH=hx('#e8907a'); EYE=hx('#2a1d16')

def rot(p,ang,L):
    a=math.radians(ang); return (p[0]+L*math.sin(a), p[1]+L*math.cos(a))

def side(i, cane_near=True):
    """cane_near=True: бастунът е в близката ръка (за посока наляво след огледало),
    False: в далечната ръка (посока надясно). Така бастунът е винаги в дясната ѝ ръка."""
    t=2*math.pi*i/8
    cv=Canvas()
    TH,SH=9.0,10.0
    def leg(ph):
        th=19*math.sin(ph)                       # бедро напред/назад
        knee=max(0,38*math.sin(ph-1.3))          # сгъване в коляното при пренасяне
        return th, th-knee
    legs=[leg(t+math.pi), leg(t)]                 # заден, преден
    ank=[TH*math.cos(math.radians(a))+SH*math.cos(math.radians(b)) for a,b in legs]
    hipY=59.5-max(ank)                            # най-ниското стъпало стои на земята
    by=hipY-40.5
    hip=(30.5,hipY)
    def cane_arm(sh,z,ex):
        hand=(41.5+1.2*math.sin(t+math.pi),37.5+by)
        elb=((sh[0]+hand[0])/2+0.5,(sh[1]+hand[1])/2+2)
        capsule(cv,sh,elb,2.4,2.1,CARD,z,extra=ex)
        capsule(cv,elb,hand,2.0,1.7,CARD,z,extra=ex)
        tip=(hand[0]+1.5+2.5*math.sin(t+math.pi),61.5)
        capsule(cv,(hand[0]+0.5,hand[1]-1),tip,1.0,1.0,CANE,z+0.5)
        capsule(cv,(hand[0]-2,hand[1]-2.5),(hand[0]+1,hand[1]-2.8),1.0,1.0,CANE,z+0.6)
        ellipse(cv,hand[0]+0.5,hand[1],2.0,2.0,SKIN,z+1,extra=ex)
    def swing_arm(sh,z,ex,sgn):
        fa=-14*math.sin(t)*sgn
        el=rot(sh,fa,6); hd=rot(el,fa+20,6)
        capsule(cv,sh,el,2.2,2.0,CARD,z,extra=ex)
        capsule(cv,el,hd,1.9,1.6,CARD,z,extra=ex)
        ellipse(cv,hd[0],hd[1]+1,1.8,1.8,SKIN,z+0.1,extra=ex+0.05)
    # --- далечна ръка (зад тялото)
    sh_far=(30,27+by)
    if cane_near: swing_arm(sh_far,1,-0.35,1)
    else:         cane_arm((31,27+by),0.5,-0.3)
    # --- крака
    for k,(a,b) in enumerate(legs):
        z=2 if k==0 else 3; ex=-0.35 if k==0 else 0
        knee=rot(hip,a,TH); ankle=rot(knee,b,SH)
        capsule(cv,(hip[0]+(k*2-1),hip[1]),knee,2.6,2.2,STOCK,z,extra=ex)
        capsule(cv,knee,ankle,2.2,1.7,STOCK,z,extra=ex)
        lift=max(0,math.sin(t+(0 if k else math.pi)-1.2))*1.5
        ellipse(cv,ankle[0]+2.2,ankle[1]+1.2-lift*0.5,3.4,1.7,SHOE,z+0.2,extra=ex-0.1)
    # --- пола (покрива бедрата), подгъвът се люлее
    sw=1.6*math.sin(t)
    w0=36+by; w1=51+by
    skirt=[(23,w0),(38,w0),(42+sw,w1-1),(41+sw,w1),(21+sw,w1),(20.5+sw,w1-1)]
    folds=((lambda y:27+0.15*(y-w0)+sw*(y-w0)/15,0.45),(lambda y:33+0.25*(y-w0)+sw*(y-w0)/15,0.45))
    poly(cv,skirt,SKIRT,4,folds=folds)
    # престилка отпред
    ap=[(34,w0+1),(38.5,w0+1),(42+sw,w1-2),(36.5+sw,w1-2)]
    poly(cv,ap,APRON,4.5,extra=0.1)
    # --- торс (прегърбен) и гърбица
    capsule(cv,(29.5,30+by),(31,36+by),6.4,6.6,CARD,5)
    ellipse(cv,28.2,29.6+by,3.5,3.8,CARD,5.1)
    for yy in range(int(28+by),int(37+by)):              # копчета по ръба
        pass
    # --- врат и глава
    hc=(36.5,18.5+by)
    capsule(cv,(33.5,26+by),(35,24+by),2.2,2.2,SKIN,5.5,extra=-0.2)
    ellipse(cv,hc[0],hc[1],7.2,7.6,SKIN,6)
    # коса: отгоре и отзад
    ellipse(cv,hc[0]-0.8,hc[1]-1.0,7.4,7.2,HAIR,6.5,mask=lambda x,y:(y<hc[1]-3) or (x<hc[0]-2 and y<hc[1]+4))
    ellipse(cv,hc[0]-8.0,hc[1]-4.5,3.6,3.4,HAIR,6.4)      # кок
    # --- близка ръка
    sh=(33,28+by)
    if cane_near: cane_arm(sh,7,0)
    else:         swing_arm(sh,7,0,-1)
    # --- лице
    cv.plot(int(hc[0]+7),int(hc[1]+0.5),SKIN[1],9,999)      # нос
    cv.plot(int(hc[0]+7),int(hc[1]+1.5),SKIN[2],9,999)
    ex,ey=int(hc[0]+3.5),int(hc[1]-0.5)
    for (x,y) in [(ex-1,ey),(ex,ey-1),(ex+1,ey-1),(ex+2,ey),(ex+1,ey+1),(ex,ey+1)]:
        cv.plot(x,y,FRAME,9,998)
    cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,LENS,9,997)
    for x in range(ex-5,ex-1): cv.plot(x,ey,FRAME,9,998)          # дръжка на очилата
    cv.plot(ex,ey-3,HAIR[3],9,993); cv.plot(ex+1,ey-3,HAIR[3],9,993)  # вежда
    cv.plot(ex+2,ey+2,SKIN[2],9,993)                                  # бръчка до окото
    cv.plot(ex,ey+3,BLUSH,9,996); cv.plot(ex+1,ey+3,BLUSH,9,996)
    cv.plot(ex+2,ey+5,MOUTH,9,995); cv.plot(ex+3,ey+5,MOUTH,9,995)    # уста
    cv.plot(ex+1,ey+4,SKIN[2],9,994)                                  # бръчка до устата
    cv.plot(int(hc[0]-1),int(hc[1]+1),SKIN[2],9,994)        # ухо
    cv.plot(int(hc[0]-1),int(hc[1]+2),SKIN[3],9,994)
    return finish(cv,OUT)

def front(i, back=False):
    t=2*math.pi*i/8
    cv=Canvas()
    by=round(0.5*(1+math.cos(2*t)))            # най-ниско при стъпване
    lift=[max(0,math.sin(t))*2.5, max(0,math.sin(t+math.pi))*2.5]
    # --- крака
    for k,x in enumerate((28.5,35.5)):
        ay=59.0-lift[k]
        capsule(cv,(x,46+by),(x,ay),2.4,1.9,STOCK,2,extra=(-0.15 if k else 0))
        ellipse(cv,x+(-0.3 if k==0 else 0.3),ay+1.6,2.7,1.8,SHOE,2.2)
    # --- пола
    sw=0.8*math.sin(t)
    w0=36+by; w1=51+by
    skirt=[(25,w0),(39,w0),(42.5+sw,w1-1),(41.5+sw,w1),(22.5+sw,w1),(21.5+sw,w1-1)]
    folds=((lambda y:27-0.18*(y-w0)+sw*(y-w0)/15,0.5),(lambda y:32+sw*(y-w0)/15,0.35),(lambda y:37+0.18*(y-w0)+sw*(y-w0)/15,0.5))
    poly(cv,skirt,SKIRT,4,folds=folds)
    if not back:
        poly(cv,[(28,w0+1),(36,w0+1),(37.5+sw,w1-2),(26.5+sw,w1-2)],APRON,4.5,extra=0.1,
             folds=((lambda y:32+sw*(y-w0)/15,0.4),))
    # --- торс
    capsule(cv,(32,29.5+by),(32,36+by),7.6,8.0,CARD,5)
    if back:
        # панделка на престилката отзад
        ellipse(cv,32,37+by,2.2,1.6,APRON,5.6); ellipse(cv,29,37+by,2.4,1.5,APRON,5.5); ellipse(cv,35,37+by,2.4,1.5,APRON,5.5)
        capsule(cv,(31,38+by),(29.5,42+by),0.9,0.9,APRON,5.5); capsule(cv,(33,38+by),(34.5,42+by),0.9,0.9,APRON,5.5)
        capsule(cv,(24,37+by),(40,37+by),0.7,0.7,APRON,5.4)
    # --- ръце: бастунът е в дясната ѝ ръка (отпред: вляво на екрана, отзад: вдясно)
    cane_side=1 if back else -1
    for side_ in (-1,1):
        sh=(32+side_*7.2,28.5+by)
        if side_==cane_side:
            hand=(32+side_*12.5,38+by)
            el=(32+side_*10.5,33.5+by)
        else:
            sway=1.2*math.sin(t+math.pi)
            el=(32+side_*8.6,34+by); hand=(32+side_*8.8,40+by+sway)
        z=6 if not back else 6
        capsule(cv,sh,el,2.5,2.2,CARD,z,extra=0.05*side_*(-1))
        capsule(cv,el,hand,2.1,1.8,CARD,z)
        if side_==cane_side:
            tipx=hand[0]+1.0*math.sin(t)
            zc=6.5 if not back else 3
            capsule(cv,(hand[0],hand[1]-3.5),(tipx,61.5),1.0,1.0,CANE,zc)
            # дръжка-кука над ръката, извита към тялото
            capsule(cv,(hand[0],hand[1]-3.8),(hand[0]-2.6*side_,hand[1]-3.8),1.0,1.0,CANE,7.0 if not back else 6.9)
            capsule(cv,(hand[0]-2.6*side_,hand[1]-3.8),(hand[0]-2.8*side_,hand[1]-2.2),0.9,0.9,CANE,7.0 if not back else 6.9)
        ellipse(cv,hand[0],hand[1]+0.6,1.9,1.9,SKIN,6.8,extra=-0.1)
    # --- глава
    hc=(32,18.5+by)
    if not back:
        poly(cv,[(29.5,25.5+by),(34.5,25.5+by),(32,28.5+by)],SKIN,5.8,extra=-0.2)   # шия/деколте
        ellipse(cv,hc[0],hc[1],7.3,7.6,SKIN,6)
        # коса, прибрана назад: открито чело, бухнала над слепоочията
        ellipse(cv,hc[0],hc[1]-0.8,7.7,7.4,HAIR,6.5,mask=lambda x,y:(y<hc[1]-3.5) or ((x<hc[0]-5.5 or x>hc[0]+4.5) and y<hc[1]+1))
        ellipse(cv,hc[0],hc[1]-8.6,4.6,3.2,HAIR,6.4,extra=0.15)    # кокът се подава отгоре
        for y in range(int(hc[1]-7),int(hc[1]-4)): cv.plot(31,y,HAIR[2],9,990)   # път по средата
        cv.plot(27,int(hc[1]-5),HAIR[2],9,990); cv.plot(36,int(hc[1]-5),HAIR[2],9,990)  # кичури
        ey=int(hc[1]+0.5)
        for ex in (28,34):
            for (x,y) in [(ex-1,ey),(ex,ey-1),(ex+1,ey-1),(ex+2,ey),(ex+1,ey+1),(ex,ey+1)]: cv.plot(x,y,FRAME,9,998)
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,LENS,9,997)
            cv.plot(ex,ey-3,HAIR[3],9,993); cv.plot(ex+1,ey-3,HAIR[3],9,993)
        cv.plot(31,ey,FRAME,9,998); cv.plot(32,ey,FRAME,9,998)
        cv.plot(31,ey+2,SKIN[2],9,996); cv.plot(32,ey+2,SKIN[2],9,996)     # нос
        for x in (30,31,32,33): cv.plot(x,ey+5,MOUTH,9,995)                # уста
        cv.plot(29,ey+4,SKIN[2],9,995); cv.plot(34,ey+4,SKIN[2],9,995)     # бръчки до устата
        cv.plot(27,ey+3,BLUSH,9,994); cv.plot(36,ey+3,BLUSH,9,994)
        cv.plot(31,int(31+by),CARD[0],9,992); cv.plot(31,int(34+by),CARD[0],9,992)   # копчета
    else:
        ellipse(cv,hc[0],hc[1],7.3,7.6,SKIN,6)
        ellipse(cv,hc[0],hc[1]-0.5,7.6,7.6,HAIR,6.5,mask=lambda x,y:y<hc[1]+5)
        # кичури, сресани надолу към кока на тила
        for (x0,x1) in ((hc[0]-5,hc[0]-2.5),(hc[0]+4,hc[0]+1.5),(hc[0]-1,hc[0]-0.5)):
            for k in range(4):
                y=hc[1]-6+k*1.6
                cv.plot(int(x0+(x1-x0)*k/3),int(y),HAIR[2],9,990)
        ellipse(cv,hc[0]-0.3,hc[1]+1.6,3.6,2.9,HAIR,7.2,extra=0.35,pid=951)  # кок на тила (без контур)
        for x in range(int(hc[0]-3),int(hc[0]+3)):                          # сянка под кока
            cv.plot(x,int(hc[1]+4.6),HAIR[3],9,989)
        cv.plot(int(hc[0]-4),int(hc[1]+3.6),HAIR[3],9,989); cv.plot(int(hc[0]+3),int(hc[1]+3.6),HAIR[3],9,989)
        cv.plot(int(hc[0]-1),int(hc[1]+0.5),HAIR[2],9,989); cv.plot(int(hc[0]),int(hc[1]+1.5),HAIR[2],9,989)  # навиване
    return finish(cv,OUT)

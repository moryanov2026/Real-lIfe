# Персона "Стоян" - музикантът: бяла риза с шевици, черен елек с гайтани, червен пояс,
# кафяви потури, черен калпак, мустаци, кавал, затъкнат в пояса.
# front(i) = отпред, front(i, True) = отзад, side(i, kaval_near) = надясно, play(i) = свири (2 кадъра).
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pix import *

M=lambda *a: tuple(hx(c) for c in a)
SKIN=M('#f4d2b0','#e8b78e','#cc916a','#9a6448')
HAIR=M('#5a4030','#402c20','#2c1e16','#1a120c')
KALP=M('#5a5254','#3c3638','#2a2628','#161314')
SHIRT=M('#fffbf2','#efe7d6','#d4c8b0','#a89c84')
VEST=M('#4c4450','#36303c','#282330','#19151f')
SASH=M('#ec5a44','#c8382c','#982822','#6a1a16')
PANT=M('#86684e','#6a523e','#4e3c2e','#33271e')
SHOE=M('#6a5038','#4c3828','#36281c','#221810')
KAV=M('#d49a62','#b07440','#8a5530','#5e351c')
BONE=hx('#efe4c8')
OUT=hx('#1e1410'); EYE=hx('#2a1d16'); RED=hx('#c8302a'); MOUTH=hx('#8c4a3e'); GOLD=hx('#d8a838')

def rot(p,ang,L):
    a=math.radians(ang); return (p[0]+L*math.sin(a), p[1]+L*math.cos(a))

def kaval(cv,p0,p1,z,pid=None):
    """Кавалът: тънка кафява пръчка с костени пръстени."""
    capsule(cv,p0,p1,1.2,1.3,KAV,z,pid=pid)
    for k in (0.0,0.33,0.7):
        x=p0[0]+(p1[0]-p0[0])*k; y=p0[1]+(p1[1]-p0[1])*k
        cv.plot(int(x),int(y),BONE,z+0.5,996)

def head_front(cv,hc,back=False,eyes_closed=False):
    ellipse(cv,hc[0],hc[1],6.6,7.2,SKIN,6)
    # калпак: висок, с плосък връх
    капа=ellipse(cv,hc[0],hc[1]-6.2,7.0,5.6,KALP,6.6,mask=lambda x,y:y<hc[1]-2.2)
    for (dx,dy) in ((-4,-9),(-1,-10),(2,-9),(4,-7),(-3,-6),(1,-7)):        # козина
        cv.plot(int(hc[0]+dx),int(hc[1]+dy),KALP[0],9,980)
    if back:
        ellipse(cv,hc[0],hc[1]+0.5,6.8,5.5,HAIR,6.5,mask=lambda x,y:y<hc[1]+4 and y>=hc[1]-3)
        return
    ey=int(hc[1]+0.5)
    for sx in (-6,6):                                                     # бакенбарди
        for y in range(ey-2,ey+2): cv.plot(int(hc[0]+sx-(1 if sx>0 else 0)),y,HAIR[2],9,990)
    for ex in (29,34):
        if eyes_closed:
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,EYE,9,997)
        else:
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,hx('#fbf4e2'),9,997)
        cv.plot(ex,ey-2,HAIR[2],9,993); cv.plot(ex+1,ey-2,HAIR[2],9,993)  # вежди
    cv.plot(31,ey+1,SKIN[2],9,996); cv.plot(32,ey+2,SKIN[2],9,996)         # нос
    for x in range(29,36): cv.plot(x,ey+3,HAIR[3],9,995)                   # мустак
    cv.plot(28,ey+4,HAIR[3],9,995); cv.plot(35,ey+4,HAIR[3],9,995)
    cv.plot(31,ey+5,MOUTH,9,994); cv.plot(32,ey+5,MOUTH,9,994)
    cv.plot(28,ey+2,hx('#e89a80'),9,993); cv.plot(36,ey+2,hx('#e89a80'),9,993)

def body_front(cv,by,back,t,arms=True,kaval_tucked=True):
    # торс: риза
    capsule(cv,(32,27+by),(32,37+by),7.4,7.0,SHIRT,5)
    if not back:
        # елекът: две страни, ризата се вижда в средата
        poly(cv,[(24.5,24+by),(30,24+by),(30.5,40+by),(24.5,40+by)],VEST,5.5,extra=0.05)
        poly(cv,[(33.5,24+by),(39.5,24+by),(39.5,40+by),(33.5,40+by)],VEST,5.5,extra=-0.05)
        for y in range(int(25+by),int(40+by)):                              # гайтани (червени шнурове)
            cv.plot(30,y,RED,9,985); cv.plot(33,y,RED,9,985)
        for y in (29,33,37): cv.plot(31,int(y+by),GOLD,9,984); cv.plot(32,int(y+by),GOLD,9,984)
        for x in (30,31,32,33): cv.plot(x,int(24+by),SHIRT[0],9,986)        # яката
        cv.plot(31,int(25+by),RED,9,986); cv.plot(32,int(25+by),RED,9,986) # шевица на яката
    else:
        poly(cv,[(24.5,24+by),(39.5,24+by),(39.5,40+by),(24.5,40+by)],VEST,5.5)
        for x in range(26,39,3): cv.plot(x,int(27+by),RED,9,985)            # шевица на гърба
    # пояс
    poly(cv,[(24,39+by),(40,39+by),(40,43+by),(24,43+by)],SASH,6,folds=((lambda y:28,0.3),(lambda y:35,0.3)))
    if not back:
        capsule(cv,(38.5,43+by),(39.5,47+by),0.9,0.9,SASH,6.1)            # краят на пояса виси
    if kaval_tucked:
        if not back: kaval(cv,(37,49+by),(42,29+by),6.2)
        else:        kaval(cv,(27,49+by),(22,29+by),3)
    if arms:
        for s in (-1,1):
            sway=1.3*math.sin(t+(0 if s>0 else math.pi))
            sh=(32+s*7.6,27+by); el=(32+s*9.4,33+by); hd=(32+s*9.6,39.5+by+sway)
            capsule(cv,sh,el,2.6,2.3,SHIRT,6.5)
            capsule(cv,el,hd,2.3,2.0,SHIRT,6.5)
            cv.plot(int(hd[0]),int(hd[1]-1.5),RED,9,983)                        # шевица на ръкава
            ellipse(cv,hd[0],hd[1]+1.3,1.9,1.9,SKIN,6.8,extra=-0.1)

def legs_front(cv,by,t):
    lift=[max(0,math.sin(t))*2.5, max(0,math.sin(t+math.pi))*2.5]
    for k,x in enumerate((29,35)):
        ay=58.5-lift[k]
        capsule(cv,(x,42+by),(x,ay-1),2.9,2.4,PANT,2,extra=(-0.12 if k else 0))
        ellipse(cv,x+(-0.3 if k==0 else 0.3),ay+1.2,2.8,1.8,SHOE,2.2)

def front(i, back=False):
    t=2*math.pi*i/8
    cv=Canvas()
    by=round(0.5*(1+math.cos(2*t)))
    legs_front(cv,by,t)
    body_front(cv,by,back,t)
    head_front(cv,(32,15.5+by),back)
    return finish(cv,OUT)

def play(i):
    """Свири на кавала, отпред. Кавалът е косо надолу вляво, двете ръце върху него."""
    cv=Canvas()
    by=1 if i==1 else 0                       # леко клати глава в такта
    legs_front(cv,0,0)
    body_front(cv,0,False,0,arms=False,kaval_tucked=False)
    hc=(32,15.5+by)
    уста=(31.5,20.5+by)
    край=(15.5,47.0-(1 if i==1 else 0))
    горна=(уста[0]+(край[0]-уста[0])*0.36, уста[1]+(край[1]-уста[1])*0.36)
    долна=(уста[0]+(край[0]-уста[0])*0.66, уста[1]+(край[1]-уста[1])*0.66)
    # ръцете: дясната (горе) и лявата (долу) пресичат тялото
    capsule(cv,(24.4,27),(22.5,31.5),2.6,2.3,SHIRT,6.5)
    capsule(cv,(22.5,31.5),горна,2.3,2.0,SHIRT,6.5)
    capsule(cv,(39.6,27),(37,36),2.6,2.3,SHIRT,6.4)
    capsule(cv,(37,36),долна,2.3,2.0,SHIRT,6.4)
    kaval(cv,уста,край,7)
    for р,пръсти in ((горна,i),(долна,1-i)):
        ellipse(cv,р[0],р[1],2.0,1.8,SKIN,7.6,extra=-0.05)
        cv.plot(int(р[0]+1+пръсти),int(р[1]+1),SKIN[2],9,982)                 # пръстите се местят
    head_front(cv,hc,eyes_closed=(i==1))
    return finish(cv,OUT)

def side(i, kaval_near=True):
    t=2*math.pi*i/8
    cv=Canvas()
    TH,SH=9.5,9.5
    def leg(ph):
        th=22*math.sin(ph)
        knee=max(0,40*math.sin(ph-1.3))
        return th, th-knee
    legs=[leg(t+math.pi), leg(t)]
    ank=[TH*math.cos(math.radians(a))+SH*math.cos(math.radians(b)) for a,b in legs]
    hipY=59.0-max(ank)
    by=hipY-41.5
    hip=(31.5,hipY)
    # далечна ръка
    def arm(sh,z,ex,sgn):
        fa=-18*math.sin(t)*sgn
        el=rot(sh,fa,6.5); hd=rot(el,fa+15,6.2)
        capsule(cv,sh,el,2.4,2.2,SHIRT,z,extra=ex)
        capsule(cv,el,hd,2.1,1.9,SHIRT,z,extra=ex)
        ellipse(cv,hd[0],hd[1]+1.2,1.9,1.9,SKIN,z+0.1,extra=ex)
    arm((31,27+by),1,-0.35,1)
    for k,(a,b) in enumerate(legs):
        z=2 if k==0 else 3; ex=-0.35 if k==0 else 0
        knee=rot(hip,a,TH); ankle=rot(knee,b,SH)
        capsule(cv,hip,knee,3.0,2.5,PANT,z,extra=ex)
        capsule(cv,knee,ankle,2.5,2.0,PANT,z,extra=ex)
        lift=max(0,math.sin(t+(0 if k else math.pi)-1.2))*1.5
        ellipse(cv,ankle[0]+2.2,ankle[1]+1.0-lift*0.5,3.4,1.7,SHOE,z+0.2,extra=ex-0.1)
    # торс: риза, елек отстрани, пояс
    capsule(cv,(31,28+by),(31.5,38+by),6.2,6.0,SHIRT,5)
    poly(cv,[(25,24+by),(33.5,24+by),(34,41+by),(25.5,41+by)],VEST,5.5)
    for y in range(int(25+by),int(41+by)): cv.plot(34,y,RED,9,985)
    poly(cv,[(25,39+by),(37.5,39+by),(37.5,43+by),(25,43+by)],SASH,6)
    if kaval_near: kaval(cv,(26,50+by),(37,30+by),6.3)
    else:          kaval(cv,(26,50+by),(37,30+by),0.3)
    # глава отстрани
    hc=(34,15.5+by)
    capsule(cv,(32,23+by),(33,21+by),2.2,2.2,SKIN,5.6,extra=-0.2)
    ellipse(cv,hc[0],hc[1],6.4,7.0,SKIN,6)
    ellipse(cv,hc[0]-0.6,hc[1]-6.2,6.8,5.6,KALP,6.6,mask=lambda x,y:y<hc[1]-2.2)
    for (dx,dy) in ((-4,-9),(-1,-10),(2,-9),(-3,-6)): cv.plot(int(hc[0]+dx),int(hc[1]+dy),KALP[0],9,980)
    ellipse(cv,hc[0]-3.5,hc[1]+0.5,3.2,4.0,HAIR,6.4,mask=lambda x,y:x<hc[0]-2 and y<hc[1]+4)   # коса на тила
    ey=int(hc[1]+0.5); ex=int(hc[0]+3)
    cv.plot(ex,ey,EYE,9,997); cv.plot(ex,ey-2,HAIR[2],9,993); cv.plot(ex+1,ey-2,HAIR[2],9,993)
    cv.plot(int(hc[0]+6.5),ey+1,SKIN[1],9,996); cv.plot(int(hc[0]+6.5),ey+2,SKIN[2],9,996)      # нос
    for x in range(ex,ex+4): cv.plot(x,ey+3,HAIR[3],9,995)                                      # мустак
    cv.plot(ex,ey+4,HAIR[3],9,995)
    cv.plot(ex+2,ey+5,MOUTH,9,994)
    cv.plot(int(hc[0]-1),ey+1,SKIN[2],9,994); cv.plot(int(hc[0]-1),ey+2,SKIN[3],9,994)          # ухо
    # близка ръка
    arm((32,27+by),7,0,-1)
    return finish(cv,OUT)

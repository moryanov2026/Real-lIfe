# Персона "Иван" (сервитьорът) в празнична носия: бяла риза с шевици на ръкавите,
# бял елек с черни гайтани, черен пояс с бели ивици, бели потури с гайтани на подбедриците, цървули.
# front(i) = отпред, front(i, True) = отзад, side(i) = надясно, dance(i) = хоро (8 кадъра).
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pix import *

M=lambda *a: tuple(hx(c) for c in a)
SKIN=M('#f4d2b0','#e8b78e','#cc916a','#9a6448')
HAIR=M('#6a4a34','#4e3424','#36241a','#22160e')
SHIRT=M('#ffffff','#f1ede4','#d8d0c0','#aaa292')
VEST=M('#fdf9ee','#efe6d0','#d6c8aa','#a8977a')
PANT=M('#fbf5e8','#ece2cc','#d2c4a6','#a8987a')
SASH=M('#3e3a44','#28252e','#1c1a22','#0f0e13')
SHOE=M('#4a3a30','#342822','#241c18','#16100c')
BRAID=hx('#1a1614'); STRIPE=hx('#d8d4cc')
RED=hx('#d8322e'); ORANGE=hx('#f08c2a'); GREEN=hx('#3c9a4a'); BLUE=hx('#2e6ad0'); YEL=hx('#f2c230')
OUT=hx('#1e1410'); EYE=hx('#2a1d16'); MOUTH=hx('#8c4a3e')

def rot(p,ang,L):
    a=math.radians(ang); return (p[0]+L*math.sin(a), p[1]+L*math.cos(a))

def шевица(cv,cx,cy,z=9):
    """Ромб с шевица на ръкава (3x3 + връх)."""
    for (dx,dy,c) in ((0,-1,ORANGE),(-1,0,RED),(0,0,YEL),(1,0,RED),(0,1,ORANGE),(-1,-1,GREEN),(1,1,GREEN),(0,2,RED)):
        cv.plot(int(cx+dx),int(cy+dy),c,z,979)

def ръкав(cv,sh,el,hd,z,ex=0.0,шевици=True):
    capsule(cv,sh,el,2.6,2.3,SHIRT,z,extra=ex)
    capsule(cv,el,hd,2.3,2.0,SHIRT,z,extra=ex)
    if шевици:
        шевица(cv,(sh[0]*0.55+el[0]*0.45),(sh[1]*0.55+el[1]*0.45)-0.5)
        for k,c in ((0.35,BLUE),(0.6,RED),(0.85,YEL)):              # цветни точки надолу по ръкава
            cv.plot(int(el[0]+(hd[0]-el[0])*k),int(el[1]+(hd[1]-el[1])*k),c,9,978)
    ellipse(cv,hd[0],hd[1]+1.3,1.9,1.9,SKIN,z+0.3,extra=-0.1)

def гайтан_извивка(cv,x,y,огледално=False):
    """Малка черна извивка от гайтан (като спирала)."""
    s=-1 if огледално else 1
    for (dx,dy) in ((0,0),(1,0),(2,1),(1,2),(0,2),(-1,1)):
        cv.plot(int(x+dx*s),int(y+dy),BRAID,9,977)

def легенче(cv,x,y_от,y_до):
    """Гайтани на подбедрицата на потурите: черна линия с извивки отстрани."""
    for y in range(int(y_от),int(y_до)):
        cv.plot(int(x),y,BRAID,9,976)
        if (y-int(y_от))%3==1:
            cv.plot(int(x)-1,y,BRAID,9,976); cv.plot(int(x)+1,y,BRAID,9,976)

def head_front(cv,hc,back=False,усмивка=False):
    ellipse(cv,hc[0],hc[1],6.6,7.2,SKIN,6)
    # къса тъмна коса с път отстрани
    ellipse(cv,hc[0],hc[1]-1.5,7.0,6.6,HAIR,6.5,mask=(lambda x,y:y<hc[1]+4) if back else (lambda x,y:(y<hc[1]-3.0) or ((x<hc[0]-5.5 or x>hc[0]+5) and y<hc[1]+0.5)))
    if back:
        return
    ey=int(hc[1]+0.5)
    for x in (27,28,29): cv.plot(x,ey-4,HAIR[1],9,990)                     # бретон, сресан встрани
    for ex in (29,34):
        if усмивка:
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,EYE,9,997)
        else:
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,hx('#fbf4e2'),9,997)
        cv.plot(ex,ey-2,HAIR[2],9,993); cv.plot(ex+1,ey-2,HAIR[2],9,993)
    cv.plot(31,ey+1,SKIN[2],9,996); cv.plot(32,ey+2,SKIN[2],9,996)         # нос
    for x in range(30,35): cv.plot(x,ey+3,HAIR[2],9,995)                   # тънък мустак
    if усмивка:
        for x in (30,31,32,33): cv.plot(x,ey+5,MOUTH,9,994)
        cv.plot(29,ey+4,MOUTH,9,994); cv.plot(34,ey+4,MOUTH,9,994)
    else:
        cv.plot(31,ey+5,MOUTH,9,994); cv.plot(32,ey+5,MOUTH,9,994)
    cv.plot(28,ey+2,hx('#eca088'),9,993); cv.plot(36,ey+2,hx('#eca088'),9,993)

def торс_отпред(cv,by,back):
    capsule(cv,(32,27+by),(32,37+by),7.4,7.0,SHIRT,5)
    if not back:
        poly(cv,[(24.5,24+by),(30.2,24+by),(30.5,39+by),(24.5,39+by)],VEST,5.5,extra=0.05)
        poly(cv,[(33.8,24+by),(39.5,24+by),(39.5,39+by),(33.5,39+by)],VEST,5.5,extra=-0.05)
        for y in range(int(24+by),int(39+by)):                       # черни гайтани по ръба на елека
            cv.plot(30,y,BRAID,9,986); cv.plot(33,y,BRAID,9,986)
            cv.plot(24,y,BRAID,9,985); cv.plot(39,y,BRAID,9,985)
        гайтан_извивка(cv,26,int(28+by)); гайтан_извивка(cv,37,int(28+by),True)
        гайтан_извивка(cv,26,int(33+by)); гайтан_извивка(cv,37,int(33+by),True)
        for x in (31,32): cv.plot(x,int(24+by),RED,9,986)              # червен кант на яката
        cv.plot(31,int(25+by),RED,9,986)
    else:
        poly(cv,[(24.5,24+by),(39.5,24+by),(39.5,39+by),(24.5,39+by)],VEST,5.5)
        for y in range(int(26+by),int(36+by)): cv.plot(31,y,BRAID,9,985); cv.plot(32,y,BRAID,9,985)
        гайтан_извивка(cv,28,int(29+by),True); гайтан_извивка(cv,35,int(29+by))
        for x in range(25,40): cv.plot(x,int(24+by),BRAID,9,985)
    # широк черен пояс с бели ивици
    poly(cv,[(24,38+by),(40,38+by),(40,44+by),(24,44+by)],SASH,6)
    for x in range(25,40): cv.plot(x,int(40+by),STRIPE,9,984); cv.plot(x,int(42+by),STRIPE,9,984)

def крака_отпред(cv,by,лифт,навън=(0,0)):
    ellipse(cv,32,45.5+by,8.0,3.6,PANT,2.4)                              # потурите са широки горе
    for k,x in enumerate((29,35)):
        ay=58.5-лифт[k]; nx=x+навън[k]
        capsule(cv,(x,44+by),(nx,ay-1),3.4,2.6,PANT,2,extra=(-0.12 if k else 0))
        легенче(cv,nx,ay-9,ay-1)
        ellipse(cv,nx+(-0.3 if k==0 else 0.3),ay+1.1,2.8,1.8,SHOE,2.2)

def front(i, back=False):
    t=2*math.pi*i/8
    cv=Canvas()
    by=round(0.5*(1+math.cos(2*t)))
    крака_отпред(cv,by,[max(0,math.sin(t))*2.5, max(0,math.sin(t+math.pi))*2.5])
    торс_отпред(cv,by,back)
    for s in (-1,1):
        sway=1.3*math.sin(t+(0 if s>0 else math.pi))
        sh=(32+s*7.6,27+by); el=(32+s*9.4,33+by); hd=(32+s*9.6,39.5+by+sway)
        ръкав(cv,sh,el,hd,6.5,шевици=not back)
    head_front(cv,(32,15.5+by),back)
    return finish(cv,OUT)

def dance(i):
    """Мъжко хоро отпред: двете ръце протегнати встрани (държи съседите), краката подритват на ред."""
    t=2*math.pi*i/8
    cv=Canvas()
    вдигане=[0,3,6,3,0,0,0,0]
    by=[1,0,0,0,1,0,0,0][i]
    л=[вдигане[i], вдигане[(i+4)%8]]
    крака_отпред(cv,by,л,навън=(-л[0]*0.35, л[1]*0.35))
    торс_отпред(cv,by,False)
    for s in (-1,1):
        вълна=0.8*math.sin(t+(0 if s>0 else math.pi))
        sh=(32+s*7.6,27+by); el=(32+s*12,29.5+by); hd=(32+s*16.5,30.5+by+вълна)
        ръкав(cv,sh,el,hd,6.5)
    head_front(cv,(32,15.5+by),усмивка=True)
    return finish(cv,OUT)

def side(i, ляво=False):
    t=2*math.pi*i/8
    cv=Canvas()
    TH,SH=9.5,9.5
    def leg(ph):
        th=22*math.sin(ph); knee=max(0,40*math.sin(ph-1.3)); return th, th-knee
    legs=[leg(t+math.pi), leg(t)]
    ank=[TH*math.cos(math.radians(a))+SH*math.cos(math.radians(b)) for a,b in legs]
    hipY=59.0-max(ank); by=hipY-41.5; hip=(31.5,hipY)
    def arm(sh,z,ex,sgn):
        fa=-18*math.sin(t)*sgn
        el=rot(sh,fa,6.5); hd=rot(el,fa+15,6.2)
        ръкав(cv,sh,el,hd,z,ex)
    arm((31,27+by),1,-0.35,1)
    ellipse(cv,31.5,hipY+1,5.5,4.0,PANT,2.5)                                # широки потури отзад
    for k,(a,b) in enumerate(legs):
        z=2 if k==0 else 3; ex=-0.35 if k==0 else 0
        knee=rot(hip,a,TH); ankle=rot(knee,b,SH)
        capsule(cv,hip,knee,3.4,2.8,PANT,z,extra=ex)
        capsule(cv,knee,ankle,2.8,2.1,PANT,z,extra=ex)
        for kk in range(1,6):                                              # гайтан по подбедрицата
            x=knee[0]+(ankle[0]-knee[0])*kk/6+1.5; y=knee[1]+(ankle[1]-knee[1])*kk/6
            cv.plot(int(x),int(y),BRAID,z+0.5,976)
        lift=max(0,math.sin(t+(0 if k else math.pi)-1.2))*1.5
        ellipse(cv,ankle[0]+2.2,ankle[1]+1.0-lift*0.5,3.4,1.7,SHOE,z+0.2,extra=ex-0.1)
    capsule(cv,(31,28+by),(31.5,38+by),6.2,6.0,SHIRT,5)
    poly(cv,[(25,24+by),(33.5,24+by),(34,40+by),(25.5,40+by)],VEST,5.5)
    for y in range(int(24+by),int(40+by)): cv.plot(34,y,BRAID,9,985); cv.plot(25,y,BRAID,9,985)
    гайтан_извивка(cv,29,int(29+by)); гайтан_извивка(cv,29,int(34+by))
    poly(cv,[(25,38+by),(37.5,38+by),(37.5,44+by),(25,44+by)],SASH,6)
    for x in range(26,37): cv.plot(x,int(40+by),STRIPE,9,984); cv.plot(x,int(42+by),STRIPE,9,984)
    hc=(34,15.5+by)
    capsule(cv,(32,23+by),(33,21+by),2.2,2.2,SKIN,5.6,extra=-0.2)
    ellipse(cv,hc[0],hc[1],6.4,7.0,SKIN,6)
    ellipse(cv,hc[0]-1.2,hc[1]-1.8,6.8,6.2,HAIR,6.5,mask=lambda x,y:(y<hc[1]-3.0) or (x<hc[0]-2 and y<hc[1]+3))
    ey=int(hc[1]+0.5); ex=int(hc[0]+3)
    cv.plot(ex,ey,EYE,9,997); cv.plot(ex,ey-2,HAIR[2],9,993); cv.plot(ex+1,ey-2,HAIR[2],9,993)
    cv.plot(int(hc[0]+6.5),ey+1,SKIN[1],9,996); cv.plot(int(hc[0]+6.5),ey+2,SKIN[2],9,996)
    for x in range(ex,ex+3): cv.plot(x,ey+3,HAIR[2],9,995)
    cv.plot(ex+1,ey+5,MOUTH,9,994)
    cv.plot(int(hc[0]-1),ey+1,SKIN[2],9,994); cv.plot(int(hc[0]-1),ey+2,SKIN[3],9,994)
    arm((32,27+by),7,0,-1)
    return finish(cv,OUT)

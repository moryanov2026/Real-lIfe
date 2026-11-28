# Персона "Димитър" (собственикът на кръчмата): около 50 години, пълен, черна коса с бели слепоочия,
# гъсти черни мустаци. Носия: бяла риза с шевици на яката и маншетите, червен елек с черни гайтани
# и жълти клонки, червен пояс, черни потури с черни гайтани долу, черни цървули.
# front(i) = отпред, front(i, True) = отзад, side(i) = надясно, dance(i) = хоро (8 кадъра).
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pix import *

M=lambda *a: tuple(hx(c) for c in a)
SKIN=M('#f2cba6','#e2ad84','#c48760','#925c40')
HAIR=M('#4a4650','#2c2a30','#1c1a20','#0e0d10')
GREY=hx('#c8c4c0')
SHIRT=M('#ffffff','#f1ede4','#d8d0c0','#aaa292')
VEST=M('#f0524a','#d42a26','#a8181a','#6e0e12')
BELT=M('#e8443e','#c42420','#961418','#5e0c10')
PANT=M('#4a4652','#2e2b34','#1e1c24','#121016')
SHOE=M('#3a3230','#262020','#181414','#0c0a0a')
BRAID=hx('#141012'); GOLD=hx('#f2cc2e'); GOLD2=hx('#b8901a')
RED=hx('#d8322e'); ORANGE=hx('#f08c2a'); GREEN=hx('#3c9a4a'); BLUE=hx('#2e6ad0'); YEL=hx('#f2c230')
OUT=hx('#1e1410'); EYE=hx('#2a1d16'); MOUTH=hx('#8c4a3e'); BUZI=hx('#e89a84')

def rot(p,ang,L):
    a=math.radians(ang); return (p[0]+L*math.sin(a), p[1]+L*math.cos(a))

def шевица(cv,cx,cy):
    for (dx,dy,c) in ((0,-1,ORANGE),(-1,0,RED),(0,0,YEL),(1,0,RED),(0,1,ORANGE)):
        cv.plot(int(cx+dx),int(cy+dy),c,9,979)

def ръкав(cv,sh,el,hd,z,ex=0.0,маншет=True):
    capsule(cv,sh,el,3.0,2.6,SHIRT,z,extra=ex)
    capsule(cv,el,hd,2.6,2.3,SHIRT,z,extra=ex)
    if маншет:                                      # шевица на маншета, като на снимката
        mx,my=el[0]+(hd[0]-el[0])*0.72, el[1]+(hd[1]-el[1])*0.72
        for d,c in ((-1,RED),(0,ORANGE),(1,RED)):
            cv.plot(int(mx+d),int(my),c,z+0.6,978)
        cv.plot(int(mx),int(my)+1,GREEN,z+0.6,978)
    гънка(cv,el,SHIRT,z)
    ellipse(cv,hd[0],hd[1]+1.4,2.1,2.0,SKIN,z+0.3,extra=-0.1)

def клонка(cv,x,y,s=1):
    """Жълта бродирана клонка (листенца) върху елека."""
    for k in range(5):
        cv.plot(int(x+s*k*0.5),int(y+k),GOLD,9,977)
        if k%2==0:
            cv.plot(int(x+s*(k*0.5+1)),int(y+k),GOLD2,9,977)
            cv.plot(int(x+s*(k*0.5-1)),int(y+k),GOLD,9,977)

def гайтан_извивка(cv,x,y,огледално=False):
    s=-1 if огледално else 1
    for (dx,dy) in ((0,0),(1,0),(2,1),(1,2),(0,2),(-1,1)):
        cv.plot(int(x+dx*s),int(y+dy),BRAID,9,977)

def head_front(cv,hc,back=False,усмивка=False):
    ellipse(cv,hc[0],hc[1]+2.5,5.0,3.0,SKIN,5.8,extra=0.25)         # двойна брадичка
    ellipse(cv,hc[0],hc[1],7.2,7.2,SKIN,6)                            # по-кръгло лице
    if not back:
        кичури(cv,(hc[0],hc[1]-0.5),HAIR)
        сянка_брадичка(cv,(hc[0],hc[1]+1.5),SHIRT)
    if back:
        ellipse(cv,hc[0],hc[1]-1.0,7.5,6.8,HAIR,6.5,mask=lambda x,y:y<hc[1]+4)
        for y in range(int(hc[1]-1),int(hc[1]+4)):                    # прошарено отзад и отстрани
            cv.plot(int(hc[0]-7),y,GREY,9,989); cv.plot(int(hc[0]+6),y,GREY,9,989)
        return
    ellipse(cv,hc[0],hc[1]-2.0,7.5,6.4,HAIR,6.5,
            mask=lambda x,y:(y<hc[1]-3.5) or ((x<hc[0]-6 or x>hc[0]+5.5) and y<hc[1]+0.5))
    ey=int(hc[1]+0.5)
    for y in (ey-3,ey-2,ey-1):                                        # бели слепоочия (50 години)
        cv.plot(int(hc[0]-7),y,GREY,9,990); cv.plot(int(hc[0]+6),y,GREY,9,990)
    for ex in (28,34):
        if усмивка:
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,EYE,9,997)
        else:
            cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,hx('#fbf4e2'),9,997)
        cv.plot(ex-1,ey-2,HAIR[1],9,993); cv.plot(ex,ey-2,HAIR[1],9,993); cv.plot(ex+1,ey-2,HAIR[1],9,993)  # гъсти вежди
    cv.plot(31,ey+1,SKIN[2],9,996); cv.plot(32,ey+1,SKIN[2],9,996); cv.plot(31,ey+2,SKIN[3],9,996)  # нос
    for x in range(28,36): cv.plot(x,ey+3,HAIR[2],9,995)              # гъст мустак
    for x in (28,29,30,33,34,35): cv.plot(x,ey+4,HAIR[1],9,995)
    cv.plot(28,ey+5,HAIR[2],9,995); cv.plot(35,ey+5,HAIR[2],9,995)     # краищата му висят надолу
    if усмивка:
        for x in (30,31,32,33): cv.plot(x,ey+6,MOUTH,9,994)
    else:
        cv.plot(31,ey+6,MOUTH,9,994); cv.plot(32,ey+6,MOUTH,9,994)
    cv.plot(26,ey+2,BUZI,9,993); cv.plot(37,ey+2,BUZI,9,993)           # червени бузи

def торс_отпред(cv,by,back):
    capsule(cv,(32,28+by),(32,37+by),9.0,9.6,SHIRT,5)                 # пълно тяло
    if not back:
        ellipse(cv,32,38+by,9.6,6.8,BELT,5.2)                         # коремът (червен пояс/риза отдолу)
        poly(cv,[(22.5,24+by),(30,24+by),(29.5,41+by),(22,41+by)],VEST,5.5,extra=0.05)
        poly(cv,[(34,24+by),(41.5,24+by),(42,41+by),(34.5,41+by)],VEST,5.5,extra=-0.05)
        for y in range(int(24+by),int(41+by)):                        # черен кант по ръба на елека
            cv.plot(29,y,BRAID,9,986); cv.plot(30,y,BRAID,9,986); cv.plot(34,y,BRAID,9,986)
            cv.plot(22,y,BRAID,9,985); cv.plot(41,y,BRAID,9,985)
        for x in range(22,31): cv.plot(x,int(41+by),BRAID,9,985)
        for x in range(34,42): cv.plot(x,int(41+by),BRAID,9,985)
        клонка(cv,25,int(25+by),1); клонка(cv,38,int(25+by),-1)         # жълтите клонки горе
        гайтан_извивка(cv,25,int(31+by)); гайтан_извивка(cv,38,int(31+by),True)
        for y in range(int(35+by),int(39+by)):                        # джобчета с гайтан
            cv.plot(24,y,GOLD,9,984); cv.plot(39,y,GOLD,9,984)
        for x in (31,32,33): cv.plot(x,int(23+by),SHIRT[1],9,987)      # яката с шевица
        шевица(cv,32,int(25+by))
        for y in range(int(26+by),int(31+by)): cv.plot(32,y,RED,9,986)  # кантът на ризата
    else:
        poly(cv,[(22.5,24+by),(41.5,24+by),(42,41+by),(22,41+by)],VEST,5.5)
        for x in range(22,42): cv.plot(x,int(24+by),BRAID,9,985); cv.plot(x,int(41+by),BRAID,9,985)
        гайтан_извивка(cv,27,int(29+by),True); гайтан_извивка(cv,36,int(29+by))
        клонка(cv,30,int(32+by),1); клонка(cv,33,int(32+by),-1)

def крака_отпред(cv,by,лифт,навън=(0,0)):
    ellipse(cv,32,45.5+by,8.6,3.8,PANT,2.4)
    for k,x in enumerate((28.5,35.5)):
        ay=58.5-лифт[k]; nx=x+навън[k]
        capsule(cv,(x,44+by),(nx,ay-1),3.8,2.8,PANT,2,extra=(-0.12 if k else 0))
        гънка(cv,((x+nx)/2,(44+by+ay)/2),PANT,2)
        for y in range(int(ay-7),int(ay)):                            # черни гайтани долу на крачола
            if y%2: cv.plot(int(nx)+(1 if k else -1),y,BRAID,9,976)
        ellipse(cv,nx+(-0.3 if k==0 else 0.3),ay+1.1,3.0,1.8,SHOE,2.2)

def front(i, back=False):
    t=2*math.pi*i/8
    cv=Canvas()
    by=round(0.5*(1+math.cos(2*t)))
    крака_отпред(cv,by,[max(0,math.sin(t))*2.2, max(0,math.sin(t+math.pi))*2.2])
    торс_отпред(cv,by,back)
    for s in (-1,1):
        sway=1.1*math.sin(t+(0 if s>0 else math.pi))
        sh=(32+s*9.0,27+by); el=(32+s*11.2,33+by); hd=(32+s*11.4,39.5+by+sway)
        ръкав(cv,sh,el,hd,6.5,маншет=not back)
    head_front(cv,(32,15.5+by),back)
    return finish(cv,OUT)

def dance(i):
    """Хоро отпред: ръцете встрани (държи съседите), краката подритват на ред."""
    t=2*math.pi*i/8
    cv=Canvas()
    вдигане=[0,2,5,2,0,0,0,0]
    by=[1,0,0,0,1,0,0,0][i]
    л=[вдигане[i], вдигане[(i+4)%8]]
    крака_отпред(cv,by,л,навън=(-л[0]*0.35, л[1]*0.35))
    торс_отпред(cv,by,False)
    for s in (-1,1):
        вълна=0.8*math.sin(t+(0 if s>0 else math.pi))
        sh=(32+s*9.0,27+by); el=(32+s*13,29.5+by); hd=(32+s*17,30.5+by+вълна)
        ръкав(cv,sh,el,hd,6.5)
    head_front(cv,(32,15.5+by),усмивка=True)
    return finish(cv,OUT)

def side(i):
    t=2*math.pi*i/8
    cv=Canvas()
    TH,SH=9.0,9.5
    def leg(ph):
        th=18*math.sin(ph); knee=max(0,34*math.sin(ph-1.3)); return th, th-knee
    legs=[leg(t+math.pi), leg(t)]
    ank=[TH*math.cos(math.radians(a))+SH*math.cos(math.radians(b)) for a,b in legs]
    hipY=59.0-max(ank); by=hipY-41.5; hip=(30.5,hipY)
    def arm(sh,z,ex,sgn):
        fa=-15*math.sin(t)*sgn
        el=rot(sh,fa,6.5); hd=rot(el,fa+15,6.2)
        ръкав(cv,(sh[0],sh[1]),el,hd,z,ex)
    arm((29,27+by),1,-0.35,1)
    for k,(a,b) in enumerate(legs):
        z=2 if k==0 else 3; ex=-0.35 if k==0 else 0
        knee=rot(hip,a,TH); ankle=rot(knee,b,SH)
        capsule(cv,hip,knee,3.8,3.0,PANT,z,extra=ex)
        capsule(cv,knee,ankle,3.0,2.3,PANT,z,extra=ex)
        for kk in range(3,6):
            x=knee[0]+(ankle[0]-knee[0])*kk/6+1.8; y=knee[1]+(ankle[1]-knee[1])*kk/6
            cv.plot(int(x),int(y),BRAID,z+0.5,976)
        ellipse(cv,ankle[0]+2.2,ankle[1]+1.0,3.4,1.7,SHOE,z+0.2,extra=ex-0.1)
    capsule(cv,(30,28+by),(31,36+by),7.6,8.4,SHIRT,5)                # пълно тяло, коремът напред
    ellipse(cv,33.5,37+by,6.2,5.0,BELT,5.2,extra=0.3)                          # червеният пояс върху корема
    poly(cv,[(22,24+by),(33,24+by),(36,30+by),(37,40+by),(22.5,41+by)],VEST,5.5)
    for y in range(int(24+by),int(41+by)): cv.plot(22,y,BRAID,9,985)
    for (x0,y0,x1,y1) in ((33,24,36,30),(36,30,37,40)):               # предният ръб на елека
        for k in range(12):
            cv.plot(int(x0+(x1-x0)*k/11),int(y0+by+(y1-y0)*k/11),BRAID,9,985)
    for x in range(22,38): cv.plot(x,int(41+by),BRAID,9,985)
    клонка(cv,28,int(25+by),1); гайтан_извивка(cv,26,int(32+by))
    hc=(33,15.5+by)
    capsule(cv,(31,23+by),(32,21+by),2.6,2.6,SKIN,5.6,extra=0.1)
    ellipse(cv,hc[0]+1.5,hc[1]+3,4.6,3.2,SKIN,5.8,extra=0.2)          # двойна брадичка
    ellipse(cv,hc[0],hc[1],6.8,7.0,SKIN,6,extra=0.35)
    ellipse(cv,hc[0]-1.2,hc[1]-1.8,7.0,6.2,HAIR,6.5,mask=lambda x,y:(y<hc[1]-3.0) or (x<hc[0]-2 and y<hc[1]+3))
    ey=int(hc[1]+0.5); ex=int(hc[0]+3)
    for y in (ey-3,ey-2): cv.plot(int(hc[0]-3),y,GREY,9,990)          # прошарено слепоочие
    cv.plot(ex,ey,EYE,9,997)
    for x in (ex-1,ex,ex+1): cv.plot(x,ey-2,HAIR[1],9,993)
    cv.plot(int(hc[0]+6.5),ey+1,SKIN[2],9,996); cv.plot(int(hc[0]+6.5),ey+2,SKIN[2],9,996)
    for x in range(ex,ex+4): cv.plot(x,ey+3,HAIR[2],9,995)            # гъстият мустак отстрани
    cv.plot(ex,ey+4,HAIR[1],9,995); cv.plot(ex+1,ey+4,HAIR[1],9,995); cv.plot(ex,ey+5,HAIR[2],9,995)
    cv.plot(ex+2,ey+6,MOUTH,9,994)
    cv.plot(ex-1,ey+2,BUZI,9,993)
    cv.plot(int(hc[0]-1),ey+1,SKIN[2],9,994); cv.plot(int(hc[0]-1),ey+2,SKIN[3],9,994)
    arm((31,27+by),7,0,-1)
    return finish(cv,OUT)

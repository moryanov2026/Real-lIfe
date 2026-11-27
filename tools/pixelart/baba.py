# Персона "баба Стана": рисува се от части с обем (виж pix.py).
# side(i) = кадър i (0-7) отстрани, front(i) = отпред, front(i, True) = отзад.
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # pix.py е в същата папка
from pix import *

M=lambda *a: tuple(hx(c) for c in a)
SKIN=M('#f7dcc0','#f2c7a0','#d9a07a','#a8705a')
HAIR=M('#ffffff','#eeebe4','#c9c3b8','#948e86')
# Празнична носия: бяла риза, черен сукман, червен пояс, червена каре престилка с жълта дантела.
CARD=M('#4c4652','#33303a','#24212b','#16141b')        # сукманът (черен) - горната част
SLEEVE=M('#ffffff','#f1ede4','#d8d0c0','#aaa292')      # бялата риза (ръкави, яка)
SASH=M('#f0503c','#d63326','#a82418','#76180f')        # червеният пояс
SKIRT=M('#3c3842','#2a2730','#1f1c25','#141219')   # сукманът отдолу (черен)
APRON=M('#f4584a','#e03a2e','#b52a22','#821c18')   # каре престилката (десенът се слага накрая)
STOCK=M('#b0a090','#8e7e6e','#6c5e52','#4a4038')
SHOE=M('#5a4636','#433226','#33251c','#221710')
CANE=M('#d09a5c','#ad7440','#87552e','#5e3a1e')
OUT=hx('#1e1410'); FRAME=hx('#6e4a30'); MOUTH=hx('#8c4a3e'); LENS=hx('#d6ecf4'); GLASS=hx('#8fb4c8'); BLUSH=hx('#e8907a'); EYE=hx('#2a1d16')

def престилка_отпред(cv,by,sw,w0,w1):
    """Голяма каре престилка (десенът и жълтата дантела се слагат в облечи), червен пояс, бяла кърпа."""
    poly(cv,[(26,w0+0.5),(38,w0+0.5),(40.5+sw,w1-1.5),(23.5+sw,w1-1.5)],APRON,5.2,extra=0.1,
         folds=((lambda y:32+sw*(y-w0)/15,0.3),))
    poly(cv,[(24.5,w0-2),(39.5,w0-2),(39.5,w0+0.8),(24.5,w0+0.8)],SASH,5.8)
    poly(cv,[(34,w0+0.5),(38.5,w0+0.5),(36.8,w0+5.5)],SLEEVE,5.9)          # бялата кърпа, затъкната в пояса
    cv.plot(36,int(w0+4),hx('#d63326'),9,970); cv.plot(35,int(w0+2),hx('#d63326'),9,970)

def деколте(cv,by):
    """Бяла яка с червени шевици и бяла дантела около деколтето на сукмана."""
    for (x,y) in ((25,26),(26,27),(27,28),(28,29),(29,30),(30,30),(31,31),(32,31),(33,30),(34,30),(35,29),(36,28),(37,27),(38,26)):
        cv.plot(x,int(y+by),hx('#f6f3ec') if (x%2) else hx('#d2ccc0'),9,972)
    for (x,y) in ((26,26),(27,27),(37,26),(36,27)):
        cv.plot(x,int(y+by),hx('#d63326'),9,972)                          # червен кант
    for (x,y) in ((31,27),(32,27),(31,28),(32,29),(30,28),(33,28)):
        cv.plot(x,int(y+by),hx('#d63326'),9,973)                          # шевица на ризата

def облечи(px):
    """Накрая: каре десен на престилката, жълта дантела по края ѝ, дантела и червена лента по подгъва,
    дантела с червен кант на маншетите."""
    H,W=len(px),len(px[0])
    престилка=set(APRON); пола=set(SKIRT); ръкав=set(SLEEVE); кожа=set(SKIN)
    нов=[ред[:] for ред in px]
    for y in range(H):
        for x in range(W):
            ц=px[y][x]
            if ц in престилка:
                съседи=[px[y][x-1] if x>0 else None, px[y][x+1] if x<W-1 else None, px[y+1][x] if y<H-1 else None]
                if any(с not in престилка and с not in ръкав and с not in (hx('#d63326'),) for с in съседи):   # кърпата не е ръб
                    нов[y][x]=hx('#f2c230') if (x+y)%2 else hx('#e8b020')      # жълта дантела
                elif x%4==0 and y%4==0:
                    нов[y][x]=hx('#1e1014')                                    # пресичане на черните ивици
                elif x%4==0 or y%4==0:
                    нов[y][x]=hx('#5a1c1c') if ц in (APRON[2],APRON[3]) else hx('#3a1a1c')   # черни ивици
                elif x%4==2 and y%4==2:
                    нов[y][x]=hx('#f6e6dc')                                    # бяла нишка
            elif ц in ръкав:
                if any(0<=y+dy<H and 0<=x+dx<W and px[y+dy][x+dx] in кожа for dx,dy in ((0,1),(1,0),(-1,0),(0,-1))) and y>24:
                    нов[y][x]=hx('#d63326') if (x+y)%2 else hx('#f6f3ec')       # маншет с дантела
    for x in range(W):                                    # подгъвът на полата
        долу=[y for y in range(H) if px[y][x] in пола]
        if not долу:
            continue
        b=max(долу)
        if px[b-1][x] in пола: нов[b-1][x]=hx('#f6f3ec') if x%2 else hx('#cfc9be')
        zig=b-3 if x%2 else b-4
        if 0<=zig<H and px[zig][x] in пола: нов[zig][x]=hx('#e03a2e')
    return нов

def rot(p,ang,L):
    a=math.radians(ang); return (p[0]+L*math.sin(a), p[1]+L*math.cos(a))

def side(i, cane_near=True, седи=0.0):
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
    if седи:                                       # седнала: бедрата напред (хоризонтално), подбедрицата надолу
        legs=[(90*седи-6, -4.0*седи), (90*седи, 0.0)]
    ank=[TH*math.cos(math.radians(a))+SH*math.cos(math.radians(b)) for a,b in legs]
    hipY=59.5-max(ank)                            # най-ниското стъпало стои на земята
    by=hipY-40.5
    hip=(30.5,hipY)
    def cane_arm(sh,z,ex):
        hand=(41.5+1.2*math.sin(t+math.pi),37.5+by)
        elb=((sh[0]+hand[0])/2+0.5,(sh[1]+hand[1])/2+2)
        capsule(cv,sh,elb,2.4,2.1,SLEEVE,z,extra=ex)
        capsule(cv,elb,hand,2.0,1.7,SLEEVE,z,extra=ex)
        tip=(hand[0]+1.5+2.5*math.sin(t+math.pi),61.5)
        capsule(cv,(hand[0]+0.5,hand[1]-1),tip,1.0,1.0,CANE,z+0.5)
        capsule(cv,(hand[0]-2,hand[1]-2.5),(hand[0]+1,hand[1]-2.8),1.0,1.0,CANE,z+0.6)
        ellipse(cv,hand[0]+0.5,hand[1],2.0,2.0,SKIN,z+1,extra=ex)
    def swing_arm(sh,z,ex,sgn):
        fa=-14*math.sin(t)*sgn
        el=rot(sh,fa,6); hd=rot(el,fa+20,6)
        capsule(cv,sh,el,2.2,2.0,SLEEVE,z,extra=ex)
        capsule(cv,el,hd,1.9,1.6,SLEEVE,z,extra=ex)
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
    w0=36+by; w1=51+by-round(6*седи)
    skirt=[(23,w0),(38,w0),(42+sw+3*седи,w1-1),(41+sw+3*седи,w1),(21+sw,w1),(20.5+sw,w1-1)]
    folds=((lambda y:27+0.15*(y-w0)+sw*(y-w0)/15,0.45),(lambda y:33+0.25*(y-w0)+sw*(y-w0)/15,0.45))
    poly(cv,skirt,SKIRT,4,folds=folds)
    # престилка отпред
    ap=[(33.5,w0+0.5),(38.5,w0+0.5),(42.5+sw,w1-1.5),(36+sw,w1-1.5)]
    poly(cv,ap,APRON,4.5,extra=0.1)
    poly(cv,[(23.5,w0-1.5),(37.5,w0-1.5),(37.5,w0+1),(23.5,w0+1)],SASH,5.6)
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
    return облечи(finish(cv,OUT))

def front(i, back=False, седи=0.0):
    t=2*math.pi*i/8
    cv=Canvas()
    by=round(0.5*(1+math.cos(2*t)))            # най-ниско при стъпване
    by+=round(7*седи)                          # седнала: цялото тяло е по-ниско, колената под полата
    lift=[max(0,math.sin(t))*2.5, max(0,math.sin(t+math.pi))*2.5]
    # --- крака
    for k,x in enumerate((28.5,35.5)):
        ay=59.0-lift[k]
        capsule(cv,(x,46+by),(x,ay),2.4,1.9,STOCK,2,extra=(-0.15 if k else 0))
        ellipse(cv,x+(-0.3 if k==0 else 0.3),ay+1.6,2.7,1.8,SHOE,2.2)
    # --- пола
    sw=0.8*math.sin(t)
    w0=36+by; w1=51+by-round(3*седи)
    skirt=[(25-1.5*седи,w0),(39+1.5*седи,w0),(42.5+sw+1.5*седи,w1-1),(41.5+sw+1.5*седи,w1),(22.5+sw-1.5*седи,w1),(21.5+sw-1.5*седи,w1-1)]
    folds=((lambda y:27-0.18*(y-w0)+sw*(y-w0)/15,0.5),(lambda y:32+sw*(y-w0)/15,0.35),(lambda y:37+0.18*(y-w0)+sw*(y-w0)/15,0.5))
    poly(cv,skirt,SKIRT,4,folds=folds)
    if not back:
        престилка_отпред(cv,by,sw,w0,w1)
    # --- торс
    capsule(cv,(32,29.5+by),(32,36+by),7.6,8.0,CARD,5)
    if back:
        # панделка на престилката отзад
        ellipse(cv,32,37+by,2.2,1.6,SASH,5.8); ellipse(cv,29,37+by,2.4,1.5,SASH,5.7); ellipse(cv,35,37+by,2.4,1.5,SASH,5.7)
        capsule(cv,(31,38+by),(29.5,43+by),0.9,0.9,SASH,5.7); capsule(cv,(33,38+by),(34.5,43+by),0.9,0.9,SASH,5.7)
        poly(cv,[(24.5,35.5+by),(39.5,35.5+by),(39.5,38.5+by),(24.5,38.5+by)],SASH,5.6)
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
        capsule(cv,sh,el,2.5,2.2,SLEEVE,z,extra=0.05*side_*(-1))
        capsule(cv,el,hand,2.1,1.8,SLEEVE,z)
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
        poly(cv,[(29.5,25.5+by),(34.5,25.5+by),(32,28.5+by)],SLEEVE,5.8,extra=-0.2); деколте(cv,by)   # шия/деколте
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
    return облечи(finish(cv,OUT))


def dance(i):
    """Хоро: 8 кадъра отпред. Краката се вдигат на ред, бастунът е вдигнат и се размахва,
    другата ръка е протегната встрани (държи съседа), очите са затворени от радост."""
    t=2*math.pi*i/8
    cv=Canvas()
    вдигане=[0,3,5,3,0,0,0,0]
    by=[1,0,0,0,1,0,0,0][i]
    lift=[вдигане[i], вдигане[(i+4)%8]]
    # --- крака (вдигнатият е свит в коляното, стъпалото малко навън)
    for k,x in enumerate((28.5,35.5)):
        ay=59.0-lift[k]
        навън=(-1 if k==0 else 1)*lift[k]*0.3
        capsule(cv,(x,46+by),(x+навън,ay),2.4,1.9,STOCK,2,extra=(-0.15 if k else 0))
        ellipse(cv,x+навън+(-0.3 if k==0 else 0.3),ay+1.6,2.7,1.8,SHOE,2.2)
    # --- пола: люлее се в ритъма
    sw=1.4*math.sin(t)
    w0=36+by; w1=51+by
    poly(cv,[(24.5,w0),(39.5,w0),(43+sw,w1-1),(42+sw,w1),(22+sw,w1),(21+sw,w1-1)],SKIRT,4,
         folds=((lambda y:28-0.15*(y-w0)+sw*(y-w0)/15,0.5),(lambda y:32+sw*(y-w0)/15,0.35),(lambda y:36+0.15*(y-w0)+sw*(y-w0)/15,0.5)))
    престилка_отпред(cv,by,sw,w0,w1)
    # --- торс
    capsule(cv,(32,29.5+by),(32,36+by),7.6,8.0,CARD,5)
    cv.plot(31,int(31+by),CARD[0],9,992); cv.plot(31,int(34+by),CARD[0],9,992)
    # --- дясната ѝ ръка (вляво на екрана): вдигнат бастун, който се размахва
    маха=2.0*math.sin(t)
    sh=(24.8,28.5+by); el=(19.5,23+by); hand=(18.5+маха,16.5+by)
    capsule(cv,sh,el,2.5,2.2,SLEEVE,6)
    capsule(cv,el,hand,2.1,1.8,SLEEVE,6)
    capsule(cv,(hand[0]+1.0,hand[1]+7),(hand[0]-2.5-маха*0.6,hand[1]-9),1.0,1.0,CANE,6.5)
    capsule(cv,(hand[0]-2.5-маха*0.6,hand[1]-9),(hand[0]+0.3-маха*0.6,hand[1]-10.5),1.0,1.0,CANE,6.6)   # куката горе
    ellipse(cv,hand[0],hand[1]+0.6,1.9,1.9,SKIN,6.8,extra=-0.1)
    # --- лявата ѝ ръка (вдясно на екрана): протегната встрани, държи съседа
    sh=(39.2,28.5+by); el=(44,31.5+by); hand=(48.5,31+by-0.6*math.sin(t))
    capsule(cv,sh,el,2.5,2.2,SLEEVE,6)
    capsule(cv,el,hand,2.1,1.8,SLEEVE,6)
    ellipse(cv,hand[0]+0.4,hand[1]+0.2,1.9,1.9,SKIN,6.8,extra=-0.1)
    # --- глава: усмихната, очите затворени от радост
    hc=(32,18.5+by)
    poly(cv,[(29.5,25.5+by),(34.5,25.5+by),(32,28.5+by)],SLEEVE,5.8,extra=-0.2); деколте(cv,by)
    ellipse(cv,hc[0],hc[1],7.3,7.6,SKIN,6)
    ellipse(cv,hc[0],hc[1]-0.8,7.7,7.4,HAIR,6.5,mask=lambda x,y:(y<hc[1]-3.5) or ((x<hc[0]-5.5 or x>hc[0]+4.5) and y<hc[1]+1))
    ellipse(cv,hc[0],hc[1]-8.6,4.6,3.2,HAIR,6.4,extra=0.15)
    for y in range(int(hc[1]-7),int(hc[1]-4)): cv.plot(31,y,HAIR[2],9,990)
    ey=int(hc[1]+0.5)
    for ex in (28,34):
        for (x,y) in [(ex-1,ey),(ex,ey-1),(ex+1,ey-1),(ex+2,ey),(ex+1,ey+1),(ex,ey+1)]: cv.plot(x,y,FRAME,9,998)
        cv.plot(ex,ey,EYE,9,997); cv.plot(ex+1,ey,EYE,9,997)          # затворени очи (дъгички)
        cv.plot(ex,ey-3,HAIR[3],9,993); cv.plot(ex+1,ey-3,HAIR[3],9,993)
    cv.plot(31,ey,FRAME,9,998); cv.plot(32,ey,FRAME,9,998)
    cv.plot(31,ey+2,SKIN[2],9,996); cv.plot(32,ey+2,SKIN[2],9,996)
    for x in (30,31,32,33): cv.plot(x,ey+4,MOUTH,9,995)              # широка усмивка
    cv.plot(31,ey+5,hx('#5a2a24'),9,995); cv.plot(32,ey+5,hx('#5a2a24'),9,995)
    cv.plot(29,ey+3,MOUTH,9,995); cv.plot(34,ey+3,MOUTH,9,995)
    cv.plot(27,ey+3,BLUSH,9,994); cv.plot(36,ey+3,BLUSH,9,994); cv.plot(27,ey+2,BLUSH,9,994); cv.plot(36,ey+2,BLUSH,9,994)
    return облечи(finish(cv,OUT))


def sit(посока, кадър):
    """Сядане: кадри 0-1 = сяда (наполовина, седнала), 2-3 = седи. посока: down, up, right."""
    седи=[0.5,1.0,1.0,1.0][кадър]
    if посока=="down":
        return front(0, False, седи)
    if посока=="up":
        return front(0, True, седи)
    return side(0, cane_near=False, седи=седи)

# Малък "художник" за пиксел арт: части с обем (4 тона), контури и стави.
# Ползва се от baba.py. Без външни библиотеки.
import math

def hx(h):
    h=h.lstrip('#'); return (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16),255)

LIGHT=(-0.62,-0.78)   # светлината идва горе вляво

class Canvas:
    def __init__(s,w=64,h=64):
        s.w,s.h=w,h
        s.col=[[None]*w for _ in range(h)]
        s.part=[[None]*w for _ in range(h)]
        s.z=[[-1e9]*w for _ in range(h)]
        s.n=0
    def plot(s,x,y,c,z,pid):
        if 0<=x<s.w and 0<=y<s.h and z>=s.z[y][x]:
            s.col[y][x]=c; s.z[y][x]=z; s.part[y][x]=pid
    def newid(s):
        s.n+=1; return s.n

def tone(mat,b):
    # mat = (hi, light, mid, dark)
    if b>0.50: return mat[0]
    if b>0.08: return mat[1]
    if b>-0.38: return mat[2]
    return mat[3]

def bright(nx,ny,extra=0.0):
    r2=nx*nx+ny*ny
    return (nx*LIGHT[0]+ny*LIGHT[1])*0.9-0.30*r2+extra

def ellipse(cv,cx,cy,rx,ry,mat,z,mask=None,extra=0.0,pid=None):
    pid=pid or cv.newid()
    for y in range(int(cy-ry)-1,int(cy+ry)+2):
        for x in range(int(cx-rx)-1,int(cx+rx)+2):
            nx=(x+0.5-cx)/rx; ny=(y+0.5-cy)/ry
            if nx*nx+ny*ny<=1 and (mask is None or mask(x,y)):
                cv.plot(x,y,tone(mat,bright(nx,ny,extra)),z,pid)
    return pid

def capsule(cv,p0,p1,r0,r1,mat,z,extra=0.0,pid=None):
    pid=pid or cv.newid()
    (x0,y0),(x1,y1)=p0,p1
    dx,dy=x1-x0,y1-y0; L2=dx*dx+dy*dy or 1e-6
    rm=max(r0,r1)
    for y in range(int(min(y0,y1)-rm)-1,int(max(y0,y1)+rm)+2):
        for x in range(int(min(x0,x1)-rm)-1,int(max(x0,x1)+rm)+2):
            px,py=x+0.5,y+0.5
            t=max(0,min(1,((px-x0)*dx+(py-y0)*dy)/L2))
            cx,cy=x0+t*dx,y0+t*dy; r=r0+(r1-r0)*t
            ox,oy=px-cx,py-cy
            if ox*ox+oy*oy<=r*r:
                cv.plot(x,y,tone(mat,bright(ox/r,oy/r,extra)),z,pid)
    return pid

def poly(cv,pts,mat,z,extra=0.0,pid=None,folds=()):
    """Многоъгълник с обем по хоризонтала (за пола, престилка)."""
    pid=pid or cv.newid()
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    for y in range(int(min(ys)),int(max(ys))+1):
        py=y+0.5; xsect=[]
        n=len(pts)
        for i in range(n):
            (ax,ay),(bx,by)=pts[i],pts[(i+1)%n]
            if (ay<=py<by) or (by<=py<ay):
                xsect.append(ax+(py-ay)*(bx-ax)/(by-ay))
        xsect.sort()
        for i in range(0,len(xsect)-1,2):
            l,r=xsect[i],xsect[i+1]
            for x in range(int(round(l)),int(round(r))):
                nx=((x+0.5)-(l+r)/2)/max(1,(r-l)/2)
                ny=((py-min(ys))/max(1,(max(ys)-min(ys))))*2-1
                b=bright(nx,ny*0.4,extra)
                for fx,depth in folds:
                    if abs((x+0.5)-fx(y))<0.8: b-=depth
                cv.plot(x,y,tone(mat,b),z,pid)
    return pid

def finish(cv,outline,inner=True):
    out=[row[:] for row in cv.col]
    for y in range(cv.h):
        for x in range(cv.w):
            if cv.col[y][x] is None:
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    X,Y=x+dx,y+dy
                    if 0<=X<cv.w and 0<=Y<cv.h and cv.col[Y][X] is not None:
                        out[y][x]=outline; break
            elif inner and (cv.part[y][x] or 0)<900:
                # ръб между части: предната част получава тъмен ръб
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    X,Y=x+dx,y+dy
                    if 0<=X<cv.w and 0<=Y<cv.h and cv.part[Y][X] not in (None,cv.part[y][x]) and cv.z[Y][X]<cv.z[y][x]-0.5:
                        out[y][x]=outline; break
    return out

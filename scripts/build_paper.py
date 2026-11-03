#!/usr/bin/env python3
"""A4 academic typesetter. Direct Unicode Yoon text + editable PDF vectors.
Public edition: portable command-line paths; same academic Yoon layout.
Copyright 2026 박성모. SPDX-License-Identifier: Apache-2.0
No fallback font, rasterized text, source-font copying, or external service.
"""
import argparse,json,pathlib,re,hashlib
import fitz
B=pathlib.Path(__file__).resolve().parents[1]
OUT=FONTS=LAYOUT=None
ROLE={'body':'YoonMyungjoPro730','bold':'YoonMyungjoPro760','sans':'YoonGothicPro740','sansbold':'YoonGothicPro760'}
class Paper:
 def __init__(self):
  self.meta={x['postscript']:x for x in json.loads(FONTS.read_text(encoding='utf-8'))}
  self.fonts={k:fitz.Font(fontfile=self.meta[v]['path']) for k,v in ROLE.items()}
  self.doc=fitz.open();self.W=595.2756;self.H=841.8898;self.L=94.9606;self.R=self.W-self.L;self.width=self.R-self.L;self.bottom=766;self.toc=[];self.layout=[];self.newpage()
 def newpage(self):
  self.page=self.doc.new_page(width=self.W,height=self.H)
  for role,name in ROLE.items():self.page.insert_font(fontname=name,fontfile=self.meta[name]['path'])
  self.y=72
 def ensure(self,h):
  if self.y+h>self.bottom:self.newpage()
 def text(self,x,y,s,role='body',size=10.5,color=(0,0,0)):
  missing=[c for c in s if not c.isspace() and not self.fonts[role].has_glyph(ord(c))]
  if missing:raise ValueError(('missing glyph',role,sorted(set(missing))))
  self.page.insert_text((x,y),s,fontname=ROLE[role],fontsize=size,color=color)
  self.layout.append({'page':self.page.number+1,'x':x,'baseline':y,'text':s,'role':role,'size':size})
 def wrap(self,s,width,size=10.5,role='body'):
  out=[]
  for paragraph in s.split('\n'):
   words=paragraph.split(' ');line=''
   for word in words:
    cand=(line+' '+word).strip()
    if self.fonts[role].text_length(cand,fontsize=size)<=width:line=cand;continue
    if line:out.append(line);line=''
    while self.fonts[role].text_length(word,fontsize=size)>width:
     n=max(1,int(width/size))
     while n<len(word) and self.fonts[role].text_length(word[:n+1],fontsize=size)<=width:n+=1
     while self.fonts[role].text_length(word[:n],fontsize=size)>width:n-=1
     out.append(word[:n]);word=word[n:]
    line=word
   out.append(line)
  return out
 def para(self,s,role='body',size=10.5,leading=15.5,inset=0,gap=7):
  lines=self.wrap(s,self.width-2*inset,size,role)
  if size<=9.5 and len(lines)<=8:self.ensure(len(lines)*leading+2)
  while lines:
   available=int((self.bottom-self.y-2)/leading)
   if available<2 and len(lines)>available:self.newpage();continue
   count=min(available,len(lines))
   if len(lines)>count and len(lines)-count==1:count-=1
   if count<=0:self.newpage();continue
   for line in lines[:count]:
    self.text(self.L+inset,self.y+size,line,role,size);self.y+=leading
   lines=lines[count:]
   if lines:self.newpage()
  self.y+=gap
 def heading(self,s,level=1):
  if s=='English Abstract':self.ensure(345)
  size=12.5 if level==1 else 10.8;self.ensure(112 if level==1 else 72);self.y+=10 if level==1 else 5
  self.text(self.L,self.y+size,s,'bold',size);self.toc.append([level,s,len(self.doc)]);self.y+=size+12
 def centered(self,s,role='body',size=10.5):
  self.text((self.W-self.fonts[role].text_length(s,fontsize=size))/2,self.y+size,s,role,size);self.y+=size+5
 def title(self,meta):
  self.page.draw_line((self.L,72),(self.R,72),color=(0,0,0),width=3.4);self.y=91
  for line in meta['title']:self.centered(line,'bold',18.5)
  self.y+=6;self.page.draw_line((self.L,self.y),(self.R,self.y),color=(0,0,0),width=.8);self.y+=18
  for line in meta['english_title']:self.centered(line,'body',11.2)
  self.y+=13;self.centered('박성모','bold',11.5);self.centered('vividsaebom@gmail.com','body',10.1);self.y+=13
  self.centered('초록','bold',11.3);self.y+=5;self.para(meta['abstract'],inset=25,size=10,leading=14.6,gap=9)
  self.para('주제어: '+meta['keywords'],size=9.2,leading=13,inset=25,gap=13)
 def table(self,caption,headers,rows,ratios=None,note=None):
  self.ensure(75);self.para(caption,'body',9.5,13,gap=6)
  widths=[self.width*r/sum(ratios or [1]*len(headers)) for r in (ratios or [1]*len(headers))]
  def row(values,head=False):
   role='sansbold' if head else 'sans';size=8.6 if len(headers)>4 else 9.1;lead=12.5
   lines=[self.wrap(str(v),w-9,size,role) for v,w in zip(values,widths)];h=max(map(len,lines))*lead+11
   if self.y+h>self.bottom:
    self.newpage();self.text(self.L,self.y+9,caption+' (계속)','body',9);self.y+=22;row(headers,True)
   x=self.L
   for ls,w in zip(lines,widths):
    for j,line in enumerate(ls):self.text(x+4,self.y+8+size+j*lead,line,role,size)
    x+=w
   self.y+=h
   if head:self.page.draw_line((self.L,self.y),(self.R,self.y),color=(0,0,0),width=.4)
  self.page.draw_line((self.L,self.y),(self.R,self.y),color=(0,0,0),width=.8);row(headers,True)
  for i,r in enumerate(rows):
   if len(rows)-i==2:
    size=8.6 if len(headers)>4 else 9.1
    two=sum(max(len(self.wrap(str(v),w-9,size,'sans')) for v,w in zip(rr,widths))*12.5+11 for rr in rows[i:])
    if self.y+two>self.bottom:self.y=self.bottom+1
   row(r)
  self.page.draw_line((self.L,self.y),(self.R,self.y),color=(0,0,0),width=.8);self.y+=7
  if note:self.para(note,size=9,leading=12.6,gap=9)
  else:self.y+=7
 def boxtext(self,rect,lines,fill):
  self.page.draw_rect(rect,fill=fill,color=(.18,.18,.18),width=.5)
  for i,s in enumerate(lines):
   role='sansbold' if i==0 else 'sans';size=9.3 if i==0 else 8.7
   w=self.fonts[role].text_length(s,fontsize=size);self.text(rect.x0+(rect.width-w)/2,rect.y0+19+i*15,s,role,size)
 def architecture(self,caption):
  self.ensure(207);top=self.y+4;gap=17;w=(self.width-2*gap)/3;h=65
  boxes=[('입력·정책',['양력/음력 · 윤달','시각 · 경도 · 야자시'],(.94,.93,.98)),('결정론적 계산',['내장 역법 DB','시간 미상 후보 집합'],(.91,.95,.98)),('로컬 언어모델',['계산값 + 상태 전달','A / B / C 비교'],(.94,.96,.90))]
  for i,(title,ls,color) in enumerate(boxes):
   x=self.L+i*(w+gap);self.boxtext(fitz.Rect(x,top,x+w,top+h),[title]+ls,color)
   if i<2:self.text(x+w+3,top+36,'→','sans',12)
  y=top+90;self.boxtext(fitz.Rect(self.L,y,self.L+w,y+h),['공식 자료 대조','KASI 확정판 역서','계산 정확성 감사'],(.98,.94,.88))
  self.boxtext(fitz.Rect(self.L+w+gap,y,self.L+2*w+gap,y+h),['필드 검증 D','같은 C 출력 재사용','일치 전달 / 전체 보류'],(.97,.91,.91))
  self.boxtext(fitz.Rect(self.L+2*w+2*gap,y,self.R,y+h),['증거 보존','원시 응답·실패 포함','요청·소스 SHA-256'],(.94,.94,.94))
  self.page.draw_line((self.L+w/2,top+h),(self.L+w/2,y),color=(.3,.3,.3),width=.5)
  self.page.draw_line((self.R-w/2,top+h),(self.L+1.5*w+gap,y),color=(.3,.3,.3),width=.5)
  self.y=y+h+10;self.para(caption,size=9.2,leading=13,gap=8)
 def bars(self,caption,values,total):
  self.ensure(170);start=self.y+10;barleft=self.L+60;bw=self.width-120
  for i,(name,v) in enumerate(values):
   y=start+i*28;self.text(self.L,y+10,name,'sansbold',9.6)
   self.page.draw_rect(fitz.Rect(barleft,y,barleft+bw,y+13),fill=(.93,.93,.93),color=None)
   if v:self.page.draw_rect(fitz.Rect(barleft,y,barleft+bw*v/total,y+13),fill=(.25,.37,.47),color=None)
   self.text(barleft+bw+8,y+10,f'{v}/{total}','sans',9.3)
  self.y=start+len(values)*28+10;self.para(caption,size=9.2,leading=13,gap=8)
 def equation(self,s):
  self.ensure(43);self.y+=5;self.centered(s,'body',11);self.y+=12
 def finish(self,meta):
  for i,p in enumerate(self.doc):
   self.page=p
   self.text(self.W/2-3,self.H-39,str(i+1),'body',9)
  self.doc.set_metadata({'title':' '.join(meta['title']),'author':'박성모 <vividsaebom@gmail.com>','subject':'Local Saju LLM: implementation audit and measured fact preservation','creator':'Public research typesetter; licensed Yoon fonts','keywords':meta['keywords']})
  self.doc.set_toc(self.toc);self.doc.subset_fonts()
  # Yoon's cmap has Unicode aliases for identical glyphs. Restore the source
  # characters in PDF ToUnicode only; never alter font programs or glyph codes.
  original=''.join(x['text'] for x in self.layout)
  aliases={'30fb':'00b7','22ef':'2026','f971':'8fb0'}
  assert all(chr(int(k,16)) not in original for k in aliases)
  seen=set()
  for page in self.doc:
   for font in page.get_fonts():
    kind,value=self.doc.xref_get_key(font[0],'ToUnicode')
    if kind!='xref':continue
    xref=int(value.split()[0])
    if xref in seen:continue
    seen.add(xref);stream=self.doc.xref_stream(xref).decode('ascii')
    for src,dst in aliases.items():
     stream=re.sub(r'(?mi)^(<[0-9a-f]+>)[ \t]+<'+src+r'>$' ,lambda m:m[1]+' <'+dst+'>',stream)
    self.doc.update_stream(xref,stream.encode('ascii'))
  OUT.parent.mkdir(parents=True,exist_ok=True);self.doc.save(OUT,garbage=4,deflate=True)
  LAYOUT.write_text(json.dumps(self.layout,ensure_ascii=False,indent=2),encoding='utf-8');print(OUT,len(self.doc),'pages')
def main():
 global B,OUT,FONTS,LAYOUT
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--manuscript',type=pathlib.Path,default=B/'manuscript.json')
 parser.add_argument('--fonts',type=pathlib.Path,required=True,help='Local font metadata JSON; never publish activation paths or font programs')
 parser.add_argument('--output',type=pathlib.Path,required=True)
 parser.add_argument('--layout',type=pathlib.Path)
 args=parser.parse_args();B=args.manuscript.resolve().parent;OUT=args.output.resolve();FONTS=args.fonts.resolve()
 LAYOUT=args.layout.resolve() if args.layout else OUT.with_suffix('.layout.json')
 LAYOUT.parent.mkdir(parents=True,exist_ok=True)
 m=json.loads(args.manuscript.read_text(encoding='utf-8'));p=Paper();p.title(m)
 for b in m['blocks']:
  k=b['type']
  if k=='h1':p.heading(b['text'])
  elif k=='h2':p.heading(b['text'],2)
  elif k=='p':p.para(b['text'])
  elif k=='small':p.para(b['text'],size=9.2,leading=13,gap=6)
  elif k=='table':p.table(b['caption'],b['headers'],b['rows'],b.get('ratios'),b.get('note'))
  elif k=='architecture':p.architecture(b['caption'])
  elif k=='bars':p.bars(b['caption'],b['values'],b['total'])
  elif k=='equation':p.equation(b['text'])
  elif k=='page':p.newpage()
  else:raise ValueError(k)
 p.finish(m)
if __name__=='__main__':main()

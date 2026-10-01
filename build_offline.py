import base64,json,re,random
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance

SRC=Path("code_artifact.html"); OUT=Path("dist/index.html"); AD=Path("build_assets")
AD.mkdir(exist_ok=True); OUT.parent.mkdir(exist_ok=True)
W,H=1280,720

def rgb(h):
    h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def mix(a,b,t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))
def bg(top,bottom):
    im=Image.new("RGB",(W,H)); d=ImageDraw.Draw(im); a,b=rgb(top),rgb(bottom)
    for y in range(H): d.line((0,y,W,y),fill=mix(a,b,y/(H-1)))
    return im
def stars(im,n,seed):
    d=ImageDraw.Draw(im,"RGBA"); r=random.Random(seed)
    for _ in range(n):
        x=r.randrange(W); y=r.randrange(430); s=r.choice((1,1,1,2))
        d.ellipse((x-s,y-s,x+s,y+s),fill=(255,240,190,r.randrange(50,170)))
def mountains(im,y,seed,c=(25,28,35),count=8):
    d=ImageDraw.Draw(im,"RGBA"); r=random.Random(seed); pts=[(-50,H)]
    step=W//count
    for i in range(count+1): pts.append((i*step-50,y-r.randint(50,150)))
    pts += [(W+50,H),(0,H)]; d.polygon(pts,fill=(*c,245))
def city(im,y,seed,c=(15,18,24)):
    d=ImageDraw.Draw(im,"RGBA"); r=random.Random(seed); x=-20
    while x<W+30:
        w=r.randint(45,105); h=r.randint(60,210)
        d.rectangle((x,y-h,x+w,y),fill=(*c,240))
        if r.random()<.3: d.rectangle((x+w*.35,y-h-r.randint(20,60),x+w*.65,y-h),fill=(*c,240))
        x+=w+r.randint(8,25)
def crowd(im,y,n,seed,c=(5,7,9)):
    d=ImageDraw.Draw(im,"RGBA"); r=random.Random(seed)
    for _ in range(n):
        x=r.randrange(W); h=r.randint(70,155); w=max(5,int(h*.22))
        d.ellipse((x-w//2,y-h,x+w//2,y-h+w),fill=(*c,230))
        d.polygon((x-w,y-h+w,x+w,y-h+w,x+w*2,y,x-w*2,y),fill=(*c,220))
def person(im,x,y,h=260,c=(3,5,8),cape=False):
    d=ImageDraw.Draw(im,"RGBA"); head=max(10,int(h*.15)); bw=max(18,int(h*.28))
    d.ellipse((x-head//2,y-h,x+head//2,y-h+head),fill=(*c,245))
    d.polygon((x-bw//2,y-h+head,x+bw//2,y-h+head,x+int(h*.22),y,x-int(h*.22),y),fill=(*c,245))
    if cape: d.polygon((x-int(h*.23),y-h+head,x+int(h*.23),y-h+head,x+int(h*.58),y,x-int(h*.58),y),fill=(*c,190))
def fire(im,base,seed):
    d=ImageDraw.Draw(im,"RGBA"); r=random.Random(seed)
    for _ in range(55):
        x=r.randrange(W); w=r.randint(18,80); h=r.randint(60,220)
        pts=[(x-w//2,base),(x-w//3,base-h//2),(x-r.randint(3,max(4,w//5)),base-h),(x+r.randint(3,max(4,w//5)),base-h//3),(x+w//2,base)]
        d.polygon(pts,fill=(190+r.randint(0,55),30+r.randint(0,70),10,r.randint(70,180)))
def beams(im,color=(240,250,255),n=9,spread=520):
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov,"RGBA")
    for i in range(n):
        t=(i-(n-1)/2)/max(1,(n-1)/2); x=W//2+int(t*spread)
        d.polygon([(W//2,0),(x-50,H),(x+50,H)],fill=(*color,45))
    ov=ov.filter(ImageFilter.GaussianBlur(9))
    return Image.alpha_composite(im.convert("RGBA"),ov).convert("RGB")
def gate(im,jannah=True):
    d=ImageDraw.Draw(im,"RGBA"); x=W//2; y=410; glow=(70,220,170) if jannah else (180,100,45)
    d.ellipse((x-340,y-210,x+340,y+230),fill=(*glow,20))
    d.rectangle((x-260,y-150,x+260,y+170),fill=(88,78,64,235))
    d.ellipse((x-235,y-130,x+235,y+175),outline=(*glow,220),width=12)
    d.rectangle((x-120,y-120,x+120,y+175),fill=(7,10,13,255)); d.ellipse((x-85,y-112,x+85,y-5),fill=(*glow,145))

def scene_image(title,event,sid):
    t=title+" "+event; r=random.Random(1000+sid*77); im=bg("#0a1020","#352315"); stars(im,90,sid)
    if any(k in t for k in ["الجنة","الفردوس","باب الجنة","النعيم","أنهار","قصور","رؤية وجه الله"]):
        im=bg("#0b2b31","#285641"); gate(im,True); im=beams(im,(190,255,235),11,560)
        d=ImageDraw.Draw(im,"RGBA"); d.polygon([(0,H),(180,520),(450,545),(760,475),(W,530),(W,H)],fill=(50,145,155,190))
        for _ in range(120):
            x=r.randrange(W); y=r.randrange(350,H-25); s=r.randint(3,9); d.ellipse((x-s,y-s,x+s,y+s),fill=(70,170+r.randrange(70),100,150))
        for x in (260,455,825,1030): person(im,x,650,r.randint(150,205),(4,10,10))
    elif any(k in t for k in ["جهنم","النار","إبليس","الجحيم","السعير","العذاب"]):
        im=bg("#3b0807","#090204"); fire(im,610,sid); crowd(im,650,90,sid)
        if "إبليس" in t: person(im,W//2,620,300,(2,2,4),True)
    elif any(k in t for k in ["الصراط","القنطرة","الميزان","الحشر","القيامة","الموقف","الشفاعة"]):
        im=bg("#0d1220","#473223"); mountains(im,500,sid); im=beams(im,(255,235,200),10,500); crowd(im,635,95,sid)
        d=ImageDraw.Draw(im,"RGBA")
        if "الصراط" in t:
            d.polygon([(90,505),(W-90,455),(W-65,482),(115,535)],fill=(75,72,70,245)); fire(im,680,sid+2)
        if "الميزان" in t:
            x=W//2; d.line((x,250,x,590),fill=(205,170,95,240),width=11); d.line((x,330,x-180,415),fill=(205,170,95,240),width=9); d.line((x,330,x+180,415),fill=(205,170,95,240),width=9)
            d.ellipse((x-250,405,x-95,465),outline=(205,170,95,240),width=7); d.ellipse((x+95,405,x+250,465),outline=(205,170,95,240),width=7)
    elif any(k in t for k in ["الدجال","المهدي","عيسى","يأجوج","دابة","دخان","ريح","زلازل","خسف","طلوع الشمس","الشمس من مغرب","النفخ","البعث","القبر"]):
        im=bg("#0b1120","#5a3821")
        if "الدجال" in t:
            city(im,520,sid); person(im,int(W*.56),620,330,(3,5,8),True)
            d=ImageDraw.Draw(im,"RGBA"); d.ellipse((910,90,1090,270),fill=(255,150,80,180))
        elif "المهدي" in t:
            mountains(im,485,sid); city(im,525,sid+1); crowd(im,625,60,sid); person(im,W//2,610,300,(4,6,9),True)
        elif "يأجوج" in t:
            mountains(im,510,sid,count=7,c=(25,30,37)); d=ImageDraw.Draw(im,"RGBA"); d.rectangle((360,315,920,535),fill=(75,71,64,215)); crowd(im,655,65,sid+1)
        elif "دابة" in t:
            mountains(im,500,sid); person(im,W//2,620,285,(4,4,7),True)
        elif "ريح" in t:
            im=bg("#233944","#c8aa73"); mountains(im,520,sid,c=(42,43,45)); d=ImageDraw.Draw(im,"RGBA")
            for yy in range(190,530,42): d.arc((80,yy-80,1200,yy+120),190,350,fill=(245,245,235,65),width=10)
        elif "دخان" in t:
            im=bg("#1a1a20","#08090c"); fire(im,610,sid); sm=Image.new("RGBA",(W,H),(90,90,90,90)); sm=sm.filter(ImageFilter.GaussianBlur(35)); im=Image.alpha_composite(im.convert("RGBA"),sm).convert("RGB")
        elif "طلوع الشمس" in t or "الشمس من مغرب" in t:
            im=bg("#11192a","#6d3618"); d=ImageDraw.Draw(im,"RGBA"); x=245 if "مغرب" in t else 1035; d.ellipse((x-115,320,x+115,550),fill=(255,180,85,235)); mountains(im,535,sid)
        elif "النفخ" in t:
            im=bg("#050914","#4b281a"); im=beams(im,(255,225,190),13,700); crowd(im,650,100,sid)
        elif "القبر" in t:
            im=bg("#080b14","#3c2b20"); d=ImageDraw.Draw(im,"RGBA"); d.ellipse((330,390,950,760),fill=(10,9,9,250),outline=(185,135,75,120),width=5); im=beams(im,(180,220,245),7,300)
        else:
            mountains(im,500,sid); crowd(im,640,70,sid)
    elif any(k in t for k in ["الكعبة","مكة","المدينة","المسجد"]):
        im=bg("#0c1729","#725136"); city(im,525,sid); d=ImageDraw.Draw(im,"RGBA")
        if "الكعبة" in t:
            d.rectangle((555,335,725,520),fill=(12,12,12,255)); d.rectangle((525,420,755,458),fill=(220,190,105,175))
            for rr in range(260,70,-28): d.ellipse((640-rr,390-rr//4,640+rr,390+rr//4),outline=(235,205,155,35),width=7)
        else:
            d.polygon([(550,500),(640,300),(730,500)],fill=(45,50,60,235)); d.rectangle((520,430,760,505),fill=(32,38,48,235))
        crowd(im,610,80,sid)
    else:
        mountains(im,500,sid); person(im,W//2,640,275,(4,6,9),True)
    im=ImageEnhance.Contrast(im).enhance(1.08).filter(ImageFilter.GaussianBlur(.18))
    p=AD/f"scene_{sid}.webp"; im.save(p,"WEBP",quality=82,method=6); return p

src=SRC.read_text(encoding="utf-8")
blocks=re.findall(r'(?s)\{\s*id:\s*(\d+).*?visualPlan:\s*\{(.*?)\}\s*,\s*svgTheme:',src)
scenes={}
for sid,block in blocks:
    tm=re.search(r'title:\s*"((?:\\.|[^"])*)"',block); em=re.search(r'event:\s*"((?:\\.|[^"])*)"',block)
    if tm and em: scenes[int(sid)]=(tm.group(1),em.group(1))
if len(scenes)!=32: raise RuntimeError(f"Parsed {len(scenes)} scenes, expected 32")
imgs={}
for sid in sorted(scenes):
    p=scene_image(*scenes[sid],sid); imgs[sid]="data:image/webp;base64,"+base64.b64encode(p.read_bytes()).decode()
js="const sceneImages = "+json.dumps(imgs,separators=(",",":"))+";\\n"
src=src.replace("<script>","<script>\\n"+js,1)
src=src.replace("document.getElementById('sceneSvgContainer').innerHTML = generateSceneSvg(scene.svgTheme, scene.visualPlan.title);","document.getElementById('sceneSvgContainer').innerHTML = '<img src=\"' + sceneImages[scene.id] + '\" alt=\"\" draggable=\"false\">';")
needle="$"+"{generateSceneSvg(scene.svgTheme, scene.visualPlan.title)}"
repl="<img src=\""+("$"+"{sceneImages[scene.id]}")+"\" alt=\"\" draggable=\"false\">"
src=src.replace(needle,repl)
src=src.replace(".scene-art-wrapper svg {",".scene-art-wrapper img {").replace(".book-scene-img-wrap svg {",".book-scene-img-wrap img {")
src=src.replace("</body>","<!-- OFFLINE BUILD: 32 new raster WebP scene images embedded as data URIs. -->\\n</body>")
OUT.write_text(src,encoding="utf-8")
print("OK",OUT.stat().st_size,"bytes",len(imgs),"embedded images")

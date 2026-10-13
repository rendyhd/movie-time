"""Build the checked assembly guide as PDF and matching Markdown."""
from pathlib import Path
import sys,re,html,json,hashlib,shutil
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether,Preformatted
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader
from matplotlib import get_data_path
from content import PAGES
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/Movie_Time_Assembly_and_Wiring.pdf'
# DejaVu ships with matplotlib, so the guide builds without a system font install.
FONT=Path(get_data_path())/'fonts/ttf'
for name,file in [('Guide','DejaVuSans.ttf'),('GuideBold','DejaVuSans-Bold.ttf'),('GuideItalic','DejaVuSans-Oblique.ttf'),('GuideMono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('Guide',normal='Guide',bold='GuideBold',italic='GuideItalic',boldItalic='GuideBold')
INK=colors.HexColor('#293e42');GREEN=colors.HexColor('#547b50');BG=colors.HexColor('#f7f4ec')
ST={
    'p':ParagraphStyle('Body',fontName='Guide',fontSize=10.1,leading=13.6,textColor=INK,spaceAfter=8),
    'h':ParagraphStyle('Heading',fontName='GuideBold',fontSize=12.2,leading=16,textColor=GREEN,spaceBefore=5,spaceAfter=7),
    'caption':ParagraphStyle('Caption',fontName='Guide',fontSize=8.4,leading=11,textColor=colors.HexColor('#65736c'),spaceAfter=10),
    'cell':ParagraphStyle('Cell',fontName='Guide',fontSize=9.2,leading=12,textColor=INK),
    'head':ParagraphStyle('Head',fontName='GuideBold',fontSize=9.2,leading=12,textColor=colors.white),
    'code':ParagraphStyle('Code',fontName='GuideMono',fontSize=9.7,leading=14,textColor=INK,leftIndent=10,spaceBefore=4,spaceAfter=12),
}
W,H=A4;M=42;WIDTH=W-2*M

def paragraph(text,style='p'):return Paragraph(text,ST[style])

def as_markdown(text):
    text=re.sub(r'<link href="([^"]+)">(.+?)</link>',r'[\2](\1)',text)
    text=text.replace('<b>','**').replace('</b>','**').replace('<br/>','\n')
    return html.unescape(text)

def header(c,doc):
    index=doc.page-1
    c.saveState();c.setFillColor(GREEN);c.rect(0,H-7,W,7,fill=1,stroke=0)
    c.setFillColor(INK);c.setFont('GuideBold',23)
    title=PAGES[index]['title'] if index<len(PAGES) else 'Layout overflow'
    c.bookmarkPage('page-'+str(doc.page));c.addOutlineEntry(title,'page-'+str(doc.page),level=0)
    c.drawString(M,H-46,title)
    c.setFont('Guide',8.6);c.setFillColor(colors.HexColor('#65736c'))
    subtitle=PAGES[index]['subtitle'] if index<len(PAGES) else ''
    c.drawString(M,H-66,subtitle)
    c.setStrokeColor(colors.HexColor('#d4dacf'));c.line(M,33,W-M,33)
    c.setFont('Guide',8);c.drawString(M,20,'MOVIE TIME  |  Measured switches + reinforced PETG leaf')
    c.drawRightString(W-M,20,f'{doc.page} / {len(PAGES)}')
    c.restoreState()

def run():
    story=[];md=['# Movie Time - final assembly and wiring guide','',
                'Printable version: [Assembly and wiring PDF](output/pdf/Movie_Time_Assembly_and_Wiring.pdf).',
                'Print files: [output/final_version/plates](output/final_version/plates). See the [hardware README](README.md) for what to print.','']
    for i,page in enumerate(PAGES):
        if i:story.append(PageBreak())
        md += ['## '+page['title'],'',page['subtitle'],''];counter=0
        for block in page['blocks']:
            kind=block[0]
            if kind in ('p','h'):
                story.append(paragraph(block[1],kind));md += [('### ' if kind=='h' else '')+as_markdown(block[1]),'']
            elif kind=='note':
                box=Table([[paragraph(block[1])]],colWidths=[WIDTH])
                box.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#eaf0e5')),
                                         ('BOX',(0,0),(-1,-1),.7,colors.HexColor('#b9c9b0')),
                                         ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
                                         ('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
                story += [box,Spacer(1,10)];md += [as_markdown(block[1]),'']
            elif kind=='table':
                heads,rows,widths=block[1:]
                data=[[paragraph(t,'head') for t in heads]]+[[paragraph(t,'cell') for t in row] for row in rows]
                widths=[v/sum(widths)*WIDTH for v in widths]
                tab=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
                tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),GREEN),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f2ec'),colors.white]),
                    ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),
                    ('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),
                    ('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.5,GREEN)]))
                story += [tab,Spacer(1,10)]
                md += ['| '+' | '.join(heads)+' |','|'+'|'.join(['---']*len(heads))+'|']
                md += ['| '+' | '.join(as_markdown(t) for t in row)+' |' for row in rows];md.append('')
            elif kind=='steps':
                for text in block[1]:
                    counter+=1
                    line=Table([[paragraph(f'<b>{counter}.</b>'),paragraph(text)]],colWidths=[23,WIDTH-23])
                    line.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),
                                             ('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),
                                             ('BOTTOMPADDING',(0,0),(-1,-1),3)]))
                    story.append(line);md += [f'{counter}. '+as_markdown(text),'']
            elif kind=='image':
                file,maxh,caption=block[1:];img=Image(str(ROOT/file))
                factor=min(WIDTH/img.imageWidth,maxh/img.imageHeight)
                img.drawWidth=img.imageWidth*factor;img.drawHeight=img.imageHeight*factor
                story += [img,Spacer(1,5),paragraph(caption,'caption')]
                md += [f'![{caption}]({file})','']
            elif kind=='code':
                story.append(Preformatted(block[1],ST['code']));md += ['```yaml',block[1],'```','']
    doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=M,leftMargin=M,topMargin=86,bottomMargin=43,
                          title='Movie Time - Final assembly and wiring',author='Movie Time project',
                          subject='Checked assembly instructions, screws, original tagreader wiring and measured buttons')
    doc.build(story,onFirstPage=header,onLaterPages=header)
    reader=PdfReader(OUT);assert len(reader.pages)==len(PAGES),('page overflow',len(reader.pages),len(PAGES))
    for i,page in enumerate(reader.pages):
        text=page.extract_text();assert PAGES[i]['title'] in text,(i,'missing title')
        assert '\u25a0' not in text,(i,'missing glyph')
    (ROOT/'ASSEMBLY.md').write_text('\n'.join(md))
    report={'pages':len(reader.pages),'file':str(OUT.relative_to(ROOT)),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),
            'physical_tests_complete':False,'hardware_audit':'output/final_version/validation/assembly_audit.json',
            'pdf_text_and_page_count_checked':True,'visual_review_complete':False}
    (ROOT/'output/final_version/validation/assembly_guide.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Built',OUT,'pages',len(reader.pages),'bytes',OUT.stat().st_size)

if __name__=='__main__':run()

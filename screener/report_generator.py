"""
RecruitAI — PDF Report Generator
Uses ReportLab to generate a professional recruitment report.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


# ── Colour palette matching bioluminescent UI ──────────────────
INK       = colors.HexColor('#020408')
GLOW1     = colors.HexColor('#00f5d4')
GLOW2     = colors.HexColor('#00c9a7')
BIO1      = colors.HexColor('#7affde')
AMBER     = colors.HexColor('#ffb830')
ROSE      = colors.HexColor('#ff4d7e')
LIME      = colors.HexColor('#b8ffb8')
TEXT      = colors.HexColor('#d4f0ec')
DIM       = colors.HexColor('#4a7a72')
DIMMER    = colors.HexColor('#2a4a44')
WHITE     = colors.white
DARK_PANEL = colors.HexColor('#050d12')


def _styles():
    """Return custom paragraph styles."""
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        'ReportTitle',
        fontSize=28,
        textColor=WHITE,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=4,
        letterSpacing=2,
    )
    subtitle = ParagraphStyle(
        'ReportSubtitle',
        fontSize=10,
        textColor=GLOW1,
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=2,
    )
    section = ParagraphStyle(
        'Section',
        fontSize=8,
        textColor=GLOW1,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceAfter=6,
        spaceBefore=14,
        letterSpacing=1.5,
    )
    body = ParagraphStyle(
        'Body',
        fontSize=9,
        textColor=TEXT,
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=4,
        leading=14,
    )
    small = ParagraphStyle(
        'Small',
        fontSize=7.5,
        textColor=DIM,
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceAfter=2,
    )
    right = ParagraphStyle(
        'Right',
        fontSize=8,
        textColor=DIM,
        fontName='Helvetica',
        alignment=TA_RIGHT,
    )
    return {
        'title': title, 'subtitle': subtitle, 'section': section,
        'body': body, 'small': small, 'right': right,
    }


def _score_color(score_pct):
    """Return color based on score percentage."""
    if score_pct >= 75:
        return BIO1
    elif score_pct >= 50:
        return GLOW1
    else:
        return ROSE


def _status_color(status):
    status_map = {
        'shortlisted': LIME,
        'review':      GLOW1,
        'pending':     AMBER,
        'rejected':    ROSE,
    }
    return status_map.get(status, DIM)


def generate_pdf_report(job, candidates, user):
    """
    Generate a PDF recruitment report for a job posting.
    Returns bytes that can be sent as HTTP response.
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=18*mm,
        bottomMargin=18*mm,
    )

    s = _styles()
    story = []
    W = A4[0] - 36*mm  # usable width

    # ── HEADER ────────────────────────────────────────────────
    # Dark header background table
    now = datetime.now().strftime('%d %B %Y, %H:%M')
    header_data = [[
        Paragraph('RECRUITAI', ParagraphStyle(
            'H1', fontSize=22, textColor=GLOW1,
            fontName='Helvetica-Bold', letterSpacing=3)),
        Paragraph(f'Generated: {now}<br/>By: {user.username}',
                  ParagraphStyle('HR', fontSize=7.5, textColor=DIM,
                                 fontName='Helvetica', alignment=TA_RIGHT)),
    ]]
    header_table = Table(header_data, colWidths=[W*0.6, W*0.4])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), INK),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 12),
        ('RIGHTPADDING',  (0,0), (-1,-1), 12),
        ('LINEBELOW', (0,0), (-1,-1), 1, GLOW1),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8*mm))

    # ── JOB INFO ──────────────────────────────────────────────
    story.append(Paragraph('RECRUITMENT REPORT', s['section']))
    story.append(Paragraph(job.title, ParagraphStyle(
        'JobTitle', fontSize=18, textColor=WHITE,
        fontName='Helvetica-Bold', spaceAfter=6)))

    meta_parts = []
    if job.location:
        meta_parts.append(f'📍 {job.location}')
    if job.salary_range:
        meta_parts.append(f'💰 {job.salary_range}')
    meta_parts.append(f'📅 Report: {now}')
    story.append(Paragraph('   |   '.join(meta_parts), s['small']))
    story.append(Spacer(1, 4*mm))

    # ── SUMMARY STATS ─────────────────────────────────────────
    screened   = [c for c in candidates if c.final_score > 0]
    shortlisted = [c for c in candidates if c.status == 'shortlisted']
    avg_score  = (sum(c.score_pct for c in screened) / len(screened)) if screened else 0
    top_score  = screened[0].score_pct if screened else 0

    stats_data = [
        [
            _stat_cell('TOTAL APPLIED', str(len(candidates))),
            _stat_cell('SCREENED',      str(len(screened))),
            _stat_cell('SHORTLISTED',   str(len(shortlisted))),
            _stat_cell('AVG SCORE',     f'{avg_score:.1f}%'),
            _stat_cell('TOP SCORE',     f'{top_score:.1f}%'),
        ]
    ]
    stats_table = Table(stats_data, colWidths=[W/5]*5)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), DARK_PANEL),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('BOX',           (0,0), (-1,-1), 0.5, GLOW2),
        ('INNERGRID',     (0,0), (-1,-1), 0.5, DIMMER),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 6*mm))

    # ── CANDIDATE RANKINGS TABLE ──────────────────────────────
    story.append(Paragraph('CANDIDATE RANKINGS', s['section']))

    if not screened:
        story.append(Paragraph(
            'No candidates have been screened yet. Run AI Screening from the dashboard.',
            s['body']))
    else:
        # Table header
        thead = ['Rank', 'Candidate', 'TF-IDF', 'BERT AI', 'Final Score', 'Skills', 'Status']
        col_w = [12*mm, 40*mm, 20*mm, 20*mm, 24*mm, 48*mm, 22*mm]

        rows = [thead]
        for i, c in enumerate(screened):
            rank_str = ['🥇','🥈','🥉'][i] if i < 3 else f'#{i+1}'
            skills_str = ', '.join(c.skills[:4]) if c.skills else '—'
            if len(c.skills) > 4:
                skills_str += f' +{len(c.skills)-4}'
            rows.append([
                rank_str,
                c.name,
                f'{c.tfidf_pct:.1f}%',
                f'{c.bert_pct:.1f}%',
                f'{c.score_pct}%',
                skills_str,
                c.status.capitalize(),
            ])

        rank_table = Table(rows, colWidths=col_w, repeatRows=1)

        # Build per-row styles
        style_cmds = [
            # Header row
            ('BACKGROUND',    (0,0), (-1,0), INK),
            ('TEXTCOLOR',     (0,0), (-1,0), GLOW1),
            ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,0), 7),
            ('TOPPADDING',    (0,0), (-1,0), 7),
            ('BOTTOMPADDING', (0,0), (-1,0), 7),
            ('LINEBELOW',     (0,0), (-1,0), 0.5, GLOW2),
            # Data rows
            ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE',      (0,1), (-1,-1), 8),
            ('TEXTCOLOR',     (0,1), (-1,-1), TEXT),
            ('TOPPADDING',    (0,1), (-1,-1), 6),
            ('BOTTOMPADDING', (0,1), (-1,-1), 6),
            ('LEFTPADDING',   (0,0), (-1,-1), 6),
            ('RIGHTPADDING',  (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [DARK_PANEL, INK]),
            ('GRID',          (0,0), (-1,-1), 0.3, DIMMER),
            ('BOX',           (0,0), (-1,-1), 0.5, GLOW2),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ]

        # Colour score cells per candidate
        for i, c in enumerate(screened, start=1):
            sc = _score_color(c.score_pct)
            style_cmds.append(('TEXTCOLOR', (4,i), (4,i), sc))
            style_cmds.append(('FONTNAME',  (4,i), (4,i), 'Helvetica-Bold'))
            # Status colour
            stc = _status_color(c.status)
            style_cmds.append(('TEXTCOLOR', (6,i), (6,i), stc))

        rank_table.setStyle(TableStyle(style_cmds))
        story.append(rank_table)

    story.append(Spacer(1, 6*mm))

    # ── TOP 3 DETAILED BREAKDOWN ──────────────────────────────
    top3 = screened[:3]
    if top3:
        story.append(Paragraph('TOP CANDIDATE DETAILS', s['section']))
        for i, c in enumerate(top3):
            medal = ['🥇','🥈','🥉'][i]
            # Candidate name row
            name_data = [[
                Paragraph(f'{medal}  {c.name}', ParagraphStyle(
                    'CName', fontSize=11, textColor=WHITE,
                    fontName='Helvetica-Bold')),
                Paragraph(
                    f'Score: <font color="#{GLOW1.hexval()[2:]}"><b>{c.score_pct}%</b></font>',
                    ParagraphStyle('CScore', fontSize=11, textColor=TEXT,
                                   fontName='Helvetica', alignment=TA_RIGHT)),
            ]]
            name_table = Table(name_data, colWidths=[W*0.7, W*0.3])
            name_table.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,-1), DARK_PANEL),
                ('TOPPADDING',    (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING',   (0,0), (-1,-1), 10),
                ('RIGHTPADDING',  (0,0), (-1,-1), 10),
                ('LINEABOVE',     (0,0), (-1,-1), 1, _score_color(c.score_pct)),
                ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(name_table)

            # Details row
            email_str = c.email or 'N/A'
            skills_str = ', '.join(c.skills) if c.skills else 'None detected'
            missing_str = ', '.join(c.missing_skills) if c.missing_skills else 'None'
            detail_data = [[
                Paragraph(
                    f'<b>Email:</b> {email_str}<br/>'
                    f'<b>TF-IDF:</b> {c.tfidf_pct:.1f}%   '
                    f'<b>BERT:</b> {c.bert_pct:.1f}%   '
                    f'<b>Status:</b> {c.status.capitalize()}',
                    s['small']),
                Paragraph(
                    f'<b>Skills:</b> {skills_str}<br/>'
                    f'<b>Missing:</b> {missing_str}',
                    s['small']),
            ]]
            detail_table = Table(detail_data, colWidths=[W*0.4, W*0.6])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND',    (0,0), (-1,-1), INK),
                ('TOPPADDING',    (0,0), (-1,-1), 7),
                ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                ('LEFTPADDING',   (0,0), (-1,-1), 10),
                ('RIGHTPADDING',  (0,0), (-1,-1), 10),
                ('LINEBELOW',     (0,0), (-1,-1), 0.3, DIMMER),
                ('VALIGN',        (0,0), (-1,-1), 'TOP'),
            ]))
            story.append(detail_table)
            story.append(Spacer(1, 2*mm))

    # ── FOOTER ────────────────────────────────────────────────
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width=W, thickness=0.5, color=GLOW2))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        f'RecruitAI — AI Resume Screening System  |  '
        f'Report for: {job.title}  |  {now}  |  '
        f'Confidential — HR Use Only',
        ParagraphStyle('Footer', fontSize=7, textColor=DIMMER,
                       fontName='Helvetica', alignment=TA_CENTER)))

    # ── BUILD PDF ─────────────────────────────────────────────
    doc.build(story)
    return buffer.getvalue()


def _stat_cell(label, value):
    """Helper to create a stat cell paragraph."""
    return Paragraph(
        f'<font size="7" color="#2a4a44">{label}</font><br/>'
        f'<font size="16" color="#00f5d4"><b>{value}</b></font>',
        ParagraphStyle('Stat', fontName='Helvetica',
                       alignment=TA_CENTER, leading=20))

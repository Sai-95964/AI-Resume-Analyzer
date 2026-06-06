from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO


def generate_report_pdf(analysis: dict) -> bytes:
    """Generate a simple PDF report from analysis dict and return bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elems = []

    title = analysis.get('title', 'Resume Analysis Report')
    elems.append(Paragraph(title, styles['Title']))
    elems.append(Spacer(1, 12))

    # ATS breakdown
    elems.append(Paragraph('ATS Scoring Breakdown', styles['Heading2']))
    ats_details = analysis.get('ats_details') or {}
    if ats_details:
        table_data = [['Component', 'Score']]
        for k, v in ats_details.items():
            table_data.append([str(k), f"{v}"])
        t = Table(table_data, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        elems.append(t)
    else:
        elems.append(Paragraph('No ATS breakdown available.', styles['Normal']))

    elems.append(Spacer(1, 12))

    # Skill gaps
    elems.append(Paragraph('Skill Gaps', styles['Heading2']))
    missing = analysis.get('missing_skills') or []
    if missing:
        for s in missing:
            elems.append(Paragraph(f'• {s}', styles['Normal']))
    else:
        elems.append(Paragraph('No missing skills detected.', styles['Normal']))

    elems.append(Spacer(1, 12))

    # Recommendations
    elems.append(Paragraph('Recommendations', styles['Heading2']))
    recs = analysis.get('recommendations') or []
    if recs:
        for r in recs:
            # r could be dict or string
            text = r.get('message') if isinstance(r, dict) else str(r)
            elems.append(Paragraph(f'• {text}', styles['Normal']))
    else:
        elems.append(Paragraph('No recommendations.', styles['Normal']))

    elems.append(Spacer(1, 12))

    # Resume summary
    elems.append(Paragraph('Resume Summary', styles['Heading2']))
    summary = analysis.get('resume_summary') or analysis.get('llm_insights', {}).get('summary') or ''
    elems.append(Paragraph(summary or 'N/A', styles['Normal']))

    doc.build(elems)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

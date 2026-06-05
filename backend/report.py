from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_report(results: dict, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AI Resume Match Report", styles['Title']))
    story.append(Spacer(1, 0.2*inch))

    data = [
        ["Metric", "Score"],
        ["Overall Match", f"{results.get('final_score', 0)}%"],
        ["Semantic Similarity", f"{results.get('semantic_similarity', 0)}%"],
        ["Skills Coverage", f"{results.get('skills_match_percentage', 0)}%"],
        ["Match Level", results.get('match_level', 'N/A')],
    ]
    table = Table(data, colWidths=[3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#01696f')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f3f0ec')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dcd9d5')),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))

    for title, key in [("✅ Matched Skills", "matched_skills"),
                        ("❌ Missing Skills", "missing_skills")]:
        story.append(Paragraph(title, styles['Heading2']))
        skills = results.get(key, [])
        text = ", ".join(skills) if skills else "None"
        story.append(Paragraph(text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("💡 Improvement Suggestions", styles['Heading2']))
    for tip in results.get('improvement_suggestions', []):
        story.append(Paragraph(f"• {tip}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))

    doc.build(story)

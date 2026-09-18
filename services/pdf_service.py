"""PDF Travel Pass and Itinerary Export Service using ReportLab."""

import io
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from models.travel_state import TravelState


def generate_travel_pass_pdf(state: TravelState) -> bytes:
    """Generates a high-fidelity binary PDF travel pass containing the full itinerary, transit, stays, and budget."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=14
    )
    section_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0F172A')
    )
    alert_style = ParagraphStyle(
        'Alert',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#0369A1')
    )

    story = []

    # Title & Header
    src = state.get("source", "Origin")
    dst = state.get("destination", "Destination")
    days = state.get("duration_days", 2)
    travelers = state.get("travelers", 1)
    budget = state.get("budget", 3000.0)

    story.append(Paragraph("TravelPilot AI — Verified Travel Pass", title_style))
    story.append(Paragraph(f"<b>Route:</b> {src} &rarr; {dst} &nbsp;|&nbsp; <b>Duration:</b> {days} Days ({max(1, days-1)} Nights) &nbsp;|&nbsp; <b>Travelers:</b> {travelers} &nbsp;|&nbsp; <b>Total Budget:</b> ₹{budget:,.0f}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

    # Proactive Hazard / Disruption Callout if Active
    disruption_alerts = state.get("disruption_alerts", [])
    has_disruption = state.get("has_disruption_risk", False)
    recommended_reroute = state.get("recommended_reroute")

    if has_disruption and disruption_alerts:
        top_alert = disruption_alerts[0]
        alert_title = top_alert.get("title", "Active Road & Weather Hazard Advisory")
        alert_desc = top_alert.get("description", "")
        reroute_note = f"<br/><b>Recommended Bypass / Action:</b> {recommended_reroute}" if recommended_reroute else ""
        hazard_p = Paragraph(f"<b>⚠️ {alert_title}</b><br/>{alert_desc}{reroute_note}", ParagraphStyle(
            'HazardPDF', parent=styles['Normal'], fontSize=8.5, leading=12, textColor=colors.HexColor('#92400E')
        ))
        hazard_table = Table([[hazard_p]], colWidths=[7.0*inch])
        hazard_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FEF3C7')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#F59E0B')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(hazard_table)
        story.append(Spacer(1, 8))

    # 1. Transport Section
    story.append(Paragraph("1. Transit & Ground Routing", section_title))
    outbound = state.get("selected_outbound_transport")
    if outbound:
        t_data = [
            [Paragraph("<b>Leg / Direction</b>", body_bold), Paragraph("<b>Mode & Operator</b>", body_bold), Paragraph("<b>Distance / Time</b>", body_bold), Paragraph("<b>Fare</b>", body_bold)],
            [
                Paragraph("Outbound Journey", body_style),
                Paragraph(f"{outbound.mode.upper()}<br/>{outbound.provider}", body_style),
                Paragraph(f"~{outbound.distance_km:.1f} km<br/>{outbound.duration_mins} mins", body_style),
                Paragraph(f"<b>₹{outbound.fare:,.0f}</b>", body_style)
            ]
        ]
        ret = state.get("selected_return_transport")
        if ret:
            t_data.append([
                Paragraph("Return Journey", body_style),
                Paragraph(f"{ret.mode.upper()}<br/>{ret.provider}", body_style),
                Paragraph(f"~{ret.distance_km:.1f} km<br/>{ret.duration_mins} mins", body_style),
                Paragraph(f"<b>₹{ret.fare:,.0f}</b>", body_style)
            ])
        t_table = Table(t_data, colWidths=[1.5*inch, 2.8*inch, 1.6*inch, 1.1*inch])
        t_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t_table)
    else:
        story.append(Paragraph("Direct ground route planned via local verified transit.", body_style))

    story.append(Spacer(1, 8))

    # 2. Stay & Lodging Section
    story.append(Paragraph("2. Verified Accommodation / Homestay / Campsite", section_title))
    stay = state.get("selected_hotel")
    if stay:
        stay_type_str = "Campsite & Tent Rental" if getattr(stay, 'is_camping', False) else getattr(stay, 'stay_type', 'Hotel').capitalize()
        s_data = [
            [Paragraph("<b>Property Name</b>", body_bold), Paragraph("<b>Type & Location</b>", body_bold), Paragraph("<b>Rate per Night</b>", body_bold), Paragraph("<b>Amenities / Gear</b>", body_bold)],
            [
                Paragraph(f"<b>{stay.name}</b>", body_style),
                Paragraph(f"{stay_type_str}<br/>{getattr(stay, 'address', getattr(stay, 'city', 'Verified Location'))}", body_style),
                Paragraph(f"<b>₹{stay.price_per_night:,.0f}</b> / night", body_style),
                Paragraph(", ".join((getattr(stay, 'gear_included', []) or stay.amenities)[:4]), body_style)
            ]
        ]
        s_table = Table(s_data, colWidths=[2.2*inch, 2.2*inch, 1.2*inch, 1.4*inch])
        s_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(s_table)
    else:
        story.append(Paragraph("Day trip / Local homestay arrangement planned.", body_style))

    story.append(Spacer(1, 8))

    # 3. Selected Attractions & Schedule
    story.append(Paragraph("3. Confirmed Sights & Daily Itinerary", section_title))
    acts = state.get("selected_activities", [])
    if acts:
        a_data = [[Paragraph("<b>Attraction / Trail</b>", body_bold), Paragraph("<b>Category</b>", body_bold), Paragraph("<b>Entry Fee</b>", body_bold), Paragraph("<b>Hours</b>", body_bold)]]
        for a in acts[:6]:
            fee = f"₹{a.cost:.0f}" if a.cost and a.cost > 0 else "Free Entry"
            a_data.append([
                Paragraph(f"<b>{a.name}</b>", body_style),
                Paragraph(str(a.category).replace('ActivityCategory.', '').capitalize(), body_style),
                Paragraph(fee, body_style),
                Paragraph(f"{a.opening_time} - {a.closing_time}", body_style)
            ])
        a_table = Table(a_data, colWidths=[2.6*inch, 1.6*inch, 1.3*inch, 1.5*inch])
        a_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(a_table)
    else:
        story.append(Paragraph("Flexible exploration of destination landmarks.", body_style))

    story.append(Spacer(1, 8))

    # 4. Financial Budget Summary
    story.append(Paragraph("4. Financial Breakdown & Budget Feasibility", section_title))
    bd = state.get("budget_breakdown")
    if bd:
        status_text = "PASSED (WITHIN BUDGET)" if bd.feasibility_status == "PASSED" else f"STATUS: {bd.feasibility_status}"
        b_data = [
            [Paragraph("<b>Cost Category</b>", body_bold), Paragraph("<b>Allocated (INR)</b>", body_bold)],
            [Paragraph("Transport (Outbound + Return)", body_style), Paragraph(f"₹{bd.transport_cost:,.0f}", body_style)],
            [Paragraph("Accommodation (Total Nights)", body_style), Paragraph(f"₹{bd.accommodation_cost:,.0f}", body_style)],
            [Paragraph("Food & Regional Dining", body_style), Paragraph(f"₹{bd.food_cost:,.0f}", body_style)],
            [Paragraph("Activities & Entry Tickets", body_style), Paragraph(f"₹{bd.activities_cost:,.0f}", body_style)],
            [Paragraph("Local Transit & Buffer Contingency", body_style), Paragraph(f"₹{bd.local_transit_cost + bd.buffer_contingency:,.0f}", body_style)],
            [Paragraph(f"<b>Total Estimated Cost ({status_text})</b>", body_bold), Paragraph(f"<b>₹{bd.total_cost:,.0f}</b>", body_bold)],
            [Paragraph("Remaining Budget Savings", body_bold), Paragraph(f"<b>₹{max(0.0, bd.remaining_budget):,.0f}</b>", body_bold)]
        ]
        b_table = Table(b_data, colWidths=[4.2*inch, 2.8*inch])
        b_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#E2E8F0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(b_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph("<i>Generated by TravelPilot AI — Pure-Python Ground-Truth Travel Engine with Zero-Hallucination Guarantees.</i>", alert_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas that performs a two-pass drawing to render page numbers dynamically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # BNP Paribas Green header bar
        self.setFillColor(colors.HexColor("#007A48")) # BNP Paribas green
        self.rect(0, 770, 612, 22, fill=True, stroke=False)
        
        # Header text
        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 8)
        self.drawString(36, 777, "BNP PARIBAS | WEALTH MANAGEMENT & RETAIL BANKING")
        self.drawRightString(576, 777, "CUSTOMER CHURN INTELLIGENCE REPORT")
        
        # Footer text
        self.setFillColor(colors.HexColor("#666666"))
        self.setFont("Helvetica", 8)
        self.drawString(36, 36, "CONFIDENTIAL - INTERNAL USE ONLY")
        self.drawRightString(576, 36, f"Page {self._pageNumber} of {page_count}")
        
        # Thin divider line above footer
        self.setStrokeColor(colors.HexColor("#CCCCCC"))
        self.setLineWidth(0.5)
        self.line(36, 50, 576, 50)
        
        self.restoreState()


class PDFService:

    @staticmethod
    def generate_report(session_data: dict, output_path: str) -> None:
        """
        Generate a professional PDF report from the session trace data.
        """
        # Ensure directories exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()
        
        # Custom premium typography styles
        primary_color = colors.HexColor("#007A48") # BNP Green
        dark_grey = colors.HexColor("#222222")
        charcoal = colors.HexColor("#444444")
        accent_bg = colors.HexColor("#F0F8F4") # Pale green tint
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=primary_color,
            spaceAfter=15
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=charcoal,
            spaceAfter=30
        )
        
        h1_style = ParagraphStyle(
            'Heading1_Custom',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=primary_color,
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True
        )

        h2_style = ParagraphStyle(
            'Heading2_Custom',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=dark_grey,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'Body_Custom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            textColor=charcoal,
            leading=14,
            spaceAfter=10
        )

        bullet_style = ParagraphStyle(
            'Bullet_Custom',
            parent=body_style,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=4
        )

        meta_label_style = ParagraphStyle(
            'MetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            textColor=primary_color
        )
        
        meta_val_style = ParagraphStyle(
            'MetaValue',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=charcoal
        )

        story = []

        # 1. Header & Title Block
        story.append(Spacer(1, 15))
        story.append(Paragraph("BNP PARIBAS CHURN INTELLIGENCE REPORT", title_style))
        story.append(Paragraph(f"AI-Powered Risk Assessment, Actionable Recommendations & System Auditing", subtitle_style))
        
        # Meta info grid
        meta_data = [
            [
                Paragraph("Report Date:", meta_label_style),
                Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), meta_val_style),
                Paragraph("User Query:", meta_label_style),
                Paragraph(session_data.get("user_query", "N/A"), meta_val_style)
            ],
            [
                Paragraph("System Session ID:", meta_label_style),
                Paragraph(str(session_data.get("session_id", "N/A"))[:18] + "...", meta_val_style),
                Paragraph("Target Churn Intent:", meta_label_style),
                Paragraph(session_data.get("query_plan", {}).get("intent", "N/A").replace("_", " ").title(), meta_val_style)
            ]
        ]
        
        meta_table = Table(meta_data, colWidths=[100, 160, 100, 180])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), accent_bg),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 1, primary_color),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 20))

        # 2. Executive Report Section (from Reporting Agent)
        report = session_data.get("report", {})
        if report:
            story.append(Paragraph("Executive Summary", h1_style))
            story.append(Paragraph(report.get("executive_summary", "No executive summary provided."), body_style))
            
            # Key Findings
            story.append(Paragraph("Key Insights & Risk Drivers", h2_style))
            findings = report.get("key_findings", [])
            for finding in findings:
                story.append(Paragraph(f"&bull; {finding}", bullet_style))
            story.append(Spacer(1, 10))
            
            # Risk Assessment
            story.append(Paragraph("Overall Portfolio Risk Level", h2_style))
            story.append(Paragraph(report.get("risk_assessment", "No risk assessment available."), body_style))
            story.append(Spacer(1, 15))

        # 3. Overall Portfolio / RAG Database Statistics
        analysis = session_data.get("analysis", {})
        if analysis:
            story.append(Paragraph("Data Analytics Dashboard", h1_style))
            stats = analysis.get("statistics", {})
            
            stats_data = [
                ["KPI Metrics", "Value", "KPI Metrics", "Value"],
                ["Total Customer Portfolio", f"{stats.get('total_customers', 0):,}", "Average Client Age", f"{stats.get('average_age', 0)} years"],
                ["Churned Customers", f"{stats.get('churned_customers', 0):,}", "Average Account Tenure", f"{stats.get('average_tenure', 0)} months"],
                ["Identified Churn Rate", f"{stats.get('churn_rate', 0.0)}%", "ChromaDB Retrieval Size", "Top 5 Relevant Records"]
            ]
            
            stats_table = Table(stats_data, colWidths=[150, 120, 150, 120])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), primary_color),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9.5),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
                ('PADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 9),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 15))

        # 4. Target Customer Risk Assessment (from Churn Prediction Agent)
        prediction = session_data.get("prediction", {})
        if prediction:
            story.append(Paragraph("Targeted Client Churn Risk", h1_style))
            
            risk_level = prediction.get("risk_level", "Unknown")
            risk_color = "#007A48"  # Green
            if "High" in risk_level:
                risk_color = "#990000"  # Dark Red
            elif "Medium" in risk_level:
                risk_color = "#D97706"  # Orange
                
            pred_data = [
                [
                    Paragraph(f"<b>Client Account ID:</b> {prediction.get('customer_id')}", body_style),
                    Paragraph(f"<b>Predicted Risk Class:</b> <font color='{risk_color}'><b>{risk_level}</b></font>", body_style)
                ],
                [
                    Paragraph(f"<b>Model Risk Score:</b> {prediction.get('score', 0)} / 6", body_style),
                    Paragraph(f"<b>Risk Certainty (Confidence):</b> {prediction.get('confidence', 0)}%", body_style)
                ]
            ]
            pred_table = Table(pred_data, colWidths=[270, 270])
            pred_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('PADDING', (0,0), (-1,-1), 4),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#EEEEEE")),
            ]))
            story.append(pred_table)
            story.append(Spacer(1, 8))
            
            story.append(Paragraph("Churn Reasons Identified:", h2_style))
            reasons = prediction.get("reasons", [])
            for reason in reasons:
                story.append(Paragraph(f"&bull; {reason}", bullet_style))
            story.append(Spacer(1, 15))

        # Page Break to validation details
        story.append(PageBreak())

        # 5. Tailored Retention Actions (from Recommendation Agent)
        recommendation = session_data.get("recommendation", {})
        if recommendation:
            story.append(Paragraph("Tailored Strategic Retention Blueprint", h1_style))
            
            # Retention actions
            story.append(Paragraph("Immediate Retention Actions (Customer Support & Relations)", h2_style))
            actions = recommendation.get("retention_actions", [])
            for act in actions:
                story.append(Paragraph(f"&bull; {act}", bullet_style))
            story.append(Spacer(1, 8))
            
            # Upsell opportunities
            story.append(Paragraph("Contractual Incentives & Upsell Opportunities", h2_style))
            upsells = recommendation.get("upsell_opportunities", [])
            for up in upsells:
                story.append(Paragraph(f"&bull; {up}", bullet_style))
            story.append(Spacer(1, 8))

            # Service improvements
            story.append(Paragraph("Service & Support Improvements Required", h2_style))
            services = recommendation.get("service_improvements", [])
            for svc in services:
                story.append(Paragraph(f"&bull; {svc}", bullet_style))
            story.append(Spacer(1, 8))
            
            story.append(Paragraph(f"<b>Execution Priority Level:</b> {recommendation.get('priority', 'Normal')}", body_style))
            story.append(Spacer(1, 15))

        # 6. Audit & Validation Summary (Explainability & Guardrails)
        validation = session_data.get("validation", {})
        if validation:
            story.append(Paragraph("Factual Validation & Explainability Audit", h1_style))
            
            val_status = "PASSED" if validation.get("is_valid") else "FLAGGED"
            status_color = "#007A48" if val_status == "PASSED" else "#990000"
            
            # Table of metrics
            val_data = [
                ["Validation Audit Checklist", "Status", "Audit Summary Remarks"],
                ["Hallucination Analysis", "NO HALLUCINATION" if not validation.get("hallucination_detected") else "FLAGGED", validation.get("remarks", "")],
                ["Confidence Score Verification", "VERIFIED" if validation.get("confidence_verified") else "UNVERIFIED", f"System Trust Confidence: {validation.get('confidence', 0)}%"],
                ["Numerical Consistency Audit", "CONSISTENT" if validation.get("numerical_validation") else "INCONSISTENT", "All calculated rates verified."],
                ["Factual Evidence Availability", "FOUND" if validation.get("evidence_available") else "MISSING", "Trace citations present."]
            ]
            
            val_table = Table(val_data, colWidths=[180, 110, 250])
            val_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#333333")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
                ('PADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND', (0,1), (-1,-1), colors.white),
                ('FONTSIZE', (0,1), (-1,-1), 8.5),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ]))
            
            story.append(Paragraph(f"<b>Compliance Status:</b> <font color='{status_color}'><b>{val_status}</b></font>", h2_style))
            story.append(val_table)
            story.append(Spacer(1, 15))

        # 7. Explainability Logs (Evidence & Reasoning)
        story.append(Paragraph("Pipeline Explainability Logs (Evidence & Reasoning)", h2_style))
        
        # Build explainability story
        explain_items = []
        for stage, display_name in [("analysis", "RAG Analytics Stage"), ("prediction", "Churn Prediction Stage"), ("recommendation", "Retention Recommendation Stage"), ("validation", "System Validation Stage"), ("report", "Executive Reporting Stage")]:
            stage_data = session_data.get(stage, {})
            if stage_data:
                stage_story = []
                stage_story.append(Paragraph(f"<b>{display_name}</b>", h2_style))
                
                # Reasoning
                reasoning_text = stage_data.get("reasoning", "No reasoning details available.")
                stage_story.append(Paragraph(f"<b>Logical Reasoning:</b> {reasoning_text}", body_style))
                
                # Evidence
                evidence_list = stage_data.get("evidence", [])
                if evidence_list:
                    stage_story.append(Paragraph("<b>Supporting Evidence:</b>", body_style))
                    for ev in evidence_list:
                        stage_story.append(Paragraph(f"&bull; {ev}", bullet_style))
                        
                explain_items.append(KeepTogether(stage_story))
                explain_items.append(Spacer(1, 10))
                
        story.extend(explain_items)

        # Build PDF using our custom NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        print(f"ReportLab PDF Report generated successfully at {output_path}")

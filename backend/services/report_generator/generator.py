from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)


class ReportGenerator:

    def __init__(self):
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)

    # -------------------------------------------------

    def safe(self, obj, key, default="Not Available"):
        return getattr(obj, key, default)

    # -------------------------------------------------

    def make_table(self, data):

        table = Table(
            data,
            colWidths=[150, 330],
            repeatRows=1
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey,
                    ),

                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor("#dceeff"),
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),

                    (
                        "FONTSIZE",
                        (0,0),
                        (-1,-1),
                        8,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0,0),
                        (-1,-1),
                        5,
                    ),
                ]
            )
        )

        return table

    # -------------------------------------------------

    def footer(self, canvas, doc):

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.setFillColor(
            colors.grey
        )

        canvas.drawString(
            40,
            25,
            "OceanSpill AI | AI Marine Intelligence Platform"
        )


        canvas.drawRightString(
            550,
            25,
            f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}"
        )


        canvas.drawRightString(
            550,
            12,
            f"Page {doc.page}"
        )


        canvas.restoreState()

    # -------------------------------------------------

    def generate(self, report):

        output = (
            self.output_dir /
            "OceanSpill_AI_Incident_Report.pdf"
        )


        doc = SimpleDocTemplate(
            str(output),
            pagesize=A4,
            rightMargin=35,
            leftMargin=35,
            topMargin=35,
            bottomMargin=45,
        )


        styles = getSampleStyleSheet()


        title_style = ParagraphStyle(
            "title",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
        )


        heading = ParagraphStyle(
            "heading",
            parent=styles["Heading2"],
            fontSize=11,
            spaceBefore=6,
            spaceAfter=4,
        )


        body = ParagraphStyle(
            "body",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=10,
        )


        elements = []


        # =================================================
        # HEADER
        # =================================================

        elements.append(
            Paragraph(
                "OceanSpill AI",
                title_style
            )
        )


        elements.append(
            Paragraph(
                "Marine Oil Spill Incident Assessment Report",
                styles["Heading3"]
            )
        )


        elements.append(
            Paragraph(
                "AI Powered Detection | Satellite Vision | AIS Analysis | Drift Prediction",
                body
            )
        )


        elements.append(
            Spacer(1,10)
        )


        # =================================================
        # DETECTION SUMMARY
        # =================================================

        elements.append(
            Paragraph(
                "1. Detection Summary",
                heading
            )
        )


        summary = [

            ["Parameter","Value"],

            [
                "Report ID",
                "OSI-AI-2026-001"
            ],

            [
                "Detection Time",
                self.safe(report,"detection_time")
            ],

            [
                "Location",
                self.safe(report,"spill_location")
            ],

            [
                "Oil Spill Detected",
                str(self.safe(report,"spill_detected"))
            ],

            [
                "Confidence",
                str(self.safe(report,"confidence"))+"%"
            ],

            [
                "Estimated Area",
                str(self.safe(report,"spill_area"))+" km²"
            ],

            [
                "Risk Level",
                self.safe(report,"risk_level")
            ]

        ]


        elements.append(
            self.make_table(summary)
        )


        # =================================================
        # AI EVIDENCE
        # =================================================

        elements.append(
            Paragraph(
                "2. AI Detection Evidence",
                heading
            )
        )


        image_paths = [

            "outputs/original.png",

            "outputs/mask.png",

            "outputs/overlay.png"

        ]


        image_data=[]


        for p in image_paths:

            path=Path(p)

            if path.exists():

                image_data.append(
                    Image(
                        str(path),
                        width=130,
                        height=100
                    )
                )

            else:

                image_data.append(
                    Paragraph(
                        "Unavailable",
                        body
                    )
                )


        img_table = Table(
            [
                [
                    Paragraph("Original",body),
                    Paragraph("Mask",body),
                    Paragraph("Overlay",body)
                ],
                image_data
            ],

            colWidths=[
                160,
                160,
                160
            ]
        )


        elements.append(img_table)



        # =================================================
        # WEATHER + DRIFT
        # =================================================

        elements.append(
            Paragraph(
                "3. Weather & Spill Drift Prediction",
                heading
            )
        )


        weather = getattr(
            report,
            "weather",
            {}
        )


        drift = getattr(
            report,
            "drift_prediction",
            {}
        )


        combined=[]


        for k,v in weather.items():
            combined.append(
                [
                    k,
                    v
                ]
            )


        for k,v in drift.items():
            combined.append(
                [
                    "Drift - "+k,
                    v
                ]
            )


        combined.extend(

            [

                [
                    "12 Hour Forecast",
                    "Pending Weather API Integration"
                ],

                [
                    "24 Hour Forecast",
                    "Pending Ocean Current API Integration"
                ]

            ]

        )


        elements.append(
            self.make_table(
                [
                    [
                        "Factor",
                        "Value"
                    ]
                ]
                +
                combined
            )
        )



        # =================================================
        # IMPACT ANALYSIS
        # =================================================

        elements.append(
            Paragraph(
                "4. Environmental & Economic Impact",
                heading
            )
        )


        impact=[]


        for name in [

            "environmental_summary",

            "economic_summary",

        ]:

            data=getattr(
                report,
                name,
                {}
            )


            for k,v in data.items():

                impact.append(
                    [
                        k,
                        v
                    ]
                )



        elements.append(
            self.make_table(
                [
                    [
                        "Impact",
                        "Assessment"
                    ]
                ]
                +
                impact
            )
        )


        # =================================================
        # AIS + CLEANUP
        # =================================================

        elements.append(
            Paragraph(
                "5. Suspected AIS Vessel & Cleanup Recommendation",
                heading
            )
        )


        vessel=getattr(
            report,
            "suspected_vessel",
            {}
        )


        vessel_rows=[]


        for k,v in vessel.items():

            vessel_rows.append(
                [
                    k,
                    v
                ]
            )


        elements.append(
            self.make_table(
                [
                    [
                        "AIS Parameter",
                        "Value"
                    ]
                ]
                +
                vessel_rows
            )
        )


        recommendations=getattr(
            report,
            "recommendations",
            []
        )


        for r in recommendations[:4]:

            elements.append(
                Paragraph(
                    "• "+str(r),
                    body
                )
            )


        elements.append(
            Spacer(1,5)
        )


        elements.append(
            Paragraph(
                """
                AI Analysis Summary:
                Satellite segmentation detected possible hydrocarbon
                contamination. Further confirmation using AIS,
                weather API and ocean current modelling is recommended.
                """,
                body
            )
        )


        doc.build(
            elements,
            onFirstPage=self.footer,
            onLaterPages=self.footer
        )


        return output
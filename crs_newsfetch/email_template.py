from PySide6 import QtCore, QtWidgets

from scholar_result import ScholarResult

class EmailTemplate(QtWidgets.QDialog):
    def __init__(self, result: ScholarResult):
        super().__init__()

        templateText = f"""
Subject: Request to Complete CRS Achievement Form

Dear {result.author},

I hope this email finds you well. I am reaching out regarding a recent publication:

Title: {result.title}
Publication Date: {result.publication_year}
URL: {result.url}

The Center for Research and Scholarship (CRS) celebrates faculty achievements and kindly requests that you report this achievement using the CRS Achievement Portal.
Please fill out a separate form for each achievement. You can access the portal here: https://oxy.qualtrics.com/jfe/form/SV_42WuvMMsPYXasC2

Please ensure you advance to the end of the survey until you see the final confirmation page: "Thank you for visiting the CRS portal."
Responses are reviewed for bi-monthly publication. For any assistance or questions, please contact the CRS Director at crs@oxy.edu.

Thank you for taking the time to report your achievements!
        """

        self.setWindowTitle(f"Email to {result.author}")

        layout = QtWidgets.QVBoxLayout(self)
        templateLabel = QtWidgets.QLabel(templateText)
        templateLabel.setTextInteractionFlags(
                QtCore.Qt.TextInteractionFlags.TextSelectableByMouse
        )
        layout.addWidget(templateLabel)
        self.setLayout(layout)

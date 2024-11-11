from PySide6 import QtCore, QtWidgets

from scholar_result import ScholarResult

class EmailTemplate(QtWidgets.QDialog):
    def __init__(self, result: ScholarResult):
        super().__init__()

        templateText = f"""
        Template goes here
        Title: {result.title}
        Staff: {result.author}
        Publication year: {result.publication_year}
        URL: {result.url}
        """

        self.setWindowTitle(f"Email to {result.author}")

        layout = QtWidgets.QVBoxLayout(self)
        templateLabel = QtWidgets.QLabel(templateText)
        templateLabel.setTextInteractionFlags(
                QtCore.Qt.TextInteractionFlags.TextSelectableByMouse
        )
        layout.addWidget(templateLabel)
        self.setLayout(layout)

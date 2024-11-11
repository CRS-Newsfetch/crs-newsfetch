from PySide6 import QtWidgets

from scholar_result import ScholarResult

class EmailTemplate(QtWidgets.QDialog):
    def __init__(self, result: ScholarResult):
        super().__init__()

        templateText = f"""
        Template goes here
        Title: {result.title}
        Author: {result.author}
        Publication year: {result.publication_year}
        URL: {result.url}
        """

        self.setWindowTitle(f"Email to {result.author}")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel(templateText))
        self.setLayout(layout)

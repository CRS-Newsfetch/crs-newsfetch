from PySide6 import QtCore, QtWidgets, QtGui
import datetime

from scholar_result import ScholarResult

class Gui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout(self)

        today = datetime.date.today()
        lastMonth = today.replace(day = 1) - datetime.timedelta(days = 1)
        if lastMonth.day > today.day:
            lastMonth = lastMonth.replace(day = today.day)

        startDateLayout = QtWidgets.QHBoxLayout(self)
        startDateEdit = QtWidgets.QDateTimeEdit(lastMonth, calendarPopup = True)
        startDateLabel = QtWidgets.QLabel("Start date:")
        startDateLabel.setBuddy(startDateEdit)
        startDateLayout.addWidget(startDateLabel)
        startDateLayout.addWidget(startDateEdit)

        endDateLayout = QtWidgets.QHBoxLayout(self)
        endDateEdit = QtWidgets.QDateTimeEdit(today, calendarPopup = True)
        endDateLabel = QtWidgets.QLabel("End date:")
        endDateLabel.setBuddy(endDateEdit)
        endDateLayout.addWidget(endDateLabel)
        endDateLayout.addWidget(endDateEdit)

        self._resultsLayout = QtWidgets.QVBoxLayout(self)

        self.layout.addWidget(QtWidgets.QLabel("Please choose a date range to search",
                                               alignment = QtCore.Qt.AlignCenter))
        self.layout.addLayout(startDateLayout)
        self.layout.addLayout(endDateLayout)

        searchButton = QtWidgets.QPushButton("Search", self)
        searchButton.clicked.connect(self._onSearchClick)
        self.layout.addWidget(searchButton)

        self.layout.addLayout(self._resultsLayout)

    def _onSearchClick(self):
        # This is currently just a test until we have actual data
        testResult = ScholarResult("Test Title",
                                   "Test Author",
                                   datetime.date(1969, 4, 20),
                                   "Test Summary")
        self._addResult(testResult)
        self._addResult(testResult)
        self._addResult(testResult)

    def _addResult(self, result: ScholarResult):
        resultFrame = QtWidgets.QFrame(self)
        resultFrame.setLineWidth(2)
        resultFrame.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)

        resultBox = QtWidgets.QVBoxLayout(self)

        resultBox.addWidget(QtWidgets.QLabel(result.title))
        resultBox.addWidget(QtWidgets.QLabel(result.professor))
        resultBox.addWidget(QtWidgets.QLabel(str(result.date)))
        resultBox.addWidget(QtWidgets.QLabel(result.summary))

        resultFrame.setLayout(resultBox)
        self._resultsLayout.addWidget(resultFrame)

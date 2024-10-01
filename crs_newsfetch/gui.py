from PySide6 import QtCore, QtWidgets, QtGui
import datetime

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

        self._resultsLayout = QtWidgets.QVBoxLayout(self.layout)

        self.layout.addWidget(QtWidgets.QLabel("Please choose a date range to search",
                                               alignment = QtCore.Qt.AlignCenter))
        self.layout.addLayout(startDateLayout)
        self.layout.addLayout(endDateLayout)

        self.layout.addWidget(QtWidgets.QPushButton("Search", self))

        self.layout.addLayout(self._resultsLayout)

    def _addResult(self, result: ScholarResult):
        resultBox = QtWidgets.QVBoxLayout(self._resultsLayout)

        resultBox.addWidget(QtWidgets.QLabel(result.title))
        resultBox.addWidget(QtWidgets.QLabel(result.professor))
        resultBox.addWidget(QtWidgets.QLabel(str(result.date)))
        resultBox.addWidget(QtWidgets.QLabel(result.summary))

        self._resultsLayout.addLayout(resultBox)

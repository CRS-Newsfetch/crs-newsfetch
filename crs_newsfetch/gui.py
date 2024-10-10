from PySide6 import QtCore, QtWidgets, QtGui
import datetime

from scholar_result import ScholarResult
from scraper import Scraper

class Gui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self._scraper = Scraper()

        self.layout = QtWidgets.QVBoxLayout(self)
        layoutWidget = self.layout.widget()

        today = datetime.date.today()
        lastMonth = today.replace(day = 1) - datetime.timedelta(days = 1)
        if lastMonth.day > today.day:
            lastMonth = lastMonth.replace(day = today.day)

        startDateLayout = QtWidgets.QHBoxLayout(layoutWidget)
        self._start = QtWidgets.QDateTimeEdit(lastMonth, calendarPopup = True)
        startDateLabel = QtWidgets.QLabel("Start date:")
        startDateLabel.setBuddy(self._start)
        startDateLayout.addWidget(startDateLabel)
        startDateLayout.addWidget(self._start)

        endDateLayout = QtWidgets.QHBoxLayout(layoutWidget)
        self._end = QtWidgets.QDateTimeEdit(today, calendarPopup = True)
        endDateLabel = QtWidgets.QLabel("End date:")
        endDateLabel.setBuddy(self._end)
        endDateLayout.addWidget(endDateLabel)
        endDateLayout.addWidget(self._end)

        resultsScrollArea = QtWidgets.QScrollArea(layoutWidget)
        resultsWidget = QtWidgets.QWidget(resultsScrollArea)
        self._resultsLayout = QtWidgets.QVBoxLayout(resultsWidget)
        resultsWidget.setLayout(self._resultsLayout)
        resultsScrollArea.setWidgetResizable(True)
        resultsScrollArea.setWidget(resultsWidget)

        self.layout.addWidget(Gui._centeredLabel("Please choose a date range to search"))
        self.layout.addLayout(startDateLayout)
        self.layout.addLayout(endDateLayout)

        searchButton = QtWidgets.QPushButton("Search", layoutWidget)
        searchButton.clicked.connect(self._onSearchClick)
        self.layout.addWidget(searchButton)

        self.layout.addWidget(resultsScrollArea)

    def _onSearchClick(self):
        # Clear existing results
        for i in reversed(range(self._resultsLayout.count())):
            self._resultsLayout.itemAt(i).widget().setParent(None)

        scrape_results = self._scraper.scrape(self._start.date().toPython(),
                                              self._end.date().toPython())

        # Add new results
        for result in scrape_results:
            resultFrame = QtWidgets.QFrame(self._resultsLayout.widget())
            resultFrame.setLineWidth(2)
            resultFrame.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)

            resultBox = QtWidgets.QVBoxLayout(resultFrame)

            resultBox.addWidget(Gui._centeredLabel(result.title))
            resultBox.addWidget(Gui._centeredLabel(result.author))
            resultBox.addWidget(Gui._centeredLabel(f"Published {result.publication_date}"))
            resultBox.addWidget(Gui._centeredLabel(result.url))

            resultFrame.setLayout(resultBox)
            self._resultsLayout.addWidget(resultFrame)

    def _centeredLabel(text: str):
        return QtWidgets.QLabel(text, alignment = QtCore.Qt.AlignCenter)

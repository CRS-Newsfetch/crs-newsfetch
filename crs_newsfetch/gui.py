from PySide6 import QtCore, QtWidgets, QtGui
import datetime

from scholar_result import ScholarResult
from scraper import Scraper

class Gui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self._threadpool = QtCore.QThreadPool()
        
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

        self._searchText = "Search"
        self._searchButton = QtWidgets.QPushButton(self._searchText, layoutWidget)
        self._searchButton.clicked.connect(self._onSearchClick)
        self.layout.addWidget(self._searchButton)

        self.layout.addWidget(resultsScrollArea)

    def _onSearchClick(self):
        if not self._searchButton.isEnabled():
            return

        # Set up search button for fetch
        self._searchButton.setEnabled(False)
        self._searchButton.setText("Fetching results...")

        # Clear existing results
        for i in reversed(range(self._resultsLayout.count())):
            self._resultsLayout.itemAt(i).widget().setParent(None)

        # Run scraper in seperate thread for selected date range
        scraper = Scraper(self._start.date().toPython(), self._end.date().toPython())
        scraper.signals.result.connect(self._addResult)
        scraper.signals.finished.connect(self._resetSearchButton)
        self._threadpool.start(scraper)

    def _addResult(self, result: ScholarResult):
        resultFrame = QtWidgets.QFrame(self._resultsLayout.widget())
        resultFrame.setLineWidth(2)
        resultFrame.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)

        resultBox = QtWidgets.QVBoxLayout(resultFrame)

        resultBox.addWidget(QtWidgets.QLabel(f"<b>{result.author}</b>"))
        resultBox.addWidget(Gui._centeredLabel(result.title))
        resultBox.addWidget(Gui._centeredLabel(f"Published {result.publication_date}"))
        resultBox.addWidget(Gui._centeredLabel(result.url))

        resultFrame.setLayout(resultBox)
        self._resultsLayout.addWidget(resultFrame)

    def _resetSearchButton(self):
        self._searchButton.setText(self._searchText)
        self._searchButton.setEnabled(True)

    def _centeredLabel(text: str):
        return QtWidgets.QLabel(text, alignment = QtCore.Qt.AlignCenter)

from PySide6 import QtCore, QtWidgets, QtGui
import datetime

from email_template import EmailTemplate
from scholar_result import ScholarResult
from database import DatabaseManager
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

        self.layout.addWidget(Gui._centeredLabel("Please choose a date range to search"))
        self.layout.addLayout(startDateLayout)
        self.layout.addLayout(endDateLayout)

        self._searchText = "Search"
        self._searchButton = QtWidgets.QPushButton(self._searchText, layoutWidget)
        self._searchButton.clicked.connect(self._onSearchClick)
        self.layout.addWidget(self._searchButton)

        self._authorScrapedLabel = Gui._centeredLabel()
        self._resultScrapedLabel = Gui._centeredLabel()
        self._statusLabel = Gui._centeredLabel()
        self.layout.addWidget(self._authorScrapedLabel)
        self.layout.addWidget(self._resultScrapedLabel)
        self.layout.addWidget(self._statusLabel)


        self.tabWidget = QtWidgets.QTabWidget(layoutWidget)
        self.layout.addWidget(self.tabWidget)

        # Results tab with scrollable area
        resultsTab = QtWidgets.QWidget(self.tabWidget)
        resultsScrollArea = QtWidgets.QScrollArea(resultsTab)
        resultsScrollArea.setWidgetResizable(True)
        resultsWidget = QtWidgets.QWidget()
        self._resultsLayout = QtWidgets.QVBoxLayout(resultsWidget)
        resultsWidget.setLayout(self._resultsLayout)
        resultsScrollArea.setWidget(resultsWidget)
        resultsLayout = QtWidgets.QVBoxLayout(resultsTab)
        resultsLayout.addWidget(resultsScrollArea)
        self.tabWidget.addTab(resultsTab, "Results")

        # Hidden results tab with scrollable area
        hiddenTab = QtWidgets.QWidget(self.tabWidget)
        hiddenScrollArea = QtWidgets.QScrollArea(hiddenTab)
        hiddenScrollArea.setWidgetResizable(True)
        hiddenWidget = QtWidgets.QWidget()
        self._hiddenResultsLayout = QtWidgets.QVBoxLayout(hiddenWidget)
        hiddenWidget.setLayout(self._hiddenResultsLayout)
        hiddenScrollArea.setWidget(hiddenWidget)
        hiddenLayout = QtWidgets.QVBoxLayout(hiddenTab)
        hiddenLayout.addWidget(hiddenScrollArea)
        self.tabWidget.addTab(hiddenTab, "Hidden Results")

        self.db_manager = DatabaseManager()


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
        self._authorsScraped = -1
        self._resultsScraped = -1
        self._addResultScraped()
        keywords = ["Occidental"]
        scraper = Scraper(self._start.date().toPython(), self._end.date().toPython(), keywords)
        scraper.signals.author_amount.connect(self._setAuthorAmount)
        scraper.signals.author_scraping.connect(self._setAuthorScraping)
        scraper.signals.source_scraping.connect(self._setStatusLabel)
        scraper.signals.result_scraped.connect(self._addResultScraped)
        scraper.signals.result.connect(self._addResult)
        scraper.signals.finished.connect(self._handleScraperEnd)
        self._threadpool.start(scraper)

    def _hideResult(self, result: ScholarResult, resultFrame: QtWidgets.QFrame):
        resultFrame.hide()

        self.db_manager.hide_result(result)

        hiddenFrame = QtWidgets.QFrame()
        hiddenFrame.setLineWidth(2)
        hiddenFrame.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)

        hiddenBox = QtWidgets.QVBoxLayout(hiddenFrame)

        hiddenBox.addWidget(QtWidgets.QLabel(f"<b>{result.author}</b>"))
        hiddenBox.addWidget(Gui._centeredLabel(result.title))
        hiddenBox.addWidget(Gui._centeredLabel(f"Published {result.publication_year}"))
        hiddenBox.addWidget(Gui._centeredLabel(result.url))

        unhideButton = QtWidgets.QPushButton("Unhide")
        unhideButton.clicked.connect(lambda: self._unhideResult(result, hiddenFrame))
        hiddenBox.addWidget(unhideButton)

        hiddenFrame.setLayout(hiddenBox)
        self._hiddenResultsLayout.addWidget(hiddenFrame)


    def _unhideResult(self, result: ScholarResult, hiddenFrame: QtWidgets.QFrame):
        hiddenFrame.hide()
        self.db_manager.unhide_result(result)
        self._addResult(result)

    def _addResultScraped(self):
        self._resultsScraped += 1
        resultWord = "result" if self._resultsScraped == 1 else "results"
        self._resultScrapedLabel.setText(
                f"{self._resultsScraped} {resultWord} processed."
        )

    def _setAuthorAmount(self, amount: int):
        self._authorAmount = amount

    def _setAuthorScraping(self, author: str):
        self._currentAuthor = author

        self._authorsScraped += 1
        self._authorScrapedLabel.setText(
                f"{self._authorsScraped}/{self._authorAmount} staff processed."
        )

    def _setStatusLabel(self, source: str):
        self._statusLabel.setText(
                f"Currently getting results for {self._currentAuthor} from {source}."
        )

    def _addResult(self, result: ScholarResult):
        resultFrame = QtWidgets.QFrame(self._resultsLayout.widget())
        resultFrame.setLineWidth(2)
        resultFrame.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)

        resultBox = QtWidgets.QVBoxLayout(resultFrame)

        resultBox.addWidget(QtWidgets.QLabel(f"<b>{result.author}</b>"))
        resultBox.addWidget(Gui._centeredLabel(result.title))
        resultBox.addWidget(Gui._centeredLabel(f"Published {result.publication_year}"))
        resultBox.addWidget(Gui._centeredLabel(result.url))

        emailButton = QtWidgets.QPushButton("Open email template")
        emailButton.clicked.connect(lambda: EmailTemplate(result).exec())
        resultBox.addWidget(emailButton)

        hideButton = QtWidgets.QPushButton("Hide")
        hideButton.clicked.connect(lambda: self._hideResult(result, resultFrame))
        resultBox.addWidget(hideButton)

        resultFrame.setLayout(resultBox)
        self._resultsLayout.addWidget(resultFrame)

    def _handleScraperEnd(self):
        self._statusLabel.setText("")

        self._searchButton.setText(self._searchText)
        self._searchButton.setEnabled(True)

    def _centeredLabel(text: str = ""):
        return QtWidgets.QLabel(text, alignment = QtCore.Qt.AlignCenter)

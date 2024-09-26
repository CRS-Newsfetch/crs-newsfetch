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

        self.layout.addWidget(QtWidgets.QLabel("Please choose a date range to search",
                                               alignment = QtCore.Qt.AlignCenter))
        self.layout.addLayout(startDateLayout)
        self.layout.addLayout(endDateLayout)

        self.layout.addWidget(QtWidgets.QPushButton("Search", self))

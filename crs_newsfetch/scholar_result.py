from datetime import date

class ScholarResult:
    def __init__(self,
                 author: str,
                 title: str | None,
                 publication_date: date | None,
                 doi: str | None
                 url: str | None):
        self.author = author
        self.title = title
        self.publication_date = publication_date
        self.doi = doi
        self.url = url

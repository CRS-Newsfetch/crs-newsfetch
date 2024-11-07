class ScholarResult:
    def __init__(self,
                 author: str,
                 title: str | None,
                 publication_year: int,
                 url: str | None):
        self.author = author
        self.title = title
        self.publication_year = publication_year
        self.url = url

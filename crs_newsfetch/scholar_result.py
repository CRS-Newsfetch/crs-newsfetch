class ScholarResult:
    def __init__(self,
                 author: str,
                 title: str | None,
                 publication_year: int,
                 url: str | None,
                 full_content: str | None):
        self.author = author
        self.title = title
        self.publication_year = publication_year
        self.url = url
        self.full_content = full_content
        self.id = -1 # Updated later

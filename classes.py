
# Define a Job class to store job details

class Board:
    def __init__(self, company, func, url, location_qualifiers, job_title_qualifiers, job_title_disqualifiers, visited_ids):
        self.company = company
        self.func = func
        self.url = url
        self.location_qualifiers = location_qualifiers
        self.job_title_qualifiers = job_title_qualifiers
        self.job_title_disqualifiers = job_title_disqualifiers
        self.visited_ids = visited_ids

class Job:
    def __init__(self, company, job_id, title, location, url, content=None, published_at=None):
        self.company = company
        self.id = job_id
        self.title = title
        self.location = location
        self.url = url
        self.content = content
        self.published_at = published_at

    def __repr__(self):
        return f"Job(company={self.company}, id={self.id}, title={self.title}, location={self.location}, url={self.url}, published_at={self.published_at})"

    def to_dict(self):
        return {
            "company": self.company,            "id": self.id,
            "title": self.title,                "location": self.location,
            "url": self.url,                    "content": self.content,
            "published_at": self.published_at,
        }


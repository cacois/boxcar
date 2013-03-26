from django.db import models

class Recipe:
    name = ''
    description = ''
    maintainer = ''
    average_rating = ''
    date_published = ''
    date_updated = ''
    fileurl = ''
    license = ''
    version = ''

    def __init__(self, **entries):
        self.__dict__.update(entries)

from django.db import models

class Recipe:
    """
    A basic model class defining a recipe that can be instantiated
    from a json-derived dict

    """
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

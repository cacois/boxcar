from django.core.management.base import BaseCommand, CommandError
from polls.models import Poll
import requests
import logging
from pymongo import MongoClient
import json

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        """
        Queries the Opscode Community API for all available Chef 
        cookbooks from the opscode community site and stores records 
        for each in mongodb

        Record format:

        { 
        name: 'name', 
        description: 'description', 
        maintainer: 'maintainer', 
        average_rating: 'average_rating',
        date_published: 'date_published',
        date_updated: 'date_updated',
        fileurl: 'fileurl',
        license: 'license',
        version: 'version'
        }

        NOTE: May be missing one cookbook, but not sure
        """
        logger.info('Updating cookbooks from %s: ' % BASE_URL)
        res = requests.get(BASE_URL + 'cookbooks')
        cookbooks = json.loads(res.content)
        num_books = int(cookbooks['total'])
        logger.info('Found %d cookbooks available' % num_books)
        checked = 0

        while checked <= num_books:
            if checked != 0:
                res = requests.get(BASE_URL + 'cookbooks', params = {'start' : checked+1} )
                cookbooks = json.loads(res.content)

            checked += len(cookbooks['items'])

            for book in cookbooks['items']:
                # cookbook api call
                res = requests.get(book['cookbook'])
                cookbook_rec = json.loads(res.content)

                res = requests.get(cookbook_rec['latest_version'])
                cookbook_detail = json.loads(res.content)
                fileurl = cookbook_detail['file']

                # build record
                record = {
                    'name': book['cookbook_name'],
                    'description': book['cookbook_description'],
                    'maintainer': book['cookbook_maintainer'],
                    'average_rating': cookbook_rec['average_rating'],
                    'created_at': cookbook_rec['created_at'],
                    'updated_at': cookbook_rec['updated_at'],
                    'fileurl': cookbook_detail['file'],
                    'license': cookbook_detail['license'],
                    'version': cookbook_detail['version']
                  }

                # write record to db
                db.boxcar_cookbooks.insert(record)

        logger.info('Update completed.')
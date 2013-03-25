#!/usr/bin/python

import ConfigParser
import requests
import json
from string import Template
from zipfile import ZipFile
import pymongo
import time
from InMemoryZip import InMemoryZip
from pymongo import MongoClient
import tarfile
import os
import logging

# logging stuff
logger = logging.getLogger('boxcar')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler('boxcar.log'))

# config stuff
config = ConfigParser.RawConfigParser()
config.read('boxcar.cfg')

# mongodb stuff
connection = MongoClient('localhost')
db = connection.boxcar_cookbooks

BASE_URL = config.get('api', 'base_url')
ITEMS = 99 # can get 99 cookbooks from api per request

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

def update_cookbooks():
    """
    Gathers information on all available Chef cookbooks from the opscode 
    community site and stores records for each in mongodb

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

def download_cookbook(fileurl, download_dir):
  """
  Downloads a cookbook tar.gz, unzips it, and writes the 
  directory structure to the zip file. 
  """

  # download and save file to download_dir
  logger.info('Downloading: %s' % fileurl)
  # get filename
  tarname = fileurl.split('/')[-1].split('?')[0]
  tarfilepath = download_dir + tarname
  logger.info('Writing file to %s' % tarfilepath)
  with open(tarfilepath, 'w') as tmpfile:
    res = requests.get(fileurl)  
    for chunk in res.iter_content(256):
      tmpfile.write(chunk)

  logger.info('Extracting contents of %s to %s' % (tarfilepath, download_dir))
  # extract file to download_dir
  with tarfile.open(tarfilepath) as tar:
    try:
      tar.extractall(download_dir)
    except Exception as e:
      logger.error('Error extracting tarfile %s. Ex: %s' % (tarfilepath, e))

  logger.info('Deleting %s' % tarfilepath)
  # delete the downloaded archive
  os.remove(tarfilepath)

def generate_vagrantfile(box, app_name, memory, recipes, port=None):
  """
  From a template, generate a custom vagrantfile as defined by user
  """
  logger.info('Generating Vagrantfile')

  if port != None:
    portline = '\n  config.vm.forward_port %s, %s\n' % (port, port)
    logger.info('Configured port forwarding...')

  recipe_lines = ''
  for recipe in recipes:
    recipe_lines += '    chef.add_recipe \"%s\"\n' % recipe.name

  logger.info('Configured %d recipes...' % len(recipes))

  # generate final Vagrantfile from template
  template = Template(open('vagrantfile_template', 'r').read())
  return template.safe_substitute({'box':box, 'port_line':portline, 'app_name':app_name, 'memory':memory, 'recipe_lines':recipe_lines})

def build_package(box, app_name, memory, recipes, port=None):
  """
  Builds a Vagrant environment in a zip file, including configured 
  Vagrantfile, chef cookbooks, and sample app directory
  """

  # get directory to download temp files to
  download_dir = config.get('local', 'download_base_dir')

  # create a zip file
  zipname = app_name + '-env.zip'
  logger.info('Creating zipfile: %s...' % zipname)
  zip = ZipFile(zipname, 'w')

  # get the vagrantfile
  vagrantfile = generate_vagrantfile(box, app_name, memory, recipes, port)
  logger.info('Adding Vagrantfile to zip...')
  zip.writestr('Vagrantfile', vagrantfile)

  # download each cookbook, write to zip
  logger.info('Writing recipes to zip...')
  for recipe in recipes:
    # download cookbook
    download_cookbook(recipe.fileurl, download_dir)

  cookbook_dirs = []

  # search for all unpacked cookbooks
  for (root, dirs, files) in os.walk(download_dir):
    # copy list, add root path
    cookbook_dirs = map(lambda x: root + x, dirs[:])
    logger.info("Found unpacked cookbooks: %s" % cookbook_dirs)
    # stop recursing
    dirs[:] = []
  
  # write each cookbook to zip
  for cb_dir in cookbook_dirs:
    logger.info('Writing cookbook %s to zip...' % cb_dir)
    write_dir_to_zip(cb_dir, zip, '/cookbooks/')
    

def write_dir_to_zip(target_dir, zip, zip_path):
  """
  Writes a directory and all of its contents to the specified zip archive, 
  at the specified path within the archive.
  """
  logger.info('Attempting to write file %s to zip path %s' % (target_dir, zip_path))

  # trim '/' off target_dir, if necessary
  if target_dir[-1] == '/':
    target_dir = target_dir[:-1]

  # grab the last index of the base path
  basepathend = len(target_dir) + 1

  # get the name of the dir to write
  dir = target_dir.split('/')[-1]

  logger.info('target_dir: ' + target_dir)

  # walk along the target dir path, hitting all files
  for base, dirs, files in os.walk(target_dir):
    for file in files:
      full_path = os.path.join(base, file)
      path_from_base = full_path[basepathend:]
      # write to zip
      logger.info('Writing file %s to zip path %s%s/%s' % (full_path, zip_path, dir, path_from_base))
      zip.write(full_path, '%s%s/%s' % (zip_path, dir, path_from_base) )


if __name__ == '__main__':
  r1 = Recipe( **db.boxcar_cookbooks.find_one({'name': 'apache2'}) )
  r2 = Recipe( **db.boxcar_cookbooks.find_one({'name': 'django'}) )
  logger.info('Recipes: {0}'.format( ', '.join([r1.name, r2.name]) ) )
  logger.info('Generating environment...')
  build_package(box='precise64', app_name='test_app', memory=512, recipes=[r1, r2], port=3000)

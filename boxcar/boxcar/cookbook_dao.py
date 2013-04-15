import os, shutil
import tarfile
import logging
from pymongo import MongoClient
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# mongodb stuff
mongo_host = settings.MONGO_HOST
connection = MongoClient(mongo_host)
db = connection.boxcar_cookbooks

def download_cookbook(fileurl, download_dir):
  """
  Downloads a cookbook tar.gz, unzips it, and writes the 
  directory structure to the zip file. 
  
  """

  # download and save file to download_dir
  logger.info('Downloading cookbook: %s' % fileurl)
  
  # get filename
  tarname = fileurl.split('/')[-1].split('?')[0]
  tarfilepath = download_dir + tarname

  logger.info('Writing cookbook file to %s' % tarfilepath)
  
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

  # delete the downloaded archive
  logger.info('Deleting %s' % tarfilepath)
  os.remove(tarfilepath)

def cookbook_search(search_term):
  """
  Search for all cookbooks matching search_term
  
  """
  return db.boxcar_cookbooks.find({'name': {'$regex':'^'+search_term}})

def find_one_cookbook(name):
  """
  Search for a single cookbook of the specified name

  """
  return db.boxcar_cookbooks.find_one({'name': name})

def cleanup():
  """
  Cleans up all cookbook files from cookbook downloads and extractions 
  during package generation process

  """
  download_dir = settings.DOWNLOAD_BASE_DIR

  for base, dirs, files in os.walk(download_dir):
    for dir in dirs:
      shutil.rmtree(download_dir + dir)
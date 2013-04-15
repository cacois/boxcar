import ConfigParser
import requests
import json
from string import Template
from zipfile import ZipFile
import pymongo
import time
from pymongo import MongoClient
import tarfile
import os, shutil
import logging
from boxcar.models import Recipe
import cookbook_dao

logger = logging.getLogger(__name__)

# config stuff
config = ConfigParser.RawConfigParser()
config.read('boxcar.cfg')

# Constants
BASE_URL = config.get('api', 'base_url')

def build_package(base_box, app_name, memory, recipes, ports=None):
  """
  Builds a Vagrant environment in a zip file, including configured 
  Vagrantfile, chef cookbooks, and sample app directory
  """

  # get directory to download temp files to
  download_dir = config.get('local', 'download_base_dir')

  # if directory doesn't exist, create it
  if not os.path.exists(download_dir):
    os.makedirs(download_dir)

  # create a zip file
  zipname = app_name + '-env.zip'
  logger.info('Creating zipfile: %s...' % zipname)
  zip = ZipFile(zipname, 'w')

  # get the vagrantfile
  vagrantfile = _generate_vagrantfile(base_box, app_name, memory, recipes, ports)
  logger.info('Adding Vagrantfile to zip...')
  zip.writestr('Vagrantfile', vagrantfile)

  # download each cookbook, write to zip
  logger.info('Writing recipes to zip...')
  for recipe in recipes:
    # download cookbook
    cookbook_dao.download_cookbook(recipe.fileurl, download_dir)

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
    _write_dir_to_zip(cb_dir, zip, '/cookbooks/')
  
  # write the app dir to the zip
  zip.writestr('/%s/README.txt' % app_name, 'Hello from Boxcar! Put your application code in this directory.\n')

  # return the filepath of the zip
  return zipname

def _generate_vagrantfile(box, app_name, memory, recipes, ports=None):
  """
  From a template, generate a custom vagrantfile as defined by user
  """
  logger.info('Generating Vagrantfile')

  port_lines = ''
  if ports != None:
    print 'ports: ',ports
    for p in ports:
      port_lines += '\n  config.vm.forward_port %s, %s\n' % (p, p)
  
  logger.info('Configured port forwarding...')

  recipe_lines = ''
  for recipe in recipes:
    recipe_lines += '    chef.add_recipe \"%s\"\n' % recipe.name

  logger.info('Configured %d recipes...' % len(recipes))

  # generate final Vagrantfile from template
  template = Template(open('vagrantfile_template', 'r').read())
  return template.safe_substitute({'box':box, 'port_lines':port_lines, 'app_name':app_name, 'memory':memory, 'recipe_lines':recipe_lines})

def _write_dir_to_zip(target_dir, zip, zip_path):
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




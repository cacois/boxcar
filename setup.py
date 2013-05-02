from setuptools import setup

setup(name='Boxcar', 
      version='1.0',
      description='Boxcar: Vagrant on Rails',
      author='C. A. Cois', 
      author_email='aaron.cois@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',

      #  Uncomment one or more lines below in the install_requires section
      #  for the specific client drivers/modules your application needs.
      install_requires=[ 'Django >= 1.5',
                         'pymongo',
                         'requests' ],
      dependency_links = ['https://www.djangoproject.com/download/1.5/tarball/#egg=Django-1.5',]
     )

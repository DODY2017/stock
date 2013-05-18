To start, create the App Engine application root directory. From the Mac OS X or Linux command line, you would typically use these commands to make the directory and set it to be the current working directory:
 mkdir myapp
cd myapp

You create a new Django project by running a command called django-admin.py startproject. Run this command to create a project named myproject in a subdirectory called myproject/:
 python ~/google_appengine/lib/django_1_3/django/bin/django-admin.py \
    startproject myproject

This command creates the myproject/ subdirectory with several starter files:

__init__.py 
A file that tells Python that code files in this directory can be imported as modules (this directory is a Python package).
manage.py 
A command-line utility you will use to build and manage this project, with many features.
settings.py 
Configuration for this project, in the form of a Python source file.
urls.py 
Mappings of URL paths to Python code, as a Python source file.


Create a file named main.py in the application root directory with the following contents:
 import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

The first two lines tell Django where to find the project’s settings module, which in this case is at the module path myproject.settings (the myproject/settings.py file). This must be set before importing any Django modules. The remaining two lines import the WSGI adapter, instantiate it, and store it in a global variable.

Next, create app.yaml in the application root directory, like so:
application: myapp
version: 1
runtime: python27
api_version: 1
threadsafe: yes

handlers:
- url: .*
  script: main.application

libraries:
- name: django
  version: "1.3"

This should be familiar by now, but to review, this tells App Engine this is an application with ID myapp and version ID 1 running in the Python 2.7 runtime environment, with multithreading enabled. All URLs are routed to the Django project we just created, via the WSGI adapter instantiated in main.py. The libraries: declaration selects Django 1.3 as the version to use when importing django modules.

Our directory structure so far looks like this:
 myapp/
  app.yaml
  main.py
  myproject/
    __init__.py
    manage.py
    settings.py
    urls.py

	
With the current working directory still set to the application root, create a new app named bookstore for this project:
 python myproject/manage.py startapp bookstore

This creates the subdirectory myproject/bookstore, with four new files:

__init__.py 
A file that tells Python that code files in this directory can be imported as modules (this directory is a Python package).
models.py 
A source file for data models common to this app.
tests.py 
A starter file illustrating how to set up automated tests in Django.
views.py 
A source file for Django views (request handlers).

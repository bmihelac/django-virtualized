==================
django-virtualized
==================

Chef and Fabric scripts for provisioning Ubuntu server and django app.
Currently works with Vagrant.

Requirements
------------

* fabric
* vagrant (with base box which can be installed with 
  ``vagrant box add base http://files.vagrantup.com/precise32.box``)

Run
---

::

    git clone git@github.com:bmihelac/django-virtualized.git
    cd django-virtualized
    vagrant up
    fab -R vagrant vagrant bootstrap

This will install blank Django 1.4 application, which is accessible at:

http://localhost:8080

Author: Bojan Mihelac with some code and inspiration from:

* https://github.com/honza/django-chef

* http://ericholscher.com/blog/2010/nov/8/building-django-app-server-chef/

* http://vagrantup.com/, http://wiki.opscode.com/display/chef/Cookbooks and others

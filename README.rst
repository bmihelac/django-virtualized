==================
django-virtualized
==================

Chef and Fabric scripts for provisioning Ubuntu server and django app.

Vagrant, EC2.

Requirements
------------

* fabric
* apache-libcloud
* vagrant (with base box which can be installed with 
  ``vagrant box add base http://files.vagrantup.com/precise32.box``)

Install
-------

::

    git clone git@github.com:bmihelac/django-virtualized.git
    cd django-virtualized

Bootstraping
------------

Vagrant instance
^^^^^^^^^^^^^^^^

    vagrant up
    fab -R vagrant vagrant bootstrap

This will install blank Django 1.4 application, which is accessible at:

http://localhost:8080

EC2 instance
------------

1. Setup EC2 environment variables::

   export EC2_ACCESS_ID="ec2-access-id"
   export EC2_SECRET_KEY="ec2-secret-key"
   export EC2_KEYPATH="~/ec2.pem"

2. Create EC2 instance::

   fab ec2 ec2_create_instance

3. List EC2 instances::

   fab ec2 ec2_list_instances

4. Bootstrap instance

   ::

       fab --hosts=ubuntu@50.17.62.32 ec2 bootstrap

    Replace IP with one that was listed with ec2_list_instances.

About
-----

Author: Bojan Mihelac with some code and inspiration from:

* https://github.com/honza/django-chef

* http://ericholscher.com/blog/2010/nov/8/building-django-app-server-chef/

* http://vagrantup.com/, http://wiki.opscode.com/display/chef/Cookbooks and others

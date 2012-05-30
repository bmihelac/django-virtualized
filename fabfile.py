import os

from fabric.api import cd, env, prefix, sudo, local, settings, run
from contextlib import contextmanager
import libcloud
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeImage, NodeSize


libcloud.security.VERIFY_SSL_CERT = False


env.roledefs = {
    'vagrant': ['vagrant@127.0.0.1:2222'],
}
env.roledefs['ec2'] = []


env.project_name = "website"
env.chef_executable = 'chef-solo'


#EC2 account settings
EC2_ACCESS_ID = os.environ.get('EC2_ACCESS_ID', '')
EC2_SECRET_KEY = os.environ.get('EC2_SECRET_KEY', '')
EC2_KEYPATH = os.environ.get('EC2_KEYPATH', '')
# EC2 instance AMI
EC2_AMI = "ami-ac9943c5"
# EC2 instance size
EC2_INSTANCE_SIZE = "t1.micro"


def _setup_env():
    env.virtualenv = '%s/env' % env.root_dir
    env.activate = 'source %s/bin/activate ' % env.virtualenv

@contextmanager
def _virtualenv():
    with prefix(env.activate):
        yield


def vagrant():
    env.root_dir = '/home/vagrant/%s' % env.project_name
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]
    _setup_env()

def ec2():
    env.root_dir = '/home/ubuntu/%s' % env.project_name
    env.key_filename = EC2_KEYPATH
    basename = os.path.basename(EC2_KEYPATH)
    env.ec2_keyname = os.path.splitext(basename)[0]
    _setup_env()

def create_virtualenv():
    with cd(env.root_dir):
        run('virtualenv %s/env' % env.root_dir)


def install_chef():
    """
    Install chef-solo on the server
    """
    sudo('apt-get update', pty=True)
    sudo('apt-get install -y git-core rubygems ruby ruby-dev', pty=True)
    sudo('gem install chef --no-ri --no-rdoc', pty=True)


def sync_config():
    """
    rsync `deploy/` to the server
    """
    local('rsync -av -e "ssh -p %(port)s -i %(key_filename)s" --rsync-path="sudo rsync" deploy/ %(user)s@%(host)s:/etc/chef' % env)


def provision():
    """
    Run chef-solo
    """
    sync_config()
    sudo('cd /etc/chef && %s' % env.chef_executable, pty=True)


def pull():
    """
    Copy website to a server
    """
    local('rsync -av -e "ssh -p %(port)s -i %(key_filename)s" website/ %(user)s@%(host)s:%(project_name)s/' % env)

def enable_website():
    sudo("rm /etc/nginx/sites-enabled/default")
    sudo("ln -s ~/website/nginx/website.conf /etc/nginx/sites-enabled/website.conf")

def restart():
    """
    Reload nginx/gunicorn
    """
    with settings(warn_only=True):
        with cd(env.root_dir):
            pid = sudo('cat gunicorn.pid')
            sudo('find . -name "*.pyc" -exec rm {} \;')
            if not pid.succeeded:
                start_gunicorn()
            else:
                sudo('kill -HUP %s' % pid)
        restart_nginx()


def restart_nginx():
    sudo('/etc/init.d/nginx restart')


def start_gunicorn():
    with cd(env.root_dir):
        with _virtualenv():
            # see https://de.twitter.com/pyfabric/status/115848459386503168
            # gunicorn --daemon probably (?) creates a background process,
            # still attached to your shell session
            run('gunicorn website.wsgi:application --pid=gunicorn.pid & sleep 3')


def install_requirements():
    """
    Init django project
    """
    with cd(env.root_dir):
        with _virtualenv():
            run('pip install -r requirements.txt', pty=True)


def bootstrap():
    """
    Bootstrap server.
    """
    install_chef()
    provision()
    pull()
    create_virtualenv()
    install_requirements()
    enable_website()
    start_gunicorn()
    restart_nginx()

def ec2_connection():
    Driver = get_driver(Provider.EC2)
    conn = Driver(EC2_ACCESS_ID, EC2_SECRET_KEY)
    return conn

def ec2_create_instance():
    conn = ec2_connection()
    image = NodeImage(id=EC2_AMI, name="", driver="")
    size = NodeSize(
            id=EC2_INSTANCE_SIZE,
            name="", ram=None, disk=None, bandwidth=None, price=None, driver="")
    instance_name = "test"
    conn.create_node(name=instance_name, image=image, size=size,
            ex_keyname=env.ec2_keyname)

def ec2_list_instances():
    conn = ec2_connection()
    nodes = conn.list_nodes()
    for node in nodes:
        if node.public_ip:
            print node.public_ip[0]

from fabric.api import cd, env, prefix, sudo, local, settings, run
from contextlib import contextmanager


env.roledefs = {
    'vagrant': ['vagrant@127.0.0.1:2222']
}


env.project_name = "website"
env.root_dir = '/home/vagrant/%s' % env.project_name
env.virtualenv = '%s/env' % env.root_dir
env.activate = 'source %s/bin/activate ' % env.virtualenv
env.chef_executable = 'chef-solo'


@contextmanager
def _virtualenv():
    with prefix(env.activate):
        yield


def vagrant():
    if env.user == 'vagrant':
        result = local('vagrant ssh-config | grep IdentityFile', capture=True)
        env.key_filename = result.split()[1]


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

def nginx_symlink():
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
    provision()
    pull()
    create_virtualenv()
    install_requirements()
    nginx_symlink()
    restart()

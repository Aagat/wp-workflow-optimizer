#!/usr/bin/env python
from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

"""
Helper script for wordpress automation.
Author: Aagat Adhikari
Email: hi@aagat.com
Twitter: @theaagat
Website: http://www.aagat.com
Lincese: MIT
"""

#######################################################
##  CUSTOM CONFIGURATION
#######################################################

## Your remote servers' hostname or IP address. Information about port is not yet clear.
env.hosts = ['']

## Remote username to login as. Avoid using root when possible.
env.user = "root"

## Your private key for SSH connection.
env.key_filename = '~/.ssh/id_rsa'

## Your git repo
env.git_repo_url = 'git@github.com:Aagat/wp-workflow-optimizer.git'

## You might not have set proper SSH access from server. Use https url as a workaround
env.git_pull_repo_url = 'https://github.com/Aagat/wp-workflow-optimizer.git'

## Your git repo SSH key
## Coming soon

## Your remote application directory
env.remote_app_dir = '~/wordpress-app'

## Use docker in production or not. Set this to false if you do not want to install/use docker in production. Useful for shared hosts.
env.docker_deploy = True


#######################################################
## Global Configuration Menthods
#######################################################

@task
def dev():
    '''
    Set working environment to local workstation
    '''
    print('Executing commands in local workstation')
    env.destination = 'local'

@task
def remote():
    '''
    Set working environment to remote server
    '''
    print('Executing commands in remote server')
    env.destination = 'remote'

#######################################################
## defs
#######################################################

@task
def test_connection():
    """
    Test connection to the remote servers and print out uname information.
    """
    result = run("uname -a")
    if result.failed:
        _pretty_output("Could not connect to remote server. Please check your configuration")
        abort("Cannot continue. Aborting...")

@task
def prepare_server():
    '''
    Prepare server by installing required dependencies
    '''
    test_connection()
    prepare_server_with_docker() if env.docker_deploy else prepare_server_without_docker

def prepare_server_with_docker():
    '''
    Prepare server for docker based deployment.
    '''
    _pretty_output("Preparing Server with Docker")
    if is_available("docker") is False:
        # Docker might be old in repo, so let's use an script to do it for us.
        install("docker")

    if is_available("git") is False:
        install("git")

    if is_available("python -V") is False:
        install("python")

    if is_available("pip --version") is False:
        install("python-setuptools python-pip")

    if is_available("fig --version") is False:
    ## fig is not available in repo. Install it via pip
        run("pip install fig")

def prepare_server_without_docker():
    '''
    Prepare server for non docker based deployment.
    '''
    if is_available("git --version") is False:
        install("git")

@task
def deploy():
    if is_available("git --version") and is_available("docker --version"):
        deploy_with_docker()
    elif is_available("git --version"):
        deploy_with_git()
    else:
        deploy_with_sftp()

def deploy_with_docker():
    '''
    Deploy container based application to remote server
    '''
    # Pull code & Run Fig
    deploy_with_git()
    with cd(env.remote_app_dir):
        sudo("fig up -d")

def deploy_with_git():
    '''
    Deploy application using git
    '''
    # Pull code and clean directory.
    # Possibly checkout production branch
    local("git push origin master")
    ## git push origin production branch when that option is ready

    # Test if app directory exists. If not, create one.
    with settings(warn_only=True):
        if run( "test -d %s" % env.remote_app_dir ).failed:
            sudo("mkdir %s" % env.remote_app_dir)

    with settings(warn_only=True), cd(env.remote_app_dir):

        if run("test -d ./.git").failed:
            run("git clone %s ." % env.git_pull_repo_url )

        run("git pull")
        ## run('git checkout production')

def deploy_with_sftp():
    '''
    Deploy application using sftp is git is not preferred/installed.
    '''
    # Make tarball, upload and unpack
    # Possibly checkout to production branch before packing

@task
def commit():
    '''
    Commit current changes to the repo.
    '''
    with settings(warn_only=True):
        result = local("git branch")
        if result.failed:
            _pretty_output('No git repo detected in this directory')
            print('Don\'t worry, we\'ll create one for you')
            local("git init")
            local("git remote add origin " + env.git_repo_url )
            ## For now, let's assume whatever is inside dir is supposed to be inside the repo
            local("git add .")

    local("git add -p && git commit -a")

@task
def start():
    '''
    Starts containers in local or production
    '''
    _execute("fig up -d")
@task
def stop():
    '''
    Stops containers in local or production
    '''
    _execute("fig stop")

def prepare_local():
    '''
    Install dependencies in local debian based system
    '''

#######################################################
## HELPER METHODS
#######################################################

def _pretty_output(message):
    '''
    Print message in screen with some stylings.
    '''
    print('#' * 80)
    print('# ' + message + ' ' * (80 - (len(message) + 4) ) + ' #')
    print('#' * 80)

def is_os_supported():
    with hide("output"):
        result = run("apt-get")
        if result.failed:
            _pretty_output("Only debian based distros are supported at the moment")
            abort("This OS doesn\'t have apt-get. Exiting")

def install(package):
    is_os_supported()
    with settings( warn_only = True ):
        result = sudo("apt-get install -y %s " % package)

        if result.failed:
            _pretty_output("Something went wrong, do you want to continue?")
            if confirm(" "):
                return
@task
def is_available(package):
    with settings( warn_only =  True ), hide( 'output' ):
        result = sudo(package)
        if result.failed:
            _pretty_output("%s was not found in the server" % package )
            return False
        else:
            return True

def _execute(command):
    if env.local is 'local':
        local("sudo %s" % command)
    else:
    ## This is only used when we have root access to remote server. So it's alright
        with cd(env.remote_app_dir):
            sudo(command)

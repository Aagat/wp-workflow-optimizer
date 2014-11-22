#Optimized Wordpress Workflow

##Quick Tutorial
* Install dependencies
Install python, python-setuptools, python-pip:
```
sudo apt-get -y python python-setuptools python-pip
```

Install Docker (In host system)

```
curl -sSL https://get.docker.com/ubuntu/ | sudo sh
```

* Download this archive and extract

```
curl -O -L -C https://github.com/Aagat/wp-workflow-optimizer/archive/master.zip
```

* Edit config files

Edit fabfile.py inside the directory with your config and save.

* Develop

Run the following command to setup your work.

```
fab dev run
```

* Deploy

```
fab commit deploy dev start
```

##Command line options

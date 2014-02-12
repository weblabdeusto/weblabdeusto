# -*- mode: ruby -*-
# vi: set ft=ruby :

# A script to provision dependencies
$provision_script = <<SCRIPT
#!/bin/bash

# disable apt cache and compress apt lists to reduce disk footprint
echo 'Dir::Cache { srcpkgcache ""; pkgcache ""; }' > /etc/apt/apt.conf.d/02nocache
echo 'Acquire::GzipIndexes "true"; Acquire::CompressionTypes::Order:: "gz";' > /etc/apt/apt.conf.d/02compress-indexes

apt-get update -q
apt-get install -y curl git
apt-get install -q -y build-essential libxml2-dev libxslt1-dev libsqlite3-dev libmysqlclient-dev libsasl2-dev
apt-get install -q -y python-dev python-pip python-virtualenv virtualenvwrapper
apt-get install -q -y openjdk-7-jdk maven ant

# MySQL
MYSQL_PASSWORD=""
debconf-set-selections <<< 'mysql-server mysql-server/root_password password $MYSQL_PASSWORD'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password $MYSQL_PASSWORD'
apt-get install -q -y mysql-client mysql-server mysql-server-5.5

# Redis server
apt-get install -q -y redis-server

# dependencies for production installation
# apt-get install -q -y apache2
# to use threads (don't use if apache must support php)
# apt-get install -q -y apache2-mpm-worker 

# program provisioning
su - vagrant /weblabdeusto/vagrant-provision.sh
SCRIPT

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "precise64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network :forwarded_port, guest: 80, host: 8080
  config.vm.network :forwarded_port, guest: 8000, host: 8000
  config.vm.network :forwarded_port, guest: 3306, host: 8033

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", "/weblabdeusto", :mount_options => ["dmode=777,fmode=666"]

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider :virtualbox do |vb, override|
    # Don't boot with headless mode
    # vb.gui = true

    override.vm.provision :shell, :inline => $provision_script

    # Use VBoxManage to customize the VM. For example to change memory:
    vb.customize ["modifyvm", :id, "--memory", "1024"]

    # Customize CPU number
    # vb.customize ["modifyvm", :id, "--cpus", $vm_cpus]

    # This setting makes it so that network access from inside the vagrant guest
    # is able to resolve DNS using the hosts VPN connection.
    # v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  end

end

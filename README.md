# Build an Item Catalog
> Jintong Wu

## About
This is the fourth project for the Udacity Full Stack Nanodegree.
The Item Catalog project provides a list of items within a variety of
categories as well as provide a user registration and authentication system. 
Registered users will have the ability to post, edit and delete their own items.

## How to run it
What you need
* Vagrant
* VirtualBox

Download and login the vm
```
git clone https://github.com/udacity/fullstack-nanodegree-vm fsnd-vm
cd fsnd-vm/vagrant

vagrant up
vagrant ssh
```
beside libraries installed in the vm, you also need

* Flask-Dance
* Flask-Login

you can install all libraries needed  by
```
pip install -r requirements.txt
```
Download this project and setup databse
```
git clone https://github.com/akudet/fsnd-proj4.git
cd fsnd-proj4
python catalog_db_setup.py
```
Run it !!!
```
python app.py
```
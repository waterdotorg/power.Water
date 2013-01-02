ABOUT
-----
The power.Water codebase allows organizations to recruit, collect, manage, and then post content on users' accounts on both Facebook and Twitter. Users "donate their voice" by authorizing the power.Water site with their Facebook Connect or Twitter OAuth credentials. 

Administrators determine when a post will occur on user accounts. Content can be scheduled, includes unique identifying information for each user and post for tracking, can include photos on Facebook, and can include links to any resolvable URI on the web. Visit [power.Water.org Production Site](http://power.water.org)

QUICK INSTALL
-------------
Setup your [virtual environment](http://www.virtualenv.org/)

    $ virtualenv --system-site-packages foobar

Download the [power.water codebase](https://github.com/waterdotorg/power.Water)

Install local requirements within the virtualenv

    $ pip install -r requirements.txt

Required global packages

    $ apt-get install postgresql python-psycopg2 python-imaging

Setup Postgres Database

    $ su postgres
    $ createuser -P -E foobar
    $ createdb -E UTF8 -T template0 --owner=foobar foobar

Setup Django environment - [Quick install guide](https://docs.djangoproject.com/en/1.4/intro/install/)
    - See comments in settings_default.py file regarding private settings
    
Install fixtures

    $ python project/manage.py loaddata groups

Install Nginx and symlink config file

    $ apt-get install nginx
    $ ln -s /src/foobar/nginx/nginx.conf /etc/nginx/sites-enabled/foobar

Install Supervisor
    - best done outside virtualenv
    - see http://supervisord.org/installing.html

    $ pip install supervisor
    $ sudo echo_supervisord_conf > /etc/supervisord.conf
    $ mkdir /etc/supervisord/
    $ mkdir /var/log/supervisord

Create an init script so supervisor is started on boot. See the project supervisord/ folder for default
daemon scripts. At a minimum symlink from power.water_gunicorn.conf to /etc/supervisord/. Note: if you
enable either of the Facebook or Twitter daemons, you'll need to setup the appropriate apps on each platform
and then add your API keys. See the settings_default.py file for further comments.

LICENSE
-------
Copyright (C) 2012

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


CREDITS
-------
A project by [Water.org](http://water.org/). For more than two decades, Water.org has been at the forefront of developing and delivering solutions to the water crisis. Founded by Gary White and Matt Damon, Water.org pioneers innovative, community-driven and market-based solutions to ensure all people have access to safe water and sanitation; giving women hope, children health and communities a future. To date, Water.org has positively transformed the lives of more than 1,000,000 individuals living across communities in Africa, South Asia, Latin America and the Caribbean; ensuring a better life for generations ahead.

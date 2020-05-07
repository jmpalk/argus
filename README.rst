=====
Argus
=====


Argus is a Django app to run masscan scans and manage the results. It is
primarily intended for environments where assessors, security ops staff
or internal pentesters will be scannned repeatedly.

Scans generate data on Hosts, which have Ports and Services. Currently, 
results can be viewed on a scan basis, or by searching for hosts.

Quick Start
-----------

1. Add 'argus' to your INSTALLED_APPS setting like this::

	INSTALLED_APPS = [
		...
		'argus',
	]

2. Include the argus URLConf in your project urls.py like this::

	path('argus/', include('argus.urls')),

3. Run ``python manage.py migrate`` to create the argus models

4. Ensure masscan (https://github.com/robertdavidgraham/masscan) is installed
at /usr/local/bin/masscan

5. Copy wrapper.sh and run_masscan.py to your project directory. Ensure 
both are owned by root and are _not_writable.  wrapper.sh must be setuid root 
so that it can run masscan as root.

6. In run_masscan.py, set the os.environ.setdefault to point at your project's 
settings module like so::

	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "<<your project name>>.settings")


7. Create /opt/argus/scans/ to save scan data

8. Start the development server and visit http://127.0.0.1:8000/admin/ to 
create an admin user and any other users you need. By default, argus requires
authentication to access all functionality.

9. Visit http://127.0.0.1:8000/argus/ to login in to the system, launch scans 
and view results.

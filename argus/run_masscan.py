import re
from datetime import datetime, timezone
import os
import subprocess
import sys
from pathlib import Path
import ipaddress
import argparse
import json
import django
from django.conf import settings
from django.db import models

PROJECT_ROOT = Path(__file__)
sys.path.append(str(PROJECT_ROOT))

#Modify the below line to point at your own project settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ikkyu.settings")
django.setup()

from argus.models import Scan, Host, Port


MASSCAN = Path("/usr/local/bin/masscan")

def check_for_ip_bad_chars(test_string):
	working_string = test_string
	print(working_string)
	searchObj = re.sub("[\.,/\-0-9]", "", working_string)
	print(searchObj)
	print(len(searchObj))
	if len(searchObj) > 0:
		return(True)
	return(False)

def check_for_bad_port_chars(test_string):
	working_string = test_string
	searchObj = re.sub("[,\-0-9]", "", working_string)
	if len(searchObj) > 0:
		return(True)
	return(False)

parser = argparse.ArgumentParser(description='Run masscan with some given arguments and insert the results into the django db')
parser.add_argument('ips', nargs=1, help="ipv4 address or ipv4 ranges to scan")
parser.add_argument('ports', nargs=1, help="tcp ports to scan")
parser.add_argument('exclude', nargs=1, help="iv4 addresses to exclude")

args = parser.parse_args()
run_scan_range = args.ips[0]
run_port_range = args.ports[0]
exclude_range = args.exclude[0]

if exclude_range != "0.0.0.0":
	if check_for_ip_bad_chars(exclude_range):
		print("* %s is not a valid target ip or range" % (exclude_range))
		exit(-1)
	ip_ranges = exclude_range.split(',')
	for ip_range in ip_ranges:
		try:
			ipaddress.ip_network(ip_range)
		except:
			print("* %s is not a valid target ip or range" % (exclude_range))
			exit(-1)
	
		

	
#may need to push some of this back into views, or duplicate, so we can give feedback on bad 
#search parameters in the web app...
if check_for_ip_bad_chars(run_scan_range):
	print("* %s is not a valid target ip or range" % (run_scan_range))
	exit(-1)
if check_for_bad_port_chars(run_port_range):
	print("* %s is not a valid port range" % (run_port_range))
	exit(-1)

	
	
ip_ranges = run_scan_range.split(',')
for ip_range in ip_ranges:
	try:
		ipaddress.ip_network(ip_range)
	except:
		print("* %s is not a valid target ip or range" % (run_scan_range))
		exit(-1)
	

port_set = run_port_range.split(',')
for port in port_set:
	if port.find("-") != -1:
		(p1, p2) = port.split("-")
		p1 = int(p1)
		p2 = int(p2)
		if p1 >= p2:
			print("* %s is not a valid target port or ports" % (run_port_range))
			exit(-1)
		if not 0 < p1 and p1 < 65536:
			print("* %s is not a valid target port or ports" % (run_port_range))
			exit(-1)
		if not 0 < p2 and p2 < 65536:
			print("* %s is not a valid target port or ports" % (run_port_range))
			exit(-1)
	elif not 0 < int(port) and int(port) < 65536:
		print("* %s is not a valid target port or ports" % (run_port_range))
		exit(-1)
			
			
if not MASSCAN.is_file():
	print("* /usr/local/bin/masscan not found -- exiting *")
	exit(-1)

if not Path("/opt/argus/scans").exists():
	print("* /opt/argus/scans/ does not exist -- exiting *")
	exit(-1)
scan_time_raw = datetime.now(timezone.utc)
scan_time = scan_time_raw.strftime("%m%d%Y%H%M%S")	
output_filename = ("/opt/argus/scans/masscan_%s.json" % (scan_time))

#command = (("masscan %s -p%s --banners -oJ %s" %(run_scan_range, run_port_range, output_filename)))

#subprocess.Popen(command, shell=True)

command_list = ["masscan", run_scan_range, "-p", run_port_range, "--banners", "-oJ", output_filename, "--max-rate", "500", "--source-port", "61001"]

if exclude_range != "0.0.0.0":
	command_list.append("--excludefile")
	excludefile_name = scan_time + "exclude.txt"
	command_list.append(excludefile_name)
	excludefile = open(excludefile_name, "w")
	for excludeline in exclude_range.split(','):
		excludefile.write(excludeline+"\n")
	excludefile.close()


subprocess.run(command_list)

json_file = open(output_filename)
json_data = json.load(json_file)
db_scan_results = Scan(start_date = scan_time_raw, scan_range = run_scan_range, port_range = run_port_range)
db_scan_results.save()

recorded_hosts  = {}
recorded_ports = {}
for host in json_data:
	if host['ip'] in recorded_hosts:
		db_host = Host.objects.get(pk=recorded_hosts[host['ip']])
	else:
		db_host = db_scan_results.host_set.create(ip_address = host['ip'], host_scan_time = datetime.fromtimestamp(int(host['timestamp'])))
		recorded_hosts[host['ip']] = db_host.id
	for port in host['ports']:
		port_key = host['ip'] + "::" + str(port['port'])
		if port_key in recorded_ports:
			db_port = Port.objects.get(pk=recorded_ports[port_key])
			if 'status' in port:
				db_port.status = port['status']
				db_port.reason = port['reason']
			else:
				db_service = db_port.service_set.create(name=port['service']['name'], banner = port['service']['banner'])
				
		else:
			if 'status' in port:
				db_port = db_host.port_set.create(port_number = port['port'], status = port['status'], reason = port['reason'], protocol = port['proto'])
			else:
				db_port = db_host.port_set.create(port_number = port['port'], protocol = port['proto'])

			if 'service' in port:
				db_service = db_port.service_set.create(name=port['service']['name'], banner = port['service']['banner'])
				if 'https' in port['service']['banner'].lower():
					db_host.https_present = True
					common_service_present = True
	
				elif 'http' in port['service']['banner'].lower():
					db_host.http_present = True
					common_service_present = True
	
				elif 'ssh' in port['service']['banner'].lower():
					db_host.ssh_present = True
					common_service_present = True
	
				elif 'smb' in port['service']['banner'].lower():
					db_host.smb_present = True
					common_service_present = True
	
				elif 'rdp' in port['service']['banner'].lower():
					db_host.rdp_present = True
					common_service_present = True

				elif 'ftp' in port['service']['banner'].lower():
					db_host.ftp_present = True
					common_service_present = True
	
				elif 'telnet' in port['service']['banner'].lower():
					db_host.telnet_present = True
					common_service_present = True
	
	
				if common_service_present:
					db_host.save()
			recorded_ports[port_key] = db_port.id

			common_service_present = False



exit(0)

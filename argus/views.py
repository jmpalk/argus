from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from argus.models import Scan, Host, Port, Service
from django.views import generic
from django.urls import reverse
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib.auth.decorators import login_required
import os
import sys
import subprocess
import re
import ipaddress
from pathlib import Path
from .forms import HostSearchForm, LoginForm
import base64
import datetime
from datetime import datetime, timezone

#helper and data validation functions
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

# Create your views here.

#class HomeView(generic.ListView):
#	template_name = 'home.html'
#	context_object_name = 'latest_scan_list'
#
#
#	def get_queryset(self):
#		return Scan.objects.order_by('-start_date')[:5]


def logout_page(request):
	logout(request)
	return redirect('argus:login')

def login_page(request):
	if request.method == 'POST':
		login_form = LoginForm(request.POST)
	
		if login_form.is_valid():
			username = login_form.cleaned_data['username']
			password = login_form.cleaned_data['password']
			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('argus:scan_home')
			else:
				login_form = LoginForm()
				login_failed = True
				return render(request, 'login_page.html', {'login_form': login_form, 'login_failed': login_failed})
	
	else:
		login_form = LoginForm()
		
		return render(request, 'login_page.html', { 'login_form': login_form, })
		


@login_required(login_url='/argus/login/')
def home_page(request):
	latest_scan_list = Scan.objects.order_by('-start_date')[:5]
	
	host_search_form = HostSearchForm()
	
	return render(request, 'home.html', {'latest_scan_list': latest_scan_list, 'host_search_form': host_search_form})


def validate_date(date_string):

	if len(date_string) != 8:
		working_date = datetime.now(timezone.utc)
		return(working_date, "BADDATE")
	
	year = int(date_string[0:4])
	month = int(date_string[4:6])
	day = int(date_string[6:8])

	print("date: %d %d %d" %(day, month, year))

	try:
		working_date = datetime(year, month, day, tzinfo=timezone.utc)
	except:
		working_date = datetime.now(timezone.utc)
		print("WTF2")
		return(working_date, "BADDATE")
	return(working_date, "GOODDATE")
		

@login_required(login_url='/argus/login/')
def host_search_results(request):
	
	if request.method == 'POST':
		host_search_form = HostSearchForm(request.POST)

		if host_search_form.is_valid():
			host_ip = host_search_form.cleaned_data['host_ip']
			from_scan_date = host_search_form.cleaned_data['from_scan_date']
			to_scan_date = host_search_form.cleaned_data['to_scan_date']
	
			from_scan_date_raw = int(from_scan_date.strftime("%Y%m%d"))
			to_scan_date_raw = int(to_scan_date.strftime("%Y%m%d"))

			redirect_url = reverse('argus:hostsearchresults') + "?host_ip=%s&fsd=%d&tsd=%d&s=%d&c=%d" % (host_ip, from_scan_date_raw, to_scan_date_raw, 0, 5)

			return HttpResponseRedirect(redirect_url)
		else:
			print("foobar")
			return render(request, 'hostsearcherror.html')

	else:

		host_search_form = HostSearchForm()
		
		host_ip = request.GET.get('host_ip', '0.0.0.0')
		from_scan_date_raw = request.GET.get('fsd', '00000000')
		to_scan_date_raw = request.GET.get('tsd', '00000000')
		start = int(request.GET.get('s', 0))
		count = int(request.GET.get('c', 5))
			
		if from_scan_date_raw == '00000000':
			from_scan_date = datetime.now(timezone.utc)
		else:
			(from_scan_date, result_code) = validate_date(from_scan_date_raw)
			if result_code == "BADDATE":
				return render(request, 'hostsearcherror.html', {'BADDATE': True})
			
		if to_scan_date_raw == '00000000':
			to_scan_date = datetime.now(timezone.utc)
		else:
			(to_scan_date, result_code) = validate_date(to_scan_date_raw)
			if result_code == "BADDATE":
				return render(request, 'hostsearcherror.html', {'BADDATE': True})
			
		if from_scan_date > to_scan_date:
			print("WTF")
			return render(request, 'hostsearcherror.html', {'FLIPPEDDATES': True})
	
		host_set = Host.objects.filter(host_scan_time__gt=from_scan_date, host_scan_time__lt=to_scan_date, ip_address=host_ip).order_by('-host_scan_time')
		num_hosts = host_set.count()
	
		if start - count < 0:
			prev = 0
		else:
			prev = start - count
	
		if start + count >= num_hosts:
			next_set = -1
		else:
			next_set = start+count
	
		latest_scan_list = Scan.objects.order_by('-start_date')[:5]
	
		host_set = Host.objects.filter(host_scan_time__gt=from_scan_date, host_scan_time__lt=to_scan_date, ip_address=host_ip).order_by('-host_scan_time')[start:start+count]
	
		return render(request, 'host_search_results.html', {'host_set': host_set, 'host_ip': host_ip, 'from_scan_date': from_scan_date, 'to_scan_date': to_scan_date, 'start': start, 'count': count, 'num_hosts': num_hosts, 'latest_scan_list': latest_scan_list, 'prev': prev, 'next_set': next_set, 'host_search_form': host_search_form})
	




@login_required(login_url='/argus/login/')
def host_search_error(request, baddata):
	host_ip = base64.b64decode(baddata).strip()
	return render(request, 'hostsearcherror.html', {'host_ip': host_ip})


@login_required(login_url='/argus/login/')
def scan_detail(request, scan_id):
	start = int(request.GET.get('s', 0))
	count = int(request.GET.get('c', 5))

	if start - count < 0:
		prev = 0
	else:
		prev = start - count

	num_hosts = Scan.objects.get(pk=scan_id).host_set.all().count()
	if start + count >= num_hosts:
		next_set = -1
	else:
		next_set = start+count

	latest_scan_list = Scan.objects.order_by('-start_date')[:5]
	scan = get_object_or_404(Scan, pk=scan_id)
	hosts = scan.host_set.order_by('ip_address')[start:start+count]
	host_search_form = HostSearchForm()
	return  render(request, 'scan_detail.html', {'start': start, 'count': count, 'prev': prev, 'next_set': next_set, 'scan': scan, 'hosts': hosts, 'latest_scan_list': latest_scan_list, 'host_search_form': host_search_form})


@login_required(login_url='/argus/login/')
def scan_list(request):
	start = int(request.GET.get('s', 0))
	count = int(request.GET.get('c', 10))

	if start - count < 0:
		prev = 0
	else:
		prev = start - count

	num_scans = Scan.objects.all().count()
	if start + count >= num_scans:
		next_set = -1
	else:
		next_set = start+count

	scan_list = Scan.objects.order_by('-start_date')[start:start+count]
	latest_scan_list = Scan.objects.order_by('-start_date')[:5]
	host_search_form = HostSearchForm()
	return render(request, 'scan_list.html', {'start': start, 'count': count, 'scan_list': scan_list, 'latest_scan_list': latest_scan_list, 'prev': prev, 'next_set': next_set, 'host_search_form': host_search_form})


@login_required(login_url='/argus/login/')
def search_result_scan_list(request):
	start = int(request.GET.get('s', 0))
	count = int(request.GET.get('c', 10))

	if start - count < 0:
		prev = 0
	else:
		prev = start - count

	num_scans = Scan.objects.all().count()
	if start + count >= num_scans:
		next_set = -1
	else:
		next_set = start+count

	scan_list = Scan.objects.order_by('-start_date')[start:start+count]
	latest_scan_list = Scan.objects.order_by('-start_date')[:5]
	host_search_form = HostSearchForm()
	return render(request, 'scan_list.html', {'start': start, 'count': count, 'scan_list': scan_list, 'latest_scan_list': latest_scan_list, 'prev': prev, 'next_set': next_set, 'host_search_form': host_search_form})


@login_required(login_url='/argus/login/')
def host_detail(request, host_id):
	latest_scan_list = Scan.objects.order_by('-start_date')[:5]
	host = get_object_or_404(Host, pk=host_id)
	ports = host.port_set.all()
	host_search_form = HostSearchForm()
	return render(request, 'host_detail.html', {'host': host, 'ports': ports, 'latest_scan_list': latest_scan_list, 'host_search_form': host_search_form})



@login_required(login_url='/argus/login/')
def launch(request):
#	BASE_PATH = str(Path(__file__)).split('/')[1:-1] 
#	TOOLS_PATH = '/'
#	for part in BASE_PATH:
#		TOOLS_PATH = TOOLS_PATH + part + '/'
#	
#
#	TOOLS_PATH = TOOLS_PATH + 'tools/'
	
	#sys.path.append(str(TOOLS_PATH))
	#print(sys.path)

	scan_range = request.POST['scan_range']
	port_range = request.POST['port_range']
	exclude_range = request.POST['exclude_range']

	if check_for_ip_bad_chars(scan_range):
		return render(request, 'scanerror.html', {'scan_range': scan_range})
	if check_for_ip_bad_chars(exclude_range):
		return render(request, 'scanerror.html', {'exclude_range': exclude_range})
	if check_for_bad_port_chars(port_range):
		return render(request, 'scanerror.html', {'port_range': port_range})
	
		
		
	ip_ranges = scan_range.split(',')
	for ip_range in ip_ranges:
		try:
			ipaddress.ip_network(ip_range)
		except:
			return render(request, 'scanerror.html', {'scan_range': scan_range})
		
	ip_ranges = exclude_range.split(',')
	for ip_range in ip_ranges:
		try:
			ipaddress.ip_network(ip_range)
		except:
			return render(request, 'scanerror.html', {'exclude_range': exclude_range})
		
	
	port_set = port_range.split(',')
	for port in port_set:
		if port.find("-") != -1:
			(p1, p2) = port.split("-")
			p1 = int(p1)
			p2 = int(p2)
			if p1 >= p2:
				return render(request, 'scanerror.html', {'port_range': port_range})
			if not 0 < p1 and p1 < 65536:
				return render(request, 'scanerror.html', {'port_range': port_range})
			if not 0 < p2 and p2 < 65536:
				return render(request, 'scanerror.html', {'port_range': port_range})
		elif not 0 < int(port) and int(port) < 65536:
			return render(request, 'scanerror.html', {'port_range': port_range})

	command = ("python3 run_masscan.py %s %s %s &" % (scan_range, port_range, exclude_range))	
	subprocess.Popen(command, shell=True)
	return render(request, 'launch.html', {'scan_range': scan_range, 'exclude_range': exclude_range, 'port_range': port_range})

import datetime
from django.db import models
from django.utils import timezone

# Create your models here.

class Scan(models.Model):
	def __str__(self):
		return self.start_date.strftime("%d-%m-%y %H:%M:%S")

	def is_recent_scan(self):
		return self.start_date >= timezone.now() - datetime.timedelta(days=1)

	start_date = models.DateTimeField(null=True, blank=True)
	scan_range = models.CharField(max_length=254, default='')
	port_range = models.CharField(max_length=254, default='')
	

class Host(models.Model):
	def __str__(self):
		return self.ip_address

	ssh_present = models.BooleanField(default=False)
	http_present = models.BooleanField(default=False)
	https_present = models.BooleanField(default=False)
	ftp_present = models.BooleanField(default=False)
	telnet_present = models.BooleanField(default=False)
	rdp_present = models.BooleanField(default=False)
	smb_present = models.BooleanField(default=False)

	ip_address = models.TextField(default='')
	host_scan_time = models.DateTimeField(null=True, blank=True)
	scan = models.ForeignKey(Scan, on_delete = models.CASCADE)

class Port(models.Model):
	def __str__(self):
		return str(self.port_number)

	TCP = 'TCP'
	UDP = 'UDP'
	ARP = 'ARP'
	ICMP = 'ICMP'
	SCTP = 'SCTP'
	ERR = 'ERR'

	UNKNOWN = 'UNKNOWN'
	OPEN = 'OPEN'
	CLOSED = 'CLOSED'
	ARP = 'UP'

	PROTOCOL_CHOICES = [
		(TCP, 'tcp'),
		(UDP, 'udp'),
		(ARP, 'arp'),
		(ICMP, 'icmp'),
		(SCTP, 'sctp'),
		(ERR, 'err'),
	]
	STATUS_CHOICES = [
		(UNKNOWN, 'unknown'),
		(OPEN, 'open'),
		(CLOSED, 'closed'),
		(ARP, 'up'),
	]
	host = models.ForeignKey(Host, on_delete = models.CASCADE)
	port_number = models.IntegerField(default=0)
	protocol = models.CharField(max_length=4, choices=PROTOCOL_CHOICES, default=TCP)
	status =  models.CharField(max_length=7, choices=STATUS_CHOICES, default=CLOSED)
	reason =  models.CharField(max_length=8, default="")


class Service(models.Model):
	def __str__(self):
		return self.name

	port = models.ForeignKey(Port, on_delete = models.CASCADE)
	name = models.CharField(max_length=30, default='')
	banner = models.TextField(default='')

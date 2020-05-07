from django import forms
import datetime
from datetime import date, datetime, timezone
import ipaddress
import time


class LoginForm(forms.Form):
	username = forms.CharField(label='username', max_length=32)
	password = forms.CharField(label='password', max_length=32, widget=forms.PasswordInput())

class HostSearchForm(forms.Form):
	host_ip = forms.CharField(label='IP Address', max_length=18)
	from_scan_date = forms.DateField(
		widget = forms.SelectDateWidget(years={'2020': 2020, '2019': 2019, '2018': 2018, '2017': 2017, '2016': 2016}, months={ '01':('Jan'), '02':('Feb'), '03':('Mar'), '04':('Apr'),
    '05':('May'), '06':('Jun'), '07':('Jul'), '08':('Aug'),
    '09':('Sep'), '10':('Oct'), '11':('Nov'), '12':('Dec')}, empty_label=("Choose Year", "Choose Month", "Choose Day")),
	)
	to_scan_date = forms.DateField(
		widget = forms.SelectDateWidget(years={'2020': 2020, '2019': 2019, '2018': 2018, '2017': 2017, '2016': 2016}, months={ '01':('Jan'), '02':('Feb'), '03':('Mar'), '04':('Apr'),
    '05':('May'), '06':('Jun'), '07':('Jul'), '08':('Aug'),
    '09':('Sep'), '10':('Oct'), '11':('Nov'), '12':('Dec')}, empty_label=("Choose Year", "Choose Month", "Choose Day")),
	)

	def clean_host_ip(self):

		data = self.cleaned_data['host_ip']
		try:
			ipaddress.ip_network(data)
		except:
			print("IP Error")
			raise forms.ValidationError('Invalid IP Address')

		return data

	def clean_from_scan_date(self):
		data = self.cleaned_data['from_scan_date']
		print("clean from date")
		print(data.toordinal())
		print(date.fromtimestamp(time.time()).toordinal())

		if data > date.fromtimestamp(time.time()):
			raise forms.ValidationError('Invalid date - Date is in the future')
		
		return data

	def clean_to_scan_date(self):
		data = self.cleaned_data['to_scan_date']
		print("clean to date")

		print(data.toordinal())
		print(date.fromtimestamp(time.time()).toordinal())

		if data > date.fromtimestamp(time.time()):
			print("foo")
			raise ValidationError('Invalid date - Date is in the future')

		return data

	def clean(self):
		cleaned_data = super().clean()
		from_scan_date = cleaned_data['from_scan_date']
		to_scan_date = cleaned_data['to_scan_date']

		if from_scan_date > to_scan_date:
			print("bar")
			raise ValidationError(_('Invalid dates - Search range is inverted'))
	


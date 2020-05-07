from django.urls import resolve
from django.test import TestCase

from scans.views import home_page
from scans.models import Ip


class IpModelTest(TestCase):
	
	def test_saving_and_retrieving_items(self):
		first_ip = Ip()
		first_ip.address = '192.168.1.1'
		first_ip.save()

		second_ip = Ip()
		second_ip.address = '192.168.1.2'
		second_ip.save()

		saved_ips = Ip.objects.all()
		self.assertEqual(saved_ips.count(), 2)

		first_saved_ip = saved_ips[0]
		second_saved_ip = saved_ips[1]
		self.assertEqual(first_saved_ip.address, '192.168.1.1')
		self.assertEqual(second_saved_ip.address, '192.168.1.2')

class HomePageTest(TestCase):
	
	def test_home_page_returns_correct_html(self):
		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')

	def test_can_save_a_POST_request(self):
		self.client.post('/', data={'host_IP': '192.168.1.1'})
		self.assertEqual(Ip.objects.count(), 1)
		new_ip = Ip.objects.first()
		self.assertEqual(new_ip.address, '192.168.1.1')


	def test_redirects_after_POST(self):
		response = self.client.post('/', data={'host_IP': '192.168.1.1'})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')

	def test_only_queries_item_when_necessary(self):
		self.client.get('/')
		self.assertEqual(Ip.objects.count(), 0)


	def test_displays_all_scans(self):
		Ip.objects.create(address='192.168.1.1')
		Ip.objects.create(address='192.168.1.2')
		
		response = self.client.get('/')
		
		self.assertIn('192.168.1.1', response.content.decode())
		self.assertIn('192.168.1.2', response.content.decode())

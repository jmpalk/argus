from django.urls import path

from . import views

app_name = 'argus'
urlpatterns = [
	#ex: /argus/
	path('', views.home_page, name='scan_home'),
#	path('', views.HomeView.as_view(), name='scan_home'),
	#ex: argus/login
	path('login/', views.login_page, name='login'),
	#ex argus/logout/
	path('logout/', views.logout_page, name='logout'),
	#ex: /argus/scan_list/
	path('scan_list/', views.scan_list, name='scan_list'),
	#ex: /argus/scans/5/
	path('scans/<int:scan_id>/', views.scan_detail, name='scan_detail'),
	#ex: scans/host/5/
	path('host/<int:host_id>/', views.host_detail, name='host_detail'),
	#ex scans/launch/
	path('launch/', views.launch, name='launch'),
	#ex scans/scanerror
#	path('scanerror/', views.scanerror, name='scanerror')
#	ex scans/hostsearcherror
	path('hostsearcherror/<str:baddata>/', views.host_search_error, name='hostsearcherror'),
	path('hostsearchresults/', views.host_search_results, name='hostsearchresults')

]

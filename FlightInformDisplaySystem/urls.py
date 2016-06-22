from django.conf.urls import include, url
from django.contrib import admin
from flightinfosystem import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'FlightInformDisplaySystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^fids/', include('flightinfosystem.urls')),
    url(r'^$', views.index, name='index')
]

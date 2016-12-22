from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from flightinfosystem import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'FlightInformDisplaySystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^fids/', include('flightinfosystem.urls', namespace='fids')),
    url(r'^$', views.index, name='index')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

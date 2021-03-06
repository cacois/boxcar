from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'boxcar.views.home'),
    url(r'^generate$', 'boxcar.views.generate'),
    url(r'^about$', 'boxcar.views.about'),
    url(r'^get_cookbooks/$', 'boxcar.views.get_cookbooks'),
    url(r'^create_environment/$', 'boxcar.views.create_environment')
    # Examples:
    # url(r'^$', 'boxcar.views.home', name='home'),
    # url(r'^boxcar/', include('boxcar.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

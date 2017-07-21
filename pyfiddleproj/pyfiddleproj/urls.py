from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

handler400 = 'pyfiddleweb.views.error_page'
handler403 = 'pyfiddleweb.views.error_page'
handler404 = 'pyfiddleweb.views.error_page'
handler500 = 'pyfiddleweb.views.error_page'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('', include('social_django.urls', namespace='social')),
    url('', include('pyfiddleweb.urls', namespace='pyfiddleweb'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

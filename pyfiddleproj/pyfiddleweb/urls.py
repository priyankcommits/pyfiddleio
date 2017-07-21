from django.conf.urls import url

from .views import logout
from .views import home, run, upload, fiddle, email_send, privacy
from .views import save, star, delete, share, file_delete, success, cancel

urlpatterns = [
    url(r'login/', home, name='login'),
    url(r'logout/', logout, name='logout'),
    url(r'^$', home, name='home'),
    url(
        r'^fiddle/(?P<fiddle_id>[0-9a-f-]+)/',
        fiddle,
        name='fiddle'
    ),
    url(r'run/', run, name='run'),
    url(r'save/', save, name='save'),
    url(r'upload/', upload, name='upload'),
    url(r'star/', star, name='star'),
    url(r'share/', share, name='share'),
    url(r'file_delete/', file_delete, name='file_delete'),
    url(r'delete/', delete, name='delete'),
    url(r'email/', email_send, name='email'),
    url(r'privacy/', privacy, name='privacy'),
    url(r'success/', success, name="success"),
    url(r'cancel/', cancel, name="cancel"),
]

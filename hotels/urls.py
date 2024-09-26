from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('hotel_list/',views.hotel_list, name='room' ),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path("login/", views.login, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signup/", views.signup, name="signup"),
    path('preferences/', views.user_preferences, name='user_preferences'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
    path('contact/', views.contact, name='contact'),
    path('profile_update/', views.profile_update, name='profile_update'),
    path('results/', views.results, name='results')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
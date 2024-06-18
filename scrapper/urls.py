from django.urls import path
from .views import MattressScrapperView

urlpatterns = [
    path('mattress/<str:asin>/', MattressScrapperView.as_view(), name='mattress_scrapper')
]
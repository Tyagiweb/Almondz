from django.urls import path
from . import views
from .views import download_from_s3,delete_from_s3,upload_to_s3
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('add-expense/<str:username>/', views.add_expense, name='add_expense'),
    path('expense-added/', views.expense_added, name='expense_added'),
    path('upload-to-s3/', upload_to_s3, name='upload_to_s3'),
    path('download-from-s3/', download_from_s3, name='download_from_s3'),
    path('delete-from-s3/', delete_from_s3, name='delete_from_s3'),

]
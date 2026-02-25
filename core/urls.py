from django.urls import path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from views import index_redirect, login_view, logout_view, warehouse_view

urlpatterns = [
    path('', index_redirect, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('warehouse/', warehouse_view, name='warehouse'),
]

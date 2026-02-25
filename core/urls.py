from django.urls import path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from views import (
    index_redirect, login_view, logout_view, 
    warehouse_view, item_add_view, item_detail_view, 
    item_edit_view, item_delete_view
)

urlpatterns = [
    path('', index_redirect, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('warehouse/', warehouse_view, name='warehouse'),
    path('warehouse/add/', item_add_view, name='item_add'),
    path('warehouse/item/<int:item_id>/', item_detail_view, name='item_detail'),
    path('warehouse/item/<int:item_id>/edit/', item_edit_view, name='item_edit'),
    path('warehouse/item/<int:item_id>/delete/', item_delete_view, name='item_delete'),
]

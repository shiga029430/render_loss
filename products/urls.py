from django.urls import path
from .views import ProductListView, ProductDisplayView, DisplayEditView
from . import views

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('product_display/', ProductDisplayView.as_view(), name='product_display'),
    path('display_edit/', DisplayEditView.as_view(), name='display_edit'),  # クラスビューを指定
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    
]

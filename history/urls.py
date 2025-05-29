from django.urls import path
# from .views import LossByDateView, LossDetailView
from . import views

app_name = 'history'

urlpatterns = [
    # 他のURLパターン
    path('', views.loss_history, name='loss_history'),
    # path('loss_by_date/', LossByDateView.as_view(), name='loss_by_date'),
    path('<int:loss_id>/', views.loss_detail, name='loss_detail'),
]
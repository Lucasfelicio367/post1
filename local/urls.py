

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('vloc', views.vloc, name='vloc'),
    path('vlocs/<insc_id>', views.vlocs, name='vlocs'),
    path('new_local', views.new_local, name='new_local'),
    path('new_ocorrencia/<int:insc_id>/', views.new_ocorrencia, name='new_ocorrencia'),
    path('edit_ocorrencia/<ocorr_id>/', views.edit_ocorrencia, name='edit_ocorrencia'),
    path('relatorio/pdf/', views.gerar_relatorio_pdf, name='gerar_relatorio_pdf'),
    path('relatorio_local/<int:insc_id>/', views.gerar_relatorio_local_pdf, name='gerar_relatorio_local_pdf'),
]

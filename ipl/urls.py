from django.contrib import admin
from django.urls import path, include
from . import views

from django.views.generic import TemplateView

appname='ipl'

urlpatterns = [
    # path('', TemplateView.as_view(template_name="index.html")),
    path('', views.Index.as_view(), name='index'),
    path('ipl-match-stats/<int:season>/', views.IPLMatchStats.as_view(), name='ipl-match-stats'),
    # path('top-four-teams/<int:>/', views.TopFourTeams.as_view(), name='top_four_team'),
    # path('top-one-team', views.TopOneTeams.as_view(), name='top_one_team')

]

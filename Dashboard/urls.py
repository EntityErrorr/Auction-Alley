from django.urls import path

from . import views

urlpatterns = [
    path("AuctionItem/<int:auction_id>", views.AuctionItem, name="AuctionItem"),
]
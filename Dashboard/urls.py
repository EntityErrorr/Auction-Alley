from django.urls import path
from . import views
app_name = 'dashboard'

urlpatterns = [
    path("AuctionItem/<int:auction_id>", views.AuctionItem, name="AuctionItem"),
    path("AuctionItem/<int:auction_id>/comment", views.comment, name="comment"),
    path("Live_Auction/", views.LiveAuction, name="LiveAuction"),
    path("AuctionItem/<int:auction_id>/bid_placement", views.bitplacement, name="bitplacement"),
    # path('', views.index, name='index'),


]



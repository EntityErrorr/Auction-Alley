from django.urls import path
from . import views
app_name = 'dashboard'

urlpatterns = [
    path("AuctionItem/<int:auction_id>", views.AuctionItem, name="AuctionItem"),
    path("AuctionItem/<int:auction_id>/comment", views.comment, name="comment"),
    path("Live_Auction/", views.LiveAuction, name="LiveAuction"),
    path('auction/<int:auction_id>/', views.auction_detail, name='auction-detail'),
    
    path("AuctionItem/<int:auction_id>/bid_placement", views.auction_detail, name="item2"),
]
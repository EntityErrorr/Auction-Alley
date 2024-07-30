from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path("AuctionItem/<int:auction_id>", views.AuctionItem, name="AuctionItem"),
    path("AuctionItem/<int:auction_id>/comment", views.comment, name="comment"),
    path('create_auction/', views.create_auction, name='create_auction'),
    path("Live_Auction/", views.LiveAuction, name="LiveAuction"),
    path("Admin_approve/", views.adminapprove, name="adminapprove"),
    path("Manage_Slots/", views.Manageslot, name="manageslot"),
    path("Create_Slots/", views.Createslot, name="createslot"),
    path('update-slot/<str:id>',views.UpdateSlot,name='updateSlot'),
    path('delete-slot/<str:id>',views.DeleteSlot, name='deleteSlot'),
    path('book-slot/<str:id>',views.BookSlot,name='bookSlot'),
    path('advisors/',views.Advisor_Page,name='advisors'),
    path('advisors/<str:id>',views.Advisor_Inside,name='advisorInside'),
    path("AuctionItem/<int:auction_id>/bid_placement", views.bitplacement, name="bitplacement"),
    path('AuctionItem/<int:auction_id>/load_bids/', views.load_bids, name='load_bids'),
    path('search/', views.search_auctions, name='search_auctions'),
    path('Advanced_search/', views.advanced_search_properties, name='advanced_search_properties'),
    path('refund/', views.refund_request, name='refund'),
    path('end_auction/<int:auction_id>/', views.end_auction, name='end_auction'),
    path('past-auctions/', views.past_auctions, name='past_auctions'),
    path('seller/<int:seller_id>/', views.seller_profile, name='seller_profile'),
    path('winner-bid-profile/', views.winner_bid_profile, name='winner_bid_profile'),
    path('purchase/<int:auction_id>/', views.purchase_process, name='purchase_process'),

    path('watchlist/add/<int:auction_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:auction_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/', views.view_watchlist, name='view_watchlist'),
]






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
]
    # path('', views.index, name='index'),






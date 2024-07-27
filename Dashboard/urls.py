from django.urls import path
from . import views
app_name = 'dashboard'

urlpatterns = [
    path("AuctionItem/<int:auction_id>", views.AuctionItem, name="AuctionItem"),
    path("AuctionItem/<int:auction_id>/comment", views.comment, name="comment"),
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
]
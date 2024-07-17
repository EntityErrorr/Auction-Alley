from django.db import models
from django.contrib.auth.models import User

# define the models of category
class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"

# define the model of a auction list
# class Auction(models.Model):
#     title = models.CharField(max_length=64)
#     description = models.TextField(max_length=512)
#     address = models.CharField(max_length=255)
#     starting_bid = models.IntegerField()
#     current_bid = models.IntegerField(default=0)
#     current_bid_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, related_name='bids_made')
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="auction_category", blank=True, null=True) 
#     seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_seller")
#     creation_date = models.DateTimeField(auto_now_add=True)
#     end_time = models.DateTimeField(blank=True, null=True)
#     image = models.ImageField(upload_to='auction_item_images/', blank=True, null=True)

#     APPROVAL_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ]
#     approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')

#     def __str__(self):
#         return f"Auction id: {self.id} | Title: {self.title} | Seller: {self.seller} | Status: {self.approval_status}"
    
#     def get_fields(self):
#         return [(field.name, getattr(self, field.name)) for field in Auction._meta.fields]

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    address = models.CharField(max_length=255)
    starting_bid = models.IntegerField(help_text="Starting bid amount in BDT")
    current_bid = models.IntegerField(default=0, help_text="Current bid amount in BDT")
    current_bid_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='bids_made')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="auction_category", blank=True, null=True) 
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_seller")
    creation_date = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='auction_item_images/', blank=True, null=True)

    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')

    def __str__(self):
        return f"Auction id: {self.id} | Title: {self.title} | Seller: {self.seller} | Status: {self.approval_status}"
    
    def get_fields(self):
        return [(field.name, getattr(self, field.name)) for field in Auction._meta.fields]

# define the model of a bid
class Bid(models.Model):
    bider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_date = models.DateTimeField(auto_now_add=True)
    bid_price = models.DecimalField(max_digits=9, decimal_places=2)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_bids")

    def __str__(self):
        return f"{self.bider} bid ${self.bid_price} on {self.auction}"
    

# define the model of a comment
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    headline = models.CharField(max_length=64)
    message = models.TextField(blank=False)
    cm_date = models.DateTimeField(auto_now_add=True)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction_comments")

    def __str__(self):
        return f"{self.user} comments on {self.auction}"

# define the model of a watchlist
class Watchlist(models.Model):
    auctions = models.ManyToManyField(Auction, related_name="auctions_in_watchlist", blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.user}'s watchlist"
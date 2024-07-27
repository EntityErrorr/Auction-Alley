from django.db import models
from django.contrib.auth.models import User

# define the models of category
class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"

# define the model of a auction list
class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=512)
    address = models.CharField(max_length=255)
    starting_bid = models.IntegerField()
    current_bid = models.IntegerField(default=0)
    current_bid_by = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True, related_name='bids_made')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="auction_category", blank=True, null=True) 
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_seller")
    creation_date = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    house_size = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='auction_item_images/')
    # latitude = models.FloatField(null=True, blank=True)
    # longitude = models.FloatField(null=True, blank=True)

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
    
    # def save(self, *args, **kwargs):
    #     if not self.latitude or not self.longitude:
    #         self.latitude, self.longitude = fetch_coordinates(self.address)
    #     super().save(*args, **kwargs)

# define the model of a bid
class Bid(models.Model):
    bider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_date = models.DateTimeField(auto_now_add=True)
    bid_price = models.IntegerField()
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
    

#define the model of advisor
class Advisorslot(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE, related_name='slot')
    d_type = [
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thrusday', 'Thrusday'),
        ('friday', 'Friday'),
    ]
    day =models.CharField(max_length=20, choices=d_type)
    start_time= models.TimeField()
    end_time=models.TimeField()
    message=models.TextField(null=True,blank=True)
    max_user=models.IntegerField(default=10)
    total_user=models.IntegerField(default=0, blank=True, null=True)
    meet_link=models.CharField(max_length=250,null=True,blank=True)
    booked_user_list= models.ManyToManyField(User,blank=True,related_name='booked_User')

    def __str__(self) :
        return f"{self.user.username}'s {self.day}'s slot"
    

#define the model of refund
class RefundRequest(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    reason = models.TextField()
    bank_branch = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reason  
    
# from django.db import models
# from opencage.geocoder import OpenCageGeocode

# def fetch_coordinates(address):
#     key = '2139a598829e40faa98ee40396028537' 
#     geocoder = OpenCageGeocode(key)
#     results = geocoder.geocode(address)
#     if results:
#         return results[0]['geometry']['lat'], results[0]['geometry']['lng']
#     return None, None

from django.forms import ModelForm
from django import forms
from .models import Auction, Bid, Comment 

# create a new auction listing model form class



# create a new Comment model from class
class NewCommentForm(ModelForm):
    # sepcifit the name of model to use
    class Meta:
        model = Comment
        fields = ["headline", "message"]
        widgets = {
            "headline": forms.TextInput(
                attrs={
                        "placeholder": "Enter headline",
                        "class": "form-control"
                    }
            ),
            "message": forms.Textarea(
                attrs={
                        "placeholder": "Enter your comment...",
                        "class": "form-control",
                        "rows": 4
                    }
        )}


# forms.py
from django import forms
from .models import Bid

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_price']
        widgets = {
            'bid_price': forms.NumberInput(attrs={'min': 1, 'step': 1}),
        }
from django.forms import ModelForm
from django import forms
from .models import Auction, Bid, Comment,Advisorslot,RefundRequest


class AuctionItemForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'address', 'starting_bid', 'image', 'category', 'house_size']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class NewCommentForm(ModelForm):
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

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid_price']
        widgets = {
            'bid_price': forms.NumberInput(attrs={'min': 1, 'step': 1}),
        }


class CreateSlotForm(forms.ModelForm):
    class Meta:
        model=Advisorslot
        fields=['day','start_time','end_time','message','meet_link','max_user']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'message': forms.Textarea(attrs={'placeholder': 'Enter message'}),
            'meet_link': forms.TextInput(attrs={'placeholder': 'Enter meeting link'}),
        }


class UpdateSlotForm(forms.ModelForm):
    class Meta:
        model=Advisorslot
        fields=['day','start_time','end_time','message','meet_link','max_user']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'message': forms.Textarea(attrs={'placeholder': 'Enter message'}),
            'meet_link': forms.TextInput(attrs={'placeholder': 'Enter meeting link'}),
        }

class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['reason', 'bank_branch', 'bank_account_number']
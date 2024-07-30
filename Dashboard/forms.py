from django.forms import ModelForm
from django import forms
from .models import Auction, Bid, Comment,Advisorslot,RefundRequest
from django.forms.widgets import DateTimeInput

class AuctionItemForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = [
            'title', 
            'description', 
            'address', 
            'starting_bid', 
            'image', 
            'category', 
            'house_size', 
            'creation_date', 
            'end_time'
        ]
        widgets = {
            'creation_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Auction Title',
            'description': 'Description',
            'address': 'Address',
            'starting_bid': 'Starting Bid',
            'image': 'Auction Image',
            'category': 'Category',
            'house_size': 'House Size',
            'creation_date': 'Creation Date',
            'end_time': 'End Time',
        }
        help_texts = {
            'creation_date': 'Select the date and time when the auction was created.',
            'end_time': 'Select the end date and time for the auction.',
        }

    def clean(self):
        cleaned_data = super().clean()
        creation_date = cleaned_data.get('creation_date')
        end_time = cleaned_data.get('end_time')
        
        if creation_date and end_time and end_time <= creation_date:
            self.add_error('end_time', 'End time must be after the creation date.')

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
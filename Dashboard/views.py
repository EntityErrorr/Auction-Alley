from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from .models import User, Auction, Bid, Category, Comment, Watchlist
from .forms import NewCommentForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def AuctionItem(request, auction_id):  
    # get the auction AuctionItem by id
    auction = Auction.objects.get(pk=auction_id)
    # set watching flag be False as default
    watching = False
    # set the highest bidder is None as default    
    highest_bidder = None

    # check if the auction in the watchlist
    if request.user.is_authenticated and Watchlist.objects.filter(user=request.user, auctions=auction):
        watching = True
    
    # get the page request user
    user = request.user

    # get the number of bids
    bid_Num = Bid.objects.filter(auction=auction_id).count()

    # get all comments of the auction
    comments = Comment.objects.filter(auction=auction_id).order_by("-cm_date")

    # get the highest bids of the aunction
    highest_bid = Bid.objects.filter(auction=auction_id).order_by("-bid_price").first()

    if request.method == "GET":
        commentForm = NewCommentForm()
        return render(request, "AuctionItem.html", {
            "auction": auction,
            "user": user,
            "bid_Num": bid_Num,
            "commentForm": commentForm,
            "comments": comments,
            "watching": watching }) 

        
@login_required
def comment(request, auction_id):
    auction = Auction.objects.get(pk=auction_id) 
    if request.method == "POST":
        form = NewCommentForm(request.POST, request.FILES)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.auction = auction
            new_comment.save()
            return HttpResponseRedirect(reverse("dashboard:AuctionItem", args=(auction.id,)))
    else:
        form = NewCommentForm()
        return render(request, "AuctionItem.html", {'form':form})

def LiveAuction(request):
    live_auctions = Auction.objects.filter(
        approval_status='approved',
        end_time__gt=timezone.now()
    ).order_by('-creation_date')
    print(live_auctions)
    return render(request, "home.html", {"auctions": live_auctions})



from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Auction, Bid
from .forms import BidForm

@login_required
def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = BidForm(request.POST)
        if form.is_valid():
            bid_price = form.cleaned_data['bid_price']
            if bid_price > auction.current_bid:
                try:
                    # Create and save the new bid
                    new_bid = Bid(
                        bider=request.user,
                        bid_date=timezone.now(),
                        bid_price=bid_price,
                        auction=auction
                    )
                    new_bid.save()

                    # Update the current bid of the auction
                    auction.current_bid = bid_price
                    auction.save()

                    return JsonResponse({
                        'success': True,
                        'current_bid': bid_price,
                        'message': 'Your bid has been placed successfully!'
                    })
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'Error: {str(e)}'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Your bid must be higher than the current bid.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid bid form.',
                'errors': form.errors.as_json()  # Add form errors to the response
            })

    # Render the auction detail page
    bid_form = BidForm()
    context = {
        'auction': auction,
        'bid_form': bid_form,
    }
    return render(request, 'auction_detail.html', context)




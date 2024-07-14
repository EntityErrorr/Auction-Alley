from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import User, Auction, Bid, Category, Comment, Watchlist
from .forms import NewCommentForm, NewBidForm
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
    
    # check the request method is POST
    if request.method == "GET":
        form = NewBidForm()
        commentForm = NewCommentForm()
        return render(request, "AuctionItem.html", {
            "auction": auction,
            # "form": form,
            "user": user,
            "bid_Num": bid_Num,
            "commentForm": commentForm,
            "comments": comments,
            "watching": watching
            }) 

        # # check if the auction AuctionItem is not closed
        # if not auction.closed:
        #     return render(request, "auctions/AuctionItem.html", {
        #     "auction": auction,
        #     "form": form,
        #     "user": user,
        #     "bid_Num": bid_Num,
        #     "commentForm": commentForm,
        #     "comments": comments,
        #     "watching": watching
        #     }) 

        # # the auction is closed
        # else:
        #     # check the if there is bid for the auction AuctionItem
        #     if highest_bid is None:
        #         messages.info(request, 'The bid is closed and no bidder.')

        #         return render(request, "auctions/listing.html", {
        #             "auction": auction,
        #             "form": form,
        #             "user": user,
        #             "bid_Num": bid_Num,
        #             "highest_bidder": highest_bidder,
        #             "commentForm": commentForm,
        #             "comments": comments,
        #             "watching": watching
        #         })

        #     else:
        #         # assign the highest_bidder
        #         highest_bidder = highest_bid.bider

        #         # check the request user if the bid winner    
        #         if user == highest_bidder:
        #             messages.info(request, 'Congratulation. You won the bid.')
        #         else:
        #             messages.info(request, f'The winner of the bid is {highest_bidder.username}')

        #         return render(request, "auctions/listing.html", {
        #         "auction": auction,
        #         "form": form,
        #         "user": user,
        #         "highest_bidder": highest_bidder,
        #         "bid_Num": bid_Num,
        #         "commentForm": commentForm,
        #         "comments": comments,
        #         "watching": watching
        #         })

    
    # listing itself does not support POST method
    else:
        return render(request, "AuctionItem.html", {
            "auction": auction,
            # "form": form,
            "user": user,
            "bid_Num": bid_Num,
            "commentForm": commentForm,
            "comments": comments,
            "watching": watching
            }) 
        
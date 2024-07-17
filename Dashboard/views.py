from django.shortcuts import get_object_or_404, render, redirect
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.utils import timezone

from .models import User, Auction, Bid, Category, Comment, Watchlist
from .forms import NewCommentForm,BidForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

# views.py
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from .models import Auction, Bid, Comment, Watchlist
from .forms import NewCommentForm

def AuctionItem(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    now = timezone.now()
    time_left = auction.end_time - now
    seconds_left = time_left.total_seconds()

    # Ensure the auction is still active
    if seconds_left < 0:
        seconds_left = 0

    # Other existing code for getting bids, comments, etc.
    bid_Num = Bid.objects.filter(auction=auction_id).count()
    comments = Comment.objects.filter(auction=auction_id).order_by("-cm_date")
    highest_bid = Bid.objects.filter(auction=auction_id).order_by("-bid_price").first()
    watching = False
    if request.user.is_authenticated and Watchlist.objects.filter(user=request.user, auctions=auction):
        watching = True

    if request.method == "GET":
        commentForm = NewCommentForm()
        return render(request, "AuctionItem.html", {
            "auction": auction,
            "user": request.user,
            "bid_Num": bid_Num,
            "commentForm": commentForm,
            "comments": comments,
            "watching": watching,
            "seconds_left": seconds_left,
        })


        
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

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
#         if form.is_valid():
#             bid_price = form.cleaned_data['bid_price']
#             if bid_price > auction.current_bid:
#                 try:
#                     # Create and save the new bid
#                     new_bid = Bid(
#                         bider=request.user,
#                         bid_date=timezone.now(),
#                         bid_price=bid_price,
#                         auction=auction
#                     )
#                     new_bid.save()

#                     # Update the current bid of the auction
#                     auction.current_bid = bid_price
#                     auction.save()

#                     return JsonResponse({
#                         'success': True,
#                         'current_bid': bid_price,
#                         'message': 'Your bid has been placed successfully!'
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'message': f'Error: {str(e)}'
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Your bid must be higher than the current bid.'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid form.',
#                 'errors': form.errors.as_json()  # Add form errors to the response
#             })

#     # Render the auction detail page
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)
# from django.shortcuts import get_object_or_404, render, redirect
# from django.http import JsonResponse
# from django.utils import timezone
# from django.contrib.auth.decorators import login_required
# from .models import Auction, Bid
# from .forms import BidForm

# from django.shortcuts import get_object_or_404, render, redirect
# from django.http import JsonResponse
# from django.utils import timezone
# from django.contrib.auth.decorators import login_required
# from .models import Auction, Bid
# from .forms import BidForm

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
#         if form.is_valid():
#             bid_price = form.cleaned_data['bid_price']
#             if bid_price > auction.current_bid:
#                 try:
#                     # Create and save the new bid
#                     new_bid = Bid(
#                         bider=request.user,
#                         bid_date=timezone.now(),
#                         bid_price=bid_price,
#                         auction=auction
#                     )
#                     new_bid.save()

#                     # Update the current bid of the auction
#                     auction.current_bid = bid_price
#                     auction.save()

#                     return JsonResponse({
#                         'success': True,
#                         'current_bid': f'${bid_price:.2f}',
#                         'message': 'Your bid has been placed successfully!'
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'message': f'Error: {str(e)}'
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Your bid must be higher than the current bid and the starting bid.'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid form.',
#                 'errors': form.errors.as_json()  # Add form errors to the response
#             })

#     # Render the auction detail page
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)


# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
#         if form.is_valid():
#             bid_price = form.cleaned_data['bid_price']
#             starting_bid = auction.starting_bid  # Get the starting bid from the auction
            
#             if bid_price > starting_bid:
#                 try:
#                     # Create and save the new bid
#                     new_bid = Bid(
#                         bider=request.user,
#                         bid_date=timezone.now(),
#                         bid_price=bid_price,
#                         auction=auction
#                     )
#                     new_bid.save()

#                     # Update the current bid of the auction
#                     auction.current_bid = bid_price
#                     auction.save()

#                     return JsonResponse({
#                         'success': True,
#                         'current_bid': f'${bid_price:.2f}',
#                         'message': 'Your bid has been placed successfully!',
#                         'bider': request.user.username,
#                         'bid_price': f'${bid_price:.2f}',
#                         'bid_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'message': f'Error: {str(e)}'
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Your bid must be higher than the starting bid.'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid form.'
#             })

#     # Fetch the bids for the auction
#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')

#     # Render the auction detail page
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bids': bids,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
#         if form.is_valid():
#             bid_price = form.cleaned_data['bid_price']
#             starting_bid = auction.starting_bid  # Get the starting bid from the auction
            
#             if bid_price > starting_bid:
#                 try:
#                     # Create and save the new bid
#                     new_bid = form.save(commit=False)
#                     new_bid.bider = request.user  # Assign the bidder (current logged-in user)
#                     new_bid.bid_date = timezone.now()
#                     new_bid.auction = auction
#                     new_bid.save()

#                     # Update the current bid of the auction
#                     auction.current_bid = bid_price
#                     auction.save()

#                     # Send email notifications to seller and bidder (code for sending emails is omitted here for brevity)

#                     return JsonResponse({
#                         'success': True,
#                         'current_bid': f'${bid_price:.2f}',
#                         'message': 'Your bid has been placed successfully!',
#                         'bidder': request.user.username,
#                         'bid_price': f'${bid_price:.2f}',
#                         'bid_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'message': f'Error: {str(e)}'
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Your bid must be higher than the starting bid.'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid form.'
#             })

#     # Fetch the bids for the auction
#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')

#     # Render the auction detail page
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bids': bids,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)
# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse
# from django.core.mail import send_mail
# from django.conf import settings
# from django.utils import timezone
# from .models import Auction, Bid
# from .forms import BidForm

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
#         if form.is_valid():
#             bid_price = form.cleaned_data['bid_price']
#             starting_bid = auction.starting_bid  # Get the starting bid from the auction
            
#             if bid_price > starting_bid:
#                 try:
#                     # Create and save the new bid
#                     new_bid = form.save(commit=False)
#                     new_bid.bider = request.user  # Assign the bidder (current logged-in user)
#                     new_bid.bid_date = timezone.now()
#                     new_bid.auction = auction
#                     new_bid.save()

#                     # Update the current bid of the auction
#                     auction.current_bid = bid_price
#                     auction.save()

#                     # Send email notification to bidder
#                     bidder_email = request.user.email
#                     if bidder_email:
#                         subject = f'Your Bid Placed on "{auction.title}"'
#                         message = (
#                             f'Dear {request.user.username},\n\n'
#                             f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
#                             f'Bid Amount: ${bid_price:.2f}\n'
#                             f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
#                             f'Thank you for using our auction platform.\n'
#                         )

#                         send_mail(
#                             subject,
#                             message,
#                             settings.EMAIL_HOST_USER,
#                             [bidder_email],
#                             fail_silently=False,
#                         )

#                         # Debugging: confirmation message
#                         print(f'Email sent successfully to {bidder_email}')

#                     return JsonResponse({
#                         'success': True,
#                         'current_bid': f'${bid_price:.2f}',
#                         'message': 'Your bid has been placed successfully!',
#                         'bidder': request.user.username,
#                         'bid_price': f'${bid_price:.2f}',
#                         'bid_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'message': f'Error: {str(e)}'
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Your bid must be higher than the starting bid.'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid form.'
#             })

#     # Fetch the bids for the auction
#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')

#     # Render the auction detail page
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bids': bids,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)
# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse
# from django.core.mail import send_mail
# from django.conf import settings
# from django.utils import timezone
# from .models import Auction, Bid
# from .forms import BidForm

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
#         if form.is_valid():
#             bid_price = form.cleaned_data['bid_price']
#             starting_bid = auction.starting_bid  # Get the starting bid from the auction
            
#             if bid_price > starting_bid:
#                 try:
#                     # Create and save the new bid
#                     new_bid = form.save(commit=False)
#                     new_bid.bider = request.user  # Assign the bidder (current logged-in user)
#                     new_bid.bid_date = timezone.now()
#                     new_bid.auction = auction
#                     new_bid.save()

#                     # Update the current bid of the auction
#                     auction.current_bid = bid_price
#                     auction.save()

#                     # Send email notification to bidder
#                     bidder_email = request.user.email
#                     if bidder_email:
#                         subject = f'Your Bid Placed on "{auction.title}"'
#                         message = (
#                             f'Dear {request.user.username},\n\n'
#                             f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
#                             f'Bid Amount: ${bid_price:.2f}\n'
#                             f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
#                             f'Thank you for using our auction platform.\n'
#                         )

#                         send_mail(
#                             subject,
#                             message,
#                             settings.EMAIL_HOST_USER,
#                             [bidder_email],
#                             fail_silently=False,
#                         )

#                         # Debugging: confirmation message
#                         print(f'Email sent successfully to {bidder_email}')

#                     return JsonResponse({
#                         'success': True,
#                         'current_bid': f'${bid_price:.2f}',
#                         'message': 'Your bid has been placed successfully!',
#                         'bidder': request.user.username,
#                         'bid_price': f'${bid_price:.2f}',
#                         'bid_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'message': f'Error: {str(e)}'
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Your bid must be higher than the starting bid.'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid form.'
#             })

#     # Fetch the bids for the auction
#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')

#     # Render the auction detail page
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bids': bids,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Auction, Bid
from .forms import BidForm
from django.contrib.auth.decorators import login_required

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
#         if form.is_valid():
#             bid_price = form.cleaned_data['bid_price']
#             starting_bid = auction.starting_bid  # Get the starting bid from the auction
            
#             if bid_price > starting_bid:
#                 try:
#                     # Create and save the new bid
#                     new_bid = form.save(commit=False)
#                     new_bid.bider = request.user  # Assign the bidder (current logged-in user)
#                     new_bid.bid_date = timezone.now()  # Use current time when bid is placed
#                     new_bid.auction = auction
#                     new_bid.save()

#                     # Update the current bid of the auction
#                     auction.current_bid = bid_price
#                     auction.save()

#                     # Send email notification to bidder
#                     bidder_email = request.user.email
#                     if bidder_email:
#                         subject = f'Your Bid Placed on "{auction.title}"'
#                         message = (
#                             f'Dear {request.user.username},\n\n'
#                             f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
#                             f'Bid Amount: ${bid_price:.2f}\n'
#                             f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
#                             f'Thank you for using our auction platform.\n'
#                         )

#                         send_mail(
#                             subject,
#                             message,
#                             settings.EMAIL_HOST_USER,
#                             [bidder_email],
#                             fail_silently=False,
#                         )

#                         # Debugging: confirmation message
#                         print(f'Email sent successfully to {bidder_email}')

#                     return JsonResponse({
#                         'success': True,
#                         'current_bid': f'${bid_price:.2f}',
#                         'message': 'Your bid has been placed successfully!',
#                         'bidder': request.user.username,
#                         'bid_price': f'${bid_price:.2f}',
#                         'bid_date': new_bid.bid_date.strftime('%Y-%m-%d %H:%M:%S')
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'message': f'Error: {str(e)}'
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Your bid must be higher than the starting bid.'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid form.'
#             })

#     # Fetch the bids for the auction
#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')

#     # Render the auction detail page
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bids': bids,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Auction, Bid
from .forms import BidForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation

@login_required
def bitplacement(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = BidForm(request.POST)
        
        # Check if bid_price is a valid number
        try:
            bid_price = Decimal(request.POST.get('bid_price', '0'))
        except InvalidOperation:
            return JsonResponse({
                'success': False,
                'message': 'Invalid bid amount. Please enter a valid number.'
            })

        # Check if bid price is greater than starting bid
        if bid_price > Decimal(auction.starting_bid):
            try:
                # Create and save the new bid
                new_bid = Bid(
                    bider=request.user,
                    bid_date=timezone.now(),
                    auction=auction,
                    bid_price=bid_price
                )
                new_bid.save()

                # Update the current bid of the auction
                auction.current_bid = bid_price
                auction.save()

                # Send email notification to bidder
                bidder_email = request.user.email
                if bidder_email:
                    subject = f'Your Bid Placed on "{auction.title}"'
                    message = (
                        f'Dear {request.user.username},\n\n'
                        f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
                        f'Bid Amount: ${bid_price:.2f}\n'
                        f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
                        f'Thank you for using our auction platform.\n'
                    )

                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [bidder_email],
                        fail_silently=False,
                    )

                    # Debugging: confirmation message
                    print(f'Email sent successfully to {bidder_email}')

                return JsonResponse({
                    'success': True,
                    'current_bid': f'${bid_price:.2f}',
                    'message': 'Your bid has been placed successfully!',
                    'bidder': request.user.username,
                    'bid_price': f'${bid_price:.2f}',
                    'bid_date': new_bid.bid_date.strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Your bid must be higher than the starting bid.'
            })

    # Fetch the bids for the auction
    bids = Bid.objects.filter(auction=auction).order_by('-bid_date')

    # Render the auction detail page
    bid_form = BidForm()
    context = {
        'auction': auction,
        'bids': bids,
        'bid_form': bid_form,
    }
    return render(request, 'bitplacement.html', context)


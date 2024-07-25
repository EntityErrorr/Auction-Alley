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



from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Auction, Bid
from .forms import BidForm
from django.contrib.auth.decorators import login_required


# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
# from django.utils import timezone
# from django.core.mail import send_mail
# from django.conf import settings
# from .models import Auction, Bid
# from .forms import BidForm
# from django.contrib.auth.decorators import login_required
# from decimal import Decimal, InvalidOperation

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
        
#         # Check if bid_price is a valid number
#         try:
#             bid_price = Decimal(request.POST.get('bid_price', '0'))
#         except InvalidOperation:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid amount. Please enter a valid number.'
#             })

#         # Check if bid price is greater than starting bid
#         if bid_price > Decimal(auction.starting_bid):
#             try:
#                 # Create and save the new bid
#                 new_bid = Bid(
#                     bider=request.user,
#                     bid_date=timezone.now(),
#                     auction=auction,
#                     bid_price=bid_price
#                 )
#                 new_bid.save()

#                 # Update the current bid of the auction
#                 auction.current_bid = bid_price
#                 auction.save()

#                 # Send email notification to bidder
#                 bidder_email = request.user.email
#                 if bidder_email:
#                     subject = f'Your Bid Placed on "{auction.title}"'
#                     message = (
#                         f'Dear {request.user.username},\n\n'
#                         f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
#                         f'Bid Amount: ${bid_price:.2f}\n'
#                         f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
#                         f'Thank you for using our auction platform.\n'
#                     )

#                     send_mail(
#                         subject,
#                         message,
#                         settings.EMAIL_HOST_USER,
#                         [bidder_email],
#                         fail_silently=False,
#                     )

#                     # Debugging: confirmation message
#                     print(f'Email sent successfully to {bidder_email}')

#                 return JsonResponse({
#                     'success': True,
#                     'current_bid': f'${bid_price:.2f}',
#                     'message': 'Your bid has been placed successfully!',
#                     'bidder': request.user.username,
#                     'bid_price': f'${bid_price:.2f}',
#                     'bid_date': new_bid.bid_date.strftime('%Y-%m-%d %H:%M:%S')
#                 })
#             except Exception as e:
#                 return JsonResponse({
#                     'success': False,
#                     'message': f'Error: {str(e)}'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Your bid must be higher than the starting bid.'
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



#new_place 

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Auction, Bid
from .forms import BidForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
        
#         try:
#             bid_price = Decimal(request.POST.get('bid_price', '0'))
#         except InvalidOperation:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid amount. Please enter a valid number.'
#             })

#         if bid_price > Decimal(auction.starting_bid):
#             try:
#                 new_bid = Bid(
#                     bider=request.user,
#                     bid_date=timezone.now(),
#                     auction=auction,
#                     bid_price=bid_price
#                 )
#                 new_bid.save()

#                 auction.current_bid = bid_price
#                 auction.save()

#                 bidder_email = request.user.email
#                 if bidder_email:
#                     subject = f'Your Bid Placed on "{auction.title}"'
#                     message = (
#                         f'Dear {request.user.username},\n\n'
#                         f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
#                         f'Bid Amount: ${bid_price:.2f}\n'
#                         f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
#                         f'Thank you for using our auction platform.\n'
#                     )

#                     send_mail(
#                         subject,
#                         message,
#                         settings.EMAIL_HOST_USER,
#                         [bidder_email],
#                         fail_silently=False,
#                     )

#                     print(f'Email sent successfully to {bidder_email}')

#                 return JsonResponse({
#                     'success': True,
#                     'current_bid': f'${bid_price:.2f}',
#                     'message': 'Your bid has been placed successfully!',
#                     'bidder': request.user.username,
#                     'bid_price': f'${bid_price:.2f}',
#                     'bid_date': new_bid.bid_date.strftime('%Y-%m-%d %H:%M:%S')
#                 })
#             except Exception as e:
#                 return JsonResponse({
#                     'success': False,
#                     'message': f'Error: {str(e)}'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Your bid must be higher than the starting bid.'
#             })

#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bids': bids,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)



#new_place2


# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
        
#         try:
#             bid_price = Decimal(request.POST.get('bid_price', '0'))
#         except InvalidOperation:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid amount. Please enter a valid number.'
#             })

#         if bid_price > Decimal(auction.starting_bid):
#             try:
#                 # Save the new bid
#                 new_bid = Bid(
#                     bider=request.user,
#                     bid_date=timezone.now(),
#                     auction=auction,
#                     bid_price=bid_price
#                 )
#                 new_bid.save()

#                 # Update the auction with the new bid
#                 auction.current_bid = bid_price
#                 auction.save()

#                 # Send confirmation email to the current bidder
#                 bidder_email = request.user.email
#                 if bidder_email:
#                     subject = f'Your Bid Placed on "{auction.title}"'
#                     message = (
#                         f'Dear {request.user.username},\n\n'
#                         f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
#                         f'Bid Amount: ${bid_price:.2f}\n'
#                         f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
#                         f'Thank you for using our auction platform.\n'
#                     )

#                     send_mail(
#                         subject,
#                         message,
#                         settings.EMAIL_HOST_USER,
#                         [bidder_email],
#                         fail_silently=False,
#                     )

#                     print(f'Email sent successfully to {bidder_email}')

#                 # Notify all previous bidders
#                 previous_bidders = Bid.objects.filter(auction=auction).exclude(bider=request.user).values_list('bider__email', flat=True).distinct()
                
#                 for email in previous_bidders:
#                     if email:
#                         notification_subject = f'A new higher bid has been placed on "{auction.title}"'
#                         notification_message = (
#                             f'Dear Bidder,\n\n'
#                             f'A new higher bid has been placed on the auction."{auction.title}".\n\n'
#                             f'New Bid Amount: ${bid_price:.2f}\n\n'
#                             f'Thank you for using our auction platform.\n'
#                         )

#                         send_mail(
#                             notification_subject,
#                             notification_message,
#                             settings.EMAIL_HOST_USER,
#                             [email],
#                             fail_silently=False,
#                         )

#                         print(f'Notification email sent to {email}')

#                 return JsonResponse({
#                     'success': True,
#                     'current_bid': f'${bid_price:.2f}',
#                     'message': 'Your bid has been placed successfully!',
#                     'bidder': request.user.username,
#                     'bid_price': f'${bid_price:.2f}',
#                     'bid_date': new_bid.bid_date.strftime('%Y-%m-%d %H:%M:%S')
#                 })
#             except Exception as e:
#                 return JsonResponse({
#                     'success': False,
#                     'message': f'Error: {str(e)}'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Your bid must be higher than the starting bid.'
#             })

#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')
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
        
#         try:
#             bid_price = Decimal(request.POST.get('bid_price', '0'))
#         except InvalidOperation:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid amount. Please enter a valid number.'
#             })

#         if bid_price > Decimal(auction.starting_bid):
#             try:
#                 new_bid = Bid(
#                     bider=request.user,
#                     bid_date=timezone.now(),
#                     auction=auction,
#                     bid_price=bid_price
#                 )
#                 new_bid.save()

#                 auction.current_bid = bid_price
#                 auction.save()

#                 bidder_email = request.user.email
#                 if bidder_email:
#                     subject = f'Your Bid Placed on "{auction.title}"'
#                     message = (
#                         f'Dear {request.user.username},\n\n'
#                         f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
#                         f'Bid Amount: ${bid_price:.2f}\n'
#                         f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
#                         f'Thank you for using our auction platform.\n'
#                     )

#                     send_mail(
#                         subject,
#                         message,
#                         settings.EMAIL_HOST_USER,
#                         [bidder_email],
#                         fail_silently=False,
#                     )

#                     print(f'Email sent successfully to {bidder_email}')

#                 # Notify previous bidders
#                 # Get all previous bids for the auction
#                 all_bids = Bid.objects.filter(auction=auction).exclude(bider=request.user).order_by('-bid_date')
#                 seen_bidders = set()
#                 for bid in all_bids:
#                     if bid.bider not in seen_bidders:
#                         seen_bidders.add(bid.bider)
#                         previous_bidder_email = bid.bider.email
#                         if previous_bidder_email:
#                             notification_subject = f'Your bid has been outbid on "{auction.title}"'
#                             notification_message = (
#                                 f'Dear {bid.bider.username},\n\n'
#                                 f'Your bid on "{auction.title}" has been outbid.\n\n'
#                                 f'Your bid was: ${bid.bid_price:.2f}\n'
#                                 f'The new bid is: ${bid_price:.2f}\n\n'
#                                 f'If you want to outbid it, please place a new bid.\n\n'
#                                 f'Thank you for using our auction platform.\n'
#                             )

#                             send_mail(
#                                 notification_subject,
#                                 notification_message,
#                                 settings.EMAIL_HOST_USER,
#                                 [previous_bidder_email],
#                                 fail_silently=False,
#                             )

#                             print(f'Notification email sent to previous bidder {previous_bidder_email}')

#                 return JsonResponse({
#                     'success': True,
#                     'current_bid': f'${bid_price:.2f}',
#                     'message': 'Your bid has been placed successfully!',
#                     'bidder': request.user.username,
#                     'bid_price': f'${bid_price:.2f}',
#                     'bid_date': new_bid.bid_date.strftime('%Y-%m-%d %H:%M:%S')
#                 })
#             except Exception as e:
#                 return JsonResponse({
#                     'success': False,
#                     'message': f'Error: {str(e)}'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Your bid must be higher than the starting bid.'
#             })

#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bids': bids,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)


# from django.utils import timezone
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404, render
# from .models import Auction, Bid
# from .forms import BidForm
# from django.core.mail import send_mail
# from decimal import Decimal, InvalidOperation

# @login_required
# def bitplacement(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
    
#     if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         form = BidForm(request.POST)
        
#         try:
#             bid_price = Decimal(request.POST.get('bid_price', '0'))
#         except InvalidOperation:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Invalid bid amount. Please enter a valid number.'
#             })

#         if bid_price > Decimal(auction.starting_bid):
#             try:
#                 new_bid = Bid(
#                     bider=request.user,
#                     bid_date=timezone.now(),
#                     auction=auction,
#                     bid_price=bid_price
#                 )
#                 new_bid.save()

#                 auction.current_bid = bid_price
#                 auction.save()

#                 bidder_email = request.user.email
#                 if bidder_email:
#                     subject = f'Your Bid Placed on "{auction.title}"'
#                     message = (
#                         f'Dear {request.user.username},\n\n'
#                         f'You have successfully placed a bid on the auction "{auction.title}".\n\n'
#                         f'Bid Amount: ${bid_price:.2f}\n'
#                         f'Bid Date: {new_bid.bid_date.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
#                         f'Thank you for using our auction platform.\n'
#                     )

#                     send_mail(
#                         subject,
#                         message,
#                         settings.EMAIL_HOST_USER,
#                         [bidder_email],
#                         fail_silently=False,
#                     )

#                     print(f'Email sent successfully to {bidder_email}')

#                 # Notify previous bidders
#                 all_bids = Bid.objects.filter(auction=auction).exclude(bider=request.user).order_by('-bid_date')
#                 seen_bidders = set()
#                 for bid in all_bids:
#                     if bid.bider not in seen_bidders:
#                         seen_bidders.add(bid.bider)
#                         previous_bidder_email = bid.bider.email
#                         if previous_bidder_email:
#                             notification_subject = f'Your bid has been outbid on "{auction.title}"'
#                             notification_message = (
#                                 f'Dear {bid.bider.username},\n\n'
#                                 f'Your bid on "{auction.title}" has been outbid.\n\n'
#                                 f'Your bid was: ${bid.bid_price:.2f}\n'
#                                 f'The new bid is: ${bid_price:.2f}\n\n'
#                                 f'If you want to outbid it, please place a new bid.\n\n'
#                                 f'Thank you for using our auction platform.\n'
#                             )

#                             send_mail(
#                                 notification_subject,
#                                 notification_message,
#                                 settings.EMAIL_HOST_USER,
#                                 [previous_bidder_email],
#                                 fail_silently=False,
#                             )

#                             print(f'Notification email sent to previous bidder {previous_bidder_email}')

#                 return JsonResponse({
#                     'success': True,
#                     'current_bid': f'${bid_price:.2f}',
#                     'message': 'Your bid has been placed successfully!',
#                     'bidder': request.user.username,
#                     'bid_price': f'${bid_price:.2f}',
#                     'bid_date': timezone.localtime(new_bid.bid_date).strftime('%Y-%m-%d %H:%M:%S')  # Local time
#                 })
#             except Exception as e:
#                 return JsonResponse({
#                     'success': False,
#                     'message': f'Error: {str(e)}'
#                 })
#         else:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Your bid must be higher than the starting bid.'
#             })

#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')
#     bid_form = BidForm()
#     context = {
#         'auction': auction,
#         'bids': bids,
#         'bid_form': bid_form,
#     }
#     return render(request, 'bitplacement.html', context)

# from django.core.paginator import Paginator
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Auction, Bid

# def load_bids(request, auction_id):
#     auction = get_object_or_404(Auction, id=auction_id)
#     bids = Bid.objects.filter(auction=auction).order_by('-bid_date')
    
#     # Pagination
#     paginator = Paginator(bids, 5)  # Show 5 bids per page
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)
    
#     # Prepare data for response
#     bid_list = list(page_obj.object_list.values('bider__username', 'bid_price', 'bid_date'))
    
#     response_data = {
#         'bids': bid_list,
#         'has_next': page_obj.has_next()
#     }
    
#     return JsonResponse(response_data)


#updated 7/26/2024

from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Auction, Bid
from .forms import BidForm

@login_required
def bitplacement(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form = BidForm(request.POST)
        
        try:
            bid_price = Decimal(request.POST.get('bid_price', '0'))
        except InvalidOperation:
            return JsonResponse({
                'success': False,
                'message': 'Invalid bid amount. Please enter a valid number.'
            })

        if bid_price > Decimal(auction.starting_bid):
            try:
                new_bid = Bid(
                    bider=request.user,
                    bid_date=timezone.now(),
                    auction=auction,
                    bid_price=bid_price
                )
                new_bid.save()

                auction.current_bid = bid_price
                auction.save()

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

                # Notify previous bidders
                all_bids = Bid.objects.filter(auction=auction).exclude(bider=request.user).order_by('-bid_date')
                seen_bidders = set()
                for bid in all_bids:
                    if bid.bider not in seen_bidders:
                        seen_bidders.add(bid.bider)
                        previous_bidder_email = bid.bider.email
                        if previous_bidder_email:
                            notification_subject = f'Your bid has been outbid on "{auction.title}"'
                            notification_message = (
                                f'Dear {bid.bider.username},\n\n'
                                f'Your bid on "{auction.title}" has been outbid.\n\n'
                                f'Your bid was: ${bid.bid_price:.2f}\n'
                                f'The new bid is: ${bid_price:.2f}\n\n'
                                f'If you want to outbid it, please place a new bid.\n\n'
                                f'Thank you for using our auction platform.\n'
                            )

                            send_mail(
                                notification_subject,
                                notification_message,
                                settings.EMAIL_HOST_USER,
                                [previous_bidder_email],
                                fail_silently=False,
                            )

                return JsonResponse({
                    'success': True,
                    'current_bid': f'${bid_price:.2f}',
                    'message': 'Your bid has been placed successfully!',
                    'bidder': request.user.username,
                    'bid_price': f'${bid_price:.2f}',
                    'bid_date': timezone.localtime(new_bid.bid_date).strftime('%Y-%m-%d %H:%M:%S')  # Local time
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

    # Display only the latest 5 bids initially
    bids = Bid.objects.filter(auction=auction).order_by('-bid_date')[:5]
    bid_form = BidForm()
    context = {
        'auction': auction,
        'bids': bids,
        'bid_form': bid_form,
        'has_next': Bid.objects.filter(auction=auction).count() > 5  # Check if there are more bids
    }
    return render(request, 'bitplacement.html', context)


from django.http import JsonResponse
from django.core.serializers import serialize

def load_bids(request, auction_id):
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 5))
    bids = Bid.objects.filter(auction_id=auction_id).select_related('bider').order_by('-bid_date')[offset:offset + limit]

    bid_data = []
    for bid in bids:
        bid_data.append({
            'bider': bid.bider.username,
            'bid_price': bid.bid_price,
            'bid_date': bid.bid_date.strftime('%Y-%m-%d %H:%M:%S')  # Format date as needed
        })

    has_next = Bid.objects.filter(auction_id=auction_id).count() > offset + limit

    return JsonResponse({
        'bids': bid_data,
        'has_next': has_next
    })

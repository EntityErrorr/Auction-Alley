from django.shortcuts import get_object_or_404, render, redirect
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.utils import timezone

from .models import User, Auction, Bid, Category, Comment, Watchlist,Advisorslot
from .forms import NewCommentForm,BidForm,CreateSlotForm,UpdateSlotForm,AuctionItemForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

# views.py
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from .models import Auction, Bid, Comment, Watchlist,RefundRequest
from .forms import NewCommentForm,RefundRequestForm

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
    ).exclude(creation_date__gt=timezone.now()).order_by('-creation_date')
    return render(request, "searchresults.html", {"auctions": live_auctions, 'name':'Live Auction'})

def UpcomingAuction(request):
    live_auctions = Auction.objects.filter(
        approval_status='approved',
        creation_date__gt=timezone.now()
    ).order_by('-creation_date')
    return render(request, "searchresults.html", {"auctions": live_auctions, 'name':'Upcoming Auction'})

def past_auctions(request):
    past_auctions = Auction.objects.filter(approval_status='approved',end_time__lt=timezone.now()).order_by('-creation_date')
    
    for auction in past_auctions:
        if not auction.winner:
            highest_bid = Bid.objects.filter(auction=auction).order_by('-bid_price').first()
            if highest_bid:
                auction.winner = highest_bid.bider
                auction.current_bid = highest_bid.bid_price
                auction.save()
                # Send an automated winner notification
                send_mail(
                    'Congratulations! You Won the Auction',
                    f'Dear {auction.winner.username},\n\nYou have won the auction for {auction.title} with a bid of ${auction.current_bid}.\n\nThank you for participating!',
                    'no-reply@auctionwebsite.com',
                    [auction.winner.email],
                    fail_silently=False,
                )
    return render(request, 'searchresults.html', {"auctions": past_auctions, 'name':'Past Auction'})

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

                    print(f'Email sent successfully to {bidder_email}')

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

                            print(f'Notification email sent to previous bidder {previous_bidder_email}')

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


from django.shortcuts import render
from .models import Auction

def search_auctions(request):
    query = request.GET.get('search', '')
    auctions = Auction.objects.all()
    
    if query:
        auctions = auctions.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query) |
            Q(starting_bid__icontains=query)
        )

    context = {
        'auctions': auctions
    }
    return render(request, 'dashboard/home.html', context)

def adminapprove(request):
    pending_auction= Auction.objects.filter(approval_status='pending')
    if request.method=='POST':
        action_value = request.POST.get('action')
        action,data=action_value.split('|')
        preauction= Auction.objects.get(pk=data)
        preauction.approval_status=action
        seller=preauction.seller
        if action == 'approved':
            seller.total_properties+=1
            seller.save()
        preauction.save()
    return render(request,'adminapprove.html',{'pending':pending_auction})

def ProtectRole(request,role):
    if not request.user.is_authenticated:
        return False
    elif role=='admin':
        if not request.user.is_superuser:
            return False
    elif role=='advisor':
        if not request.user.is_staff:
            return False
    return True

def Manageslot(request):
    role= ProtectRole(request, 'advisor')
    if not role:
        return redirect('/')
    slots=Advisorslot.objects.filter(user=request.user)
    return render(request, 'manageslot.html',{'slots':slots})

def Createslot(request):
    role = ProtectRole(request, 'advisor')
    if not role:
        return redirect('/')
    
    if request.method == 'POST':
        form = CreateSlotForm(request.POST)
        if form.is_valid():
            newslot = form.save(commit=False)
            newslot.user = request.user
            newslot.meet_link = "Will be provided when the slot is started"
            newslot.save()
            return redirect('/Manage_Slots')
        # Handle the invalid form case
        return render(request, 'createslot.html', {'form': form})

    else:
        form = CreateSlotForm()
        return render(request, 'createslot.html', {'form': form})

def UpdateSlot(request, id):
    role = ProtectRole(request,'advisor')
    if not role:
        return redirect('/')
    slot = Advisorslot.objects.get(id=int(id))

    if request.method == 'POST':
        form = UpdateSlotForm(request.POST,instance=slot)
        if form.is_valid():
            form.save()
            return redirect('/Manage_Slots')
        # Handle the invalid form case
        return render(request, 'updateslot.html', {'slot':slot,'form': form})

    else:
        form = UpdateSlotForm(instance=slot)
        return render(request,'updateslot.html',{'slot':slot,'form':form})

def DeleteSlot(request, id):
    role = ProtectRole(request,'advisor')
    if not role:
        return redirect('/')

    slot = Advisorslot.objects.get(id=int(id))

    slot.delete()

    return redirect('/Manage_Slots')

def Advisor_Page(request):
    advisors = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    return render(request,'advisorpage.html',{'advisors':advisors})

def Advisor_Inside(request,id):
    advisor = get_object_or_404(User, id=int(id))

    slots = Advisorslot.objects.filter(user=advisor)

    return render(request,'advisorinside.html',{'advisor':advisor,'slots':slots})

@login_required
def BookSlot(request, id):
    if request.user.is_authenticated:
        slot = Advisorslot.objects.get(id=int(id))
        if slot.total_user+1 > slot.max_user:
            return JsonResponse({"Error":"Max capacity reached"})
        else:
            if request.user in slot.booked_user_list.all():
                slot.total_user -= 1
                slot.booked_user_list.remove(request.user)
            else:
                slot.total_user += 1
                slot.booked_user_list.add(request.user)

            slot.save()
            return redirect(f'/advisors/{slot.user.id}')

def advanced_search_properties(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        property_type_id = request.POST.get('property_type')
        price_range = request.POST.get('price_range')
        min_size = request.POST.get('min_size')

        items = Auction.objects.all().exclude(approval_status__in=[ 'pending','rejected'])
        if location:
            items = items.filter(address__icontains=location)
        if property_type_id:
            # items = items.filter(category=property_type)
            items = items.filter(category_id=property_type_id)
        if price_range:
            items = items.filter(starting_bid__lte=price_range)
        if min_size:
            items = items.filter(house_size__gte=min_size)

        return render(request, 'searchresults.html', {'auctions': items})

    return render(request, 'home.html')

def refund_request(request):
    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            form.user=request.user
            form.save()  
            return redirect('User:home')
    else:
        form = RefundRequestForm()
    return render(request, 'refund.html', {'form': form})

@login_required 
def create_auction(request):
    if request.method == 'POST':
        form = AuctionItemForm(request.POST, request.FILES)
        if form.is_valid():
            print(request.FILES)
            auction_item = form.save(commit=False)
            seller=request.user.profile.seller
            auction_item.seller = seller 
            auction_item.approval_status = 'pending'
            auction_item.save()
            return redirect('User:home')
    else:
        form = AuctionItemForm()

    return render(request, 'createauction.html', {'form': form})


def end_auction(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    auction.status = 'past'
    auction.save()
    
    winner = auction.current_bid_by
    if winner:
        send_winner_notification(winner, auction)
    
    return JsonResponse({'success': True})
def send_winner_notification(winner, auction):
    subject = 'Congratulations! You won the auction'
    message = f'Dear {winner.username},\n\nCongratulations! You won the auction for {auction.title} with a bid of ${auction.current_bid}.\n\nThank you for participating!'
    from_email = 'no-reply@yourauction.com'
    recipient_list = [winner.email]
    send_mail(subject, message, from_email, recipient_list)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Auction

@login_required
def winner_bid_profile(request):
    user = request.user
    past_auctions = Auction.objects.filter(winner=user)
    is_winner = past_auctions.exists()  # Check if the user is a winner of any auction

    context = {
        'past_auctions': past_auctions,
        'is_winner': is_winner,
        'current_user': user,
    }
    return render(request, 'winner_bid_profile.html', context)



from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from Dashboard.models import Auction
from User.models import Profile

@login_required
def purchase_process(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    user_profile = get_object_or_404(Profile, user=request.user)
    purchase_success = False
    deposit_required = auction.current_bid

    if request.method == 'POST':
        if user_profile.amount >= deposit_required:
            # Deduct the purchase amount from the user's balance
            user_profile.amount -= deposit_required
            user_profile.save()

            subject_user = 'Purchase Confirmation'
            message_user = f'''
            Dear {request.user.username},

            Congratulations!

            You have successfully purchased the property "{auction.title}".

            The winning amount is ${auction.current_bid}.

            Thank you for using our auction service.

            Best regards,
            Auction Alley Team
            '''
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list_user = [request.user.email]

            send_mail(subject_user, message_user, from_email, recipient_list_user)
            print(f'Email sent successfully to the user {request.user.email}')

            # Notify the seller
            if auction.seller and auction.seller.profile and auction.seller.profile.user:
                confirm_url = request.build_absolute_uri(reverse('dashboard:confirm_papers', args=[auction.id]))
                subject_seller = 'Your Property Has Been Purchased'
                message_seller = f'''
                Dear {auction.seller.profile.user.username},

                Congratulations!

                Your property "{auction.title}" has been purchased successfully.

                The winning amount is ${auction.current_bid}.

                Please prepare the necessary paperwork for the transaction.

                To confirm the preparation of the papers, please click the link below:
                {confirm_url}

                Thank you for using our auction service.

                Best regards,
                Auction Alley Team
                '''
                recipient_list_seller = [auction.seller.profile.user.email]

                send_mail(subject_seller, message_seller, from_email, recipient_list_seller)
                print(f'Email sent successfully to the seller {auction.seller.profile.user.email}')

            purchase_success = True

            return redirect('dashboard:purchase_success')
        else:
            return render(request, 'purchase_process.html', {
                'auction': auction,
                'purchase_success': purchase_success,
                'error': 'Insufficient funds. Please deposit the required amount first.'
            })

    return render(request, 'purchase_process.html', {
        'auction': auction,
        'purchase_success': purchase_success,
        'error': None
    })



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Auction

@login_required
def confirm_papers(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    
    
    auction.papers_confirmed = True
    auction.save()

    return render(request, 'confirm_papers.html')




@login_required
def purchase_success(request):
    return render(request, 'purchase_success.html')



@login_required
def request_papers(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    
    return render(request, 'request_papers.html')

# dashboard/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Watchlist, Auction

# dashboard/views.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Auction, Watchlist

@login_required
def add_to_watchlist(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    if auction not in watchlist.auctions.all():
        watchlist.auctions.add(auction)
    return redirect('dashboard:AuctionItem', auction_id=auction.id)

@login_required
def remove_from_watchlist(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    watchlist = Watchlist.objects.get(user=request.user)
    if auction in watchlist.auctions.all():
        watchlist.auctions.remove(auction)
    return redirect('dashboard:AuctionItem', auction_id=auction.id)


@login_required
def view_watchlist(request):
    # Ensure the Watchlist instance exists
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    return render(request, 'watchlist.html', {'watchlist': watchlist})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Auction
from .forms import HousePaperForm

@login_required
def upload_house_paper(request):
    # Fetch the first auction related to the current user
    auctions = Auction.objects.filter(seller__profile__user=request.user)  # Fetch auctions where the user is the seller

    if not auctions:
        messages.error(request, 'No auctions found for the current seller.')
        return render(request, 'upload_house_paper.html')

    auction = auctions.first()  

    if request.method == 'POST':
        form = HousePaperForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle file upload and other form processing here
            form.instance.auction = auction  # Associate the uploaded paper with the auction
            form.save()
            messages.success(request, 'House paper uploaded successfully.')
            return render(request, 'upload_house_paper.html', {
                'auction': auction,
                'seller_name': request.user.username,
                'seller_email': request.user.email,
                'seller_phone': request.user.profile.phone_number,
                'form': form,
            })
    else:
        form = HousePaperForm()

    context = {
        'auction': auction,
        'seller_name': request.user.username,
        'seller_email': request.user.email,
        'form': form,
    }
    return render(request, 'upload_house_paper.html', context)




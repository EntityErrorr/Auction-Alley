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
# views.py

from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from .models import Auction, Bid, Comment, Watchlist
from .forms import NewCommentForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

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
        return render(request, "AuctionItem.html", {'form': form})

def LiveAuction(request):
    live_auctions = Auction.objects.filter(
        approval_status='approved',
        end_time__gt=timezone.now()
    ).exclude(creation_date__gt=timezone.now()).order_by('-creation_date')
    return render(request, "searchresults.html", {"auctions": live_auctions, 'name': 'Live Auction'})

def UpcomingAuction(request):
    upcoming_auctions = Auction.objects.filter(
        approval_status='approved',
        creation_date__gt=timezone.now()
    ).order_by('-creation_date')
    return render(request, "searchresults.html", {"auctions": upcoming_auctions, 'name': 'Upcoming Auction'})


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

# from .forms import RefundRequestForm

# def refund_request(request):
#     if request.method == 'POST':
#         form = RefundRequestForm(request.POST)
#         if form.is_valid():
#             form.user=request.user
#             form.save()  
#             return redirect('User:home')
#     else:
#         form = RefundRequestForm()
#     return render(request, 'refund.html', {'form': form})

from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Auction
from .forms import RefundRequestForm

def refund_request(request):
    # Retrieve the first auction where the current user is the winner
    auction = Auction.objects.filter(winner=request.user).first()

    if not auction:
        # If no auction is found, redirect to the profile page
        return redirect('dashboard:winner_bid_profile')

    if not auction.purchase_success:
        # Ensure the purchase was successful before allowing a refund request
        return redirect('dashboard:winner_bid_profile')

    # Check if the user has clicked the "Request for Refund" button
    ref = request.GET.get('ref')
    if ref == 'approve':
        if not auction.refund_requested:
            # Mark the auction as having a refund requested
            auction.refund_requested = True
            auction.save()

            # Set a success message
            messages.success(request, "Refund request has been successfully submitted.")

        else:
            # If refund has already been requested, set an info message
            messages.info(request, "You have already requested a refund for this auction.")

        # Redirect back to the profile page
        return redirect('dashboard:winner_bid_profile')

    # If the query parameter is incorrect, show the refund_request_required page
    return render(request, 'refund.html', {'auction': auction})



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

            # Set purchase_success to True
            auction.purchase_success = True
            auction.save()

            return redirect('dashboard:purchase_success')
        else:
            return render(request, 'purchase_process.html', {
                'auction': auction,
                'purchase_success': False,
                'error': 'Insufficient funds. Please deposit the required amount first.'
            })

    return render(request, 'purchase_process.html', {
        'auction': auction,
        'purchase_success': False,
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


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import Auction, HousePaper
from .forms import HousePaperForm

@login_required
def upload_house_paper(request):
    auctions = Auction.objects.filter(seller__profile__user=request.user)

    if not auctions:
        messages.error(request, 'No auctions found for the current seller.')
        return render(request, 'upload_house_paper.html')

    auction = auctions.first()
    house_paper_uploaded = HousePaper.objects.filter(auction=auction).exists()

    if request.method == 'POST':
        form = HousePaperForm(request.POST, request.FILES)
        if form.is_valid():
            house_paper = form.save(commit=False)
            house_paper.auction = auction
            house_paper.seller = request.user
            house_paper.save()
            messages.success(request, 'House paper uploaded successfully.')
            return redirect('dashboard:upload_house_paper')
    else:
        form = HousePaperForm()

    context = {
        'auction': auction,
        'seller_name': request.user.username,
        'seller_email': request.user.email,
        'house_paper_uploaded': house_paper_uploaded,
        'winner_name': auction.current_bid_by.username if auction.current_bid_by else None,
        'form': form,
    }
    return render(request, 'upload_house_paper.html', context)

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Auction, HousePaper

@login_required
def send_house_paper_to_buyer(request):
    # Fetch the auction based on the current seller
    auctions = Auction.objects.filter(seller__profile__user=request.user)
    if not auctions.exists():
        messages.error(request, 'No auctions found for the current seller.')
        return redirect('dashboard:upload_house_paper')

    # Adjust as needed to select the appropriate auction
    auction = auctions.first()
    house_paper = HousePaper.objects.filter(auction=auction).first()

    if house_paper:
        # Check if the auction has a valid winner
        if auction.winner:
            buyer_email = auction.winner.email
            house_paper_url = request.build_absolute_uri(house_paper.paper.url)

            # Send email to the winner
            try:
                send_mail(
                    'House Paper Uploaded',
                    f'Dear {auction.winner.username},\n\n'
                    f'Congratulations!\n\n'
                    f'You have successfully purchased the property "{auction.title}".\n'
                    f'The winning amount is ${auction.current_bid}.\n\n'
                    f'The house paper for the auction you won has been uploaded. '
                    f'You can download it using the following link:\n{house_paper_url}\n\n'
                    f'Thank you for using our auction service.\n\n'
                    f'Best regards,\n'
                    f'Auction Alley Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [buyer_email],
                    fail_silently=False,
                )
                print(f'Email sent successfully to the user {auction.winner.email}')
                messages.success(request, 'House paper sent to buyer successfully.')
                
            except Exception as e:
                messages.error(request, f'Failed to send email: {e}')
        else:
            messages.error(request, 'No valid winner found for this auction.')
    else:
        messages.error(request, 'No house paper found to send.')

    return redirect('dashboard:upload_house_paper')







@login_required
def request_papers(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)
    house_paper = HousePaper.objects.filter(auction=auction).first()

    if house_paper:
        house_paper_url = house_paper.paper.url
    else:
        house_paper_url = None

    return render(request, 'request_papers.html', {'house_paper_url': house_paper_url})



from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Auction, Bid

@login_required
def generate_bill_pdf(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    # Ensure auction is approved and has ended
    if auction.approval_status != 'approved' or auction.end_time >= timezone.now():
        messages.error(request, 'Auction is not eligible for bill generation.')
        return redirect('dashboard:LiveAuction')

    # Check or set the winner
    if not auction.winner:
        highest_bid = Bid.objects.filter(auction=auction).order_by('-bid_price').first()
        if highest_bid:
            auction.winner = highest_bid.bider
            auction.current_bid = highest_bid.bid_price
            auction.save()
            send_mail(
                'Congratulations! You Won the Auction',
                f'Dear {auction.winner.username},\n\nYou have won the auction for {auction.title} with a bid of ${auction.current_bid}.\n\nThank you for participating!',
                'no-reply@auctionwebsite.com',
                [auction.winner.email],
                fail_silently=False,
            )

    if auction.winner:
        # Render the HTML template with context
        context = {
            'winner_name': auction.winner.username,
            'winner_email': auction.winner.email,
            'auction': auction
        }
        html_content = render_to_string('bill_template.html', context)

        # Generate PDF from HTML content
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="bill_{auction_id}.pdf"'

        # Create PDF
        pisa_status = pisa.CreatePDF(html_content, dest=response)

        if pisa_status.err:
            messages.error(request, 'Error generating PDF.')
            return redirect('dashboard:LiveAuction')

        return response
    else:
        messages.error(request, 'No winner found for this auction.')
        return redirect('dashboard:LiveAuction')










from django.shortcuts import get_object_or_404, render, redirect
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.utils import timezone

from .models import User, Auction, Bid, Category, Comment, Watchlist,Advisorslot
from .forms import NewCommentForm,BidForm,CreateSlotForm,UpdateSlotForm
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
    return render(request, "home.html", {"auctions": live_auctions})

@login_required
def bitplacement(request, auction_id):
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
    return render(request, 'bitplacement.html', context)



def adminapprove(request):
    pending_auction= Auction.objects.filter(approval_status='pending')
    if request.method=='POST':
        action_value = request.POST.get('action')
        action,data=action_value.split('|')
        preauction= Auction.objects.get(pk=data)
        preauction.approval_status=action
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


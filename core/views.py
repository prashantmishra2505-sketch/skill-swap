from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import *
from django.contrib.auth import logout
from django.http import JsonResponse
from .models import Skill
from .forms import UserSkillForm, ProfileForm, UserForm

# 1. Sign Up
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user) # Create empty profile
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# 2. Home / Explore
@login_required
def home(request):
    query = request.GET.get('q')
    
    # FILTER: Get skills that are 'TEACH' AND belong to OTHER users (not me)
    skills = UserSkill.objects.filter(role='TEACH').exclude(user=request.user)
    
    if query:
        skills = skills.filter(skill__name__icontains=query)
        
    return render(request, 'core/home.html', {'skills': skills})

# 3. Send Swap Request
@login_required
def send_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    SwapRequest.objects.create(sender=request.user, receiver=receiver)
    return redirect('dashboard')

# 4. Dashboard (Requests & Chats)
@login_required
def dashboard(request):
    incoming = SwapRequest.objects.filter(receiver=request.user, status='PENDING')
    my_skills = UserSkill.objects.filter(user=request.user)

    accepted_swaps = SwapRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user), 
        status='ACCEPTED'
    )
    
    unique_partners = set()
    for swap in accepted_swaps:
        if swap.sender == request.user:
            unique_partners.add(swap.receiver)
        else:
            unique_partners.add(swap.sender)

    # --- NEW NOTIFICATION LOGIC ---
    # We need to attach an unread_count to each partner object
    for partner in unique_partners:
        partner.unread_count = Message.objects.filter(
            sender=partner, 
            receiver=request.user, 
            is_read=False
        ).count()

    # Calculate total unread count for the JavaScript checker
    total_unread = Message.objects.filter(receiver=request.user, is_read=False).count()

    return render(request, 'core/dashboard.html', {
        'incoming': incoming, 
        'my_skills': my_skills,
        'chats': unique_partners,
        'unread_messages_count': total_unread  # Match your JS variable name!
    })

# 5. Handle Request (Accept/Decline)
@login_required
def handle_request(request, request_id, action):
    req = get_object_or_404(SwapRequest, id=request_id, receiver=request.user)
    if action == 'accept':
        req.status = 'ACCEPTED'
    else:
        req.status = 'DECLINED'
    req.save()
    return redirect('dashboard')

# 6. Chat Room
@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # --- NEW: Mark messages as READ when you open the chat ---
    Message.objects.filter(
        sender=other_user, 
        receiver=request.user, 
        is_read=False
    ).update(is_read=True)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | 
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content: # Prevent empty messages
            Message.objects.create(sender=request.user, receiver=other_user, content=content)
        return redirect('chat', user_id=user_id)
        
    return render(request, 'core/chat.html', {'other_user': other_user, 'messages': messages})

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirects to login page after logging out


def skill_autocomplete(request):
    query = request.GET.get('term', '')
    results = []
    if query:
        # Search for skills containing the text, grab top 10 unique names
        skills = Skill.objects.filter(name__icontains=query).values_list('name', flat=True).distinct()[:10]
        results = list(skills)
    return JsonResponse(results, safe=False)

# Adding new skill in website
@login_required
def add_skill(request):
    if request.method == 'POST':
        form = UserSkillForm(request.POST)
        if form.is_valid():
            # Don't save yet, we need to add the user
            user_skill = form.save(commit=False)
            user_skill.user = request.user
            user_skill.save()
            return redirect('dashboard')
    else:
        form = UserSkillForm()
    
    return render(request, 'core/add_skill.html', {'form': form})

# Delete Skill
@login_required
def delete_skill(request, skill_id):
    # Get the skill, but ensure it belongs to the current user
    skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    skill.delete()
    return redirect('dashboard')



# Delete a conversation
@login_required
def delete_conversation(request, user_id):
    partner = get_object_or_404(User, id=user_id)
    
    # Delete ALL SwapRequests between you and this partner
    SwapRequest.objects.filter(
        Q(sender=request.user, receiver=partner) | 
        Q(sender=partner, receiver=request.user)
    ).delete()
    
    return redirect('dashboard')

# Real time chat refresh
@login_required
def get_messages(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    # Get messages between these two users
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | 
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    
    # Convert database objects to a list of dictionaries (JSON)
    messages_data = [{
        'sender': msg.sender.username,
        'content': msg.content,
        'is_me': msg.sender == request.user
    } for msg in messages]
    
    return JsonResponse(messages_data, safe=False)

# Create profile page
# Create profile page
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('edit_profile') 
        else:
            # THIS WILL REVEAL THE SECRET ERRORS
            print("🚨 USER FORM ERRORS:", u_form.errors)
            print("🚨 PROFILE FORM ERRORS:", p_form.errors)
    else:
        u_form = UserForm(instance=request.user)
        p_form = ProfileForm(instance=profile)

    return render(request, 'core/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })
# Refresh for newer requests
@login_required
def check_updates(request):
    # 1. Count pending swap requests where YOU are the receiver
    pending_requests = SwapRequest.objects.filter(receiver=request.user, status='PENDING').count()
    
    # 2. Count ONLY unread messages where YOU are the receiver
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    return JsonResponse({
        'pending_count': pending_requests,
        'unread_count': unread_messages
    })

# Delete the account
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('signup')  # Send them to signup after deletion
    return render(request, 'core/delete_confirm.html')
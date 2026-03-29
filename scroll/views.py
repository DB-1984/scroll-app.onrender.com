from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Entry, Label
from django.contrib.auth import login
from .forms import EntryForm, SearchForm
from django.db.models import Q

@ensure_csrf_cookie # mostly covers partials not automatically sending CSRF
@login_required # <--- ESSENTIAL: Ensures request.user exists for the POST
def index(request):
    # 1. Start with all entries
    entries = Entry.objects.filter(user=request.user).order_by('-created_at')
    
    # 2. Initialize the Forms - intercept based on req type
    search_form = SearchForm(request.GET or None)
    entry_form = EntryForm(request.POST or None) # empty form instantiated in index.html if None

    # 3. Handle Search Logic (GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('q')
        if query:
            entries = entries.filter(
                Q(body__icontains=query) | Q(label__name__icontains=query) # use 'Q' for OR
            )
            
        # If HTMX is searching, just return the list partial
        if request.headers.get('HX-Request') and request.method == 'GET':
            return render(request, 'scroll/entry_list_partial.html', {'entries': entries})

    # 4. Handle Post Logic (POST)
    if request.method == 'POST' and entry_form.is_valid():
        entry = entry_form.save(commit=False)
        entry.user = request.user

        label_text = entry_form.cleaned_data.get('label_name', '').strip().lower()
        
        if label_text:
            # 2. The "Signpost" Logic: Find or create the Label object
            label_obj, _ = Label.objects.get_or_create(name=label_text)
            # 3. Manually link the ID to the Entry
            entry.label = label_obj

        entry.save()
        
        # If HTMX is posting, return only the new entry to be prepended
        # entry_list_partial expects an 'entries' list, and we're feeding it the new entry
        if request.headers.get('HX-Request'):
            return render(request, 'scroll/entry_list_partial.html', {'entries': [entry]})
            
        return redirect('index')

    # 5. The standard page load (The "Chef" delivers the tray)
    return render(request, 'scroll/index.html', {
        'entries': entries,
        'entry_form': entry_form,
        'search_form': search_form,
    })

@login_required
def delete_entry(request, pk):
    # This filter is your 'Authorization' check
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    entry.delete()
    return HttpResponse("")

@login_required
def edit_entry(request, pk):
    entry = get_object_or_404(Entry, pk=pk)
    
    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)
        if form.is_valid():
            # 1. Hold it in memory
            entry = form.save(commit=False) 

            # 2. String-to-Object conversion
            label_text = form.cleaned_data.get('label_name')
            if label_text:
                label_obj, _ = Label.objects.get_or_create(name=label_text)
                entry.label = label_obj
            else:
                entry.label = None # Clear it if the user deleted the text

            # 3. CRITICAL: call save() on the object now!
            entry.save() 
            
            # 4. Return the updated item to HTMX
            return render(request, 'scroll/entry_item.html', {'entry': entry})
            
    else:
        # Pre-fill for the GET request
        initial_data = {'label_name': entry.label.name if entry.label else ''}
        form = EntryForm(instance=entry, initial=initial_data)
    
    return render(request, 'scroll/entry_edit_partial.html', { # update the list view item
        'entry': entry,
        'entry_form': form
    })

@login_required # <--- ADDED THIS
def get_entry(request, pk):
    # Important: Still filter by user so people can't 'peek' at others' entries
    entry = get_object_or_404(Entry, pk=pk, user=request.user)
    return render(request, 'scroll/entry_item.html', {'entry': entry})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log them in immediately after signing up
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def share_entry_email(request, pk):
    if request.method == "POST":
        entry = get_object_or_404(Entry, pk=pk)
        recipient = request.POST.get('email')

        if not recipient:
            return HttpResponse('<span class="text-xs text-red-500">Enter an email!</span>')
        
        # This uses your existing Resend SMTP config
        send_mail(
            subject=f"A Scroll shared by {request.user.username}",
            message=f"Check this out: {entry.body}",
            from_email="Scroll <onboarding@resend.dev>", # Must match Resend's allowed sender
            recipient_list=[recipient],
            fail_silently=False,
        )
        return HttpResponse('<span class="text-xs text-black">Sent!</span>')


@login_required
def labels_list(request):
    labels = Label.objects.filter(entries__user=request.user).distinct()
    
    return render(request, 'scroll/labels.html', {
        'labels': labels
    })
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.urls import reverse

from .models import Activity, Area, Connection
from .forms import (
        AreaForm,
	CommandForm,
        ConnectionForm,
        DeleteForm,
        SelectAreaForm,
)
from .interpreter import Interpreter

def index(request):

    error = None

    # If data has been posted, redirect to room
    if request.method == 'POST':
        try:
            area = Area.objects.get(title=request.POST['area_title'])
            return HttpResponseRedirect(reverse('explore:area', kwargs={'area_id': area.id}))
        except ObjectDoesNotExist:
            try:
                area = Area(title=request.POST['area_title'], creator=request.user, published=True)
                area.save()
                return HttpResponseRedirect(reverse('explore:area', kwargs={'area_id': area.id}))
            except ValueError:
                error = 'No area by that name exists. To create one, you can <a href="/accounts/login?next=/explore">login</a> or <a href="/accounts/register?next=/explore">create an account</a>.'

    top_users = User.objects.exclude(username='admin').order_by('-score__total')[:5]
    context = {
        'select_area_form': SelectAreaForm,
        'user': request.user,
        'areas': Area.objects.filter(published=True),
        'top_users': top_users,
        'error': error,
    }
    return render(request, 'explore/index.html', context)

def area(request, area_id):

    # Get area object
    area = get_object_or_404(Area, id=area_id)

    # If data has been posted, handle the command
    if request.method == 'POST':
        # Create and validate a form
        form = CommandForm(request.POST)
        if form.is_valid():
            # Create the interpreter
            i = Interpreter({'user': request.user, 'area': area})
            path = i.execute(form.cleaned_data["command_text"])
            if path is not None:
                return HttpResponseRedirect(path)

    # Get a list of activities
    if request.user.is_authenticated:
        for_user = Q(creator_only=False) | Q(creator=request.user)
    else:
        for_user = Q(creator_only=False)
    activities = Activity.objects.filter(area=area).filter(for_user).order_by('created_at')

    # Build context and render the template
    context = {
       'user': request.user,
       'area': area,
       'activities': activities,
       'command_form': CommandForm(label_suffix='')
    }
    return render(request, 'explore/room.html', context)

@login_required
def area_description(request, area_id):

    # Look up area object
    area = get_object_or_404(Area, id=area_id)

    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = AreaForm(request.POST)
        if form.is_valid():
            area.description = request.POST.get('description', '')
            area.save()
            # Update scores
            if request.user.id != area.creator.id:
                score = area.creator.score
                score.total += 10
                score.save()
            return HttpResponseRedirect(reverse('explore:area', args=[area_id]))

    # Render edit form
    context = {
        'area': area,
        'area_form': AreaForm(initial={'description': area.description}),
        'user': request.user,
    }
    return render(request, 'explore/area_detail.html', context)

@login_required
def new_connection(request, source_id, title):

    # Look up source area object
    area_from = get_object_or_404(Area, id=source_id)

    # Check whether connection exists
    try:
        connection = Connection.objects.get(area_from=area_from, title=title)
        activity = Activity(
            creator=request.user,
            creator_only=True,
            area=area_from,
            activity_text=f'Unable to create connection "{title}": already exists'
        )
        activity.save()
        return HttpResponseRedirect(reverse('explore:area', args=[area_from.id]))        
    except ObjectDoesNotExist:
        pass

    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = ConnectionForm(request.POST)
        if form.is_valid():
            area_to, created = Area.objects.get_or_create(
                title=form.cleaned_data['destination_title'],
                defaults={ 'creator': request.user })
            connection, created = Connection.objects.get_or_create(
                title=title,
                area_from=area_from,
                defaults={ 'area_to': area_to, 'creator': request.user }
            )
            if created:
                connection.save()
                # Update scores
                if area_from.creator.id != request.user.id:
                    score = area_from.creator.score
                    score.total += 10
                    score.save()
                if area_to.creator.id != request.user.id:
                    score = area_to.creator.score
                    score.total += 10
                    score.save()
            return HttpResponseRedirect(reverse('explore:area', args=[area_from.id]))

    # Render edit form
    context = {
        'title': title,
        'area_from': area_from,
        'connection_form': ConnectionForm(),
        'user': request.user,
    }
    return render(request, 'explore/connection_detail.html', context)

@login_required
def delete_connection(request, source_id, title):

    # Look up source area object and connection
    area_from = get_object_or_404(Area, id=source_id)
    
    # Check whether connection exists
    try:
        connection = Connection.objects.get(area_from=area_from, title=title)
    except ObjectDoesNotExist:
        activity = Activity(
            creator=request.user,
            creator_only=True,
            area=area_from,
            activity_text=f'Unable to delete connection "{title}": does not exist'
        )
        activity.save()
        return HttpResponseRedirect(reverse('explore:area', args=[area_from.id]))        

    # Check for changes
    if request.method == 'POST':
        # Create and validate a form
        form = DeleteForm(request.POST)
        if form.is_valid():
            area_to = connection.area_to
            connection.delete()
            # Update scores
            if area_from.creator.id != request.user.id:
                score = area_from.creator.score
                score.total += 5
                score.save()
            if area_to.creator.id != request.user.id:
                score = area_to.creator.score
                score.total += 5
                score.save()
            return HttpResponseRedirect(reverse('explore:area', args=[area_from.id]))

    # Render delete form
    context = {
        'type': 'Connection',
        'title': f'{title} : {connection.title} : {connection.area_to}',
        'form': DeleteForm(),
        'user': request.user,
    }
    return render(request, 'explore/delete.html', context)

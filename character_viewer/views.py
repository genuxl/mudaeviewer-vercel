import json
import zipfile
import os
import shutil
from django.shortcuts import render
from django.core.paginator import Paginator
from django.conf import settings
from .models import Character
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

@login_required
def upload_and_view(request):
    characters = []
    paginator = None
    page_obj = None
    error_message = None
    
    # Handle uploaded JSON file
    if request.method == 'POST' and request.FILES.get('json_file'):
        uploaded_file = request.FILES['json_file']
        
        try:
            # Process the uploaded JSON file directly
            # Read the file content
            file_content = uploaded_file.read().decode('utf-8')
            data = json.loads(file_content)
                    
            # Clear existing characters for current user
            Character.objects.filter(user=request.user).delete()
            
            # Save new characters to database with sort_order
            sort_order = 0
            for char_data in data['characters']:
                # The image field in the JSON should already contain the full URL
                image_url = char_data.get('image', '')
                # Keep the image URL as is (whether it's from cdn.imgchest.com, imgur, or mudae.net)
                
                Character.objects.create(
                    user=request.user,
                    rank=char_data.get('rank', ''),
                    name=char_data.get('name', ''),
                    series=char_data.get('series', ''),
                    value=char_data.get('value', ''),
                    note=char_data.get('note', ''),
                    image=image_url,  # Store the full image URL as provided in the JSON
                    sort_order=sort_order,  # Add the order in which they appear in the JSON
                    in_trade_list=False,  # Initialize to not in trade list
                )
                sort_order += 1
        except json.JSONDecodeError:
            # Handle invalid JSON file
            error_message = "Invalid JSON file format"
        except Exception as e:
            # Handle any other errors during upload processing
            error_message = f"Error processing uploaded file: {str(e)}"
        
        # If there was an error, we should handle it appropriately
        if 'error_message' in locals() and error_message:
            # For now, just continue to show the page but with error handling
            # In the future, you might want to show the error differently
            pass
    
    # Handle search
    search_query = request.GET.get('search', '')
    
    # Handle sorting
    sort_by = request.GET.get('sort_by', 'default')  # default, rank, kakera
    
    # Get all characters from database for current user
    if search_query:
        all_characters = Character.objects.filter(
            user=request.user,
            name__icontains=search_query
        )
    else:
        all_characters = Character.objects.filter(user=request.user)
    
    if sort_by == 'rank':
        # Sort by rank (extract numeric value from the rank string like "#1,275")
        # This requires a custom sorting using extra() or manual sorting
        all_characters = all_characters.extra(
            select={'rank_numeric': "CAST(REPLACE(REPLACE(rank, '#', ''), ',', '') AS INTEGER)"}
        ).order_by('rank_numeric')
    elif sort_by == 'kakera':
        # Sort by value (kakera) in descending order, extracting numeric value
        all_characters = all_characters.extra(
            select={'kakera_value': "CAST(REPLACE(value, ' ka', '') AS INTEGER)"}
        ).order_by('-kakera_value')
    else:  # default order
        all_characters = all_characters.order_by('sort_order')  # Order by JSON order
    
    # Paginate characters (10 per page)
    paginator = Paginator(all_characters, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prepare the page object with image URL availability check
    for character in page_obj:
        # Check if image is a valid URL (add a property to indicate if image is available)
        if character.image and (character.image.startswith('http://') or character.image.startswith('https://')):
            character.image_exists = True  # Assume URL-based images are available
        else:
            character.image_exists = bool(character.image)  # For backward compatibility
    
    context = {
        'page_obj': page_obj,
        'sort_by': sort_by,
        'total_characters': all_characters.count(),
        'MEDIA_URL': settings.MEDIA_URL,
    }
    
    # Add error message if there was one
    if 'error_message' in locals() and error_message:
        # Instead of displaying error as context (because it might get overwritten),
        # we can add it to the context with a more specific approach
        context['error_message'] = error_message
    
    return render(request, 'character_viewer/upload_and_view.html', context)

@login_required
def trade_list(request):
    # Handle search within the trade list
    search_query = request.GET.get('search', '')
    
    # Get all characters that are in the trade list for current user
    trade_characters = Character.objects.filter(user=request.user, in_trade_list=True)
    
    # Apply search filter if provided
    if search_query:
        trade_characters = trade_characters.filter(
            name__icontains=search_query
        )
    
    # Order by sort_order
    trade_characters = trade_characters.order_by('sort_order')
    
    # Paginate trade characters (10 per page)
    paginator = Paginator(trade_characters, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Prepare the page object with image URL availability check
    for character in page_obj:
        # Check if image is a valid URL (add a property to indicate if image is available)
        if character.image and (character.image.startswith('http://') or character.image.startswith('https://')):
            character.image_exists = True  # Assume URL-based images are available
        else:
            character.image_exists = bool(character.image)  # For backward compatibility
    
    context = {
        'page_obj': page_obj,
        'MEDIA_URL': settings.MEDIA_URL,
        'search_query': search_query,
    }
    
    return render(request, 'character_viewer/trade_list.html', context)

@csrf_exempt
@login_required
def toggle_trade_list(request):
    if request.method == 'POST':
        character_id = request.POST.get('character_id')
        try:
            character = Character.objects.get(id=character_id, user=request.user)
            character.in_trade_list = not character.in_trade_list
            character.save()
            return JsonResponse({
                'status': 'success',
                'in_trade_list': character.in_trade_list,
                'character_name': character.name
            })
        except Character.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Character not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def clear_all(request):
    """Delete all characters for the current user and reload the page."""
    if request.method == 'POST':
        # Delete all characters for the current user
        Character.objects.filter(user=request.user).delete()
        # Redirect back to the main page
        return HttpResponseRedirect(reverse('upload_and_view'))
    
    # If not a POST request, redirect back to the main page
    return HttpResponseRedirect(reverse('upload_and_view'))


from django.contrib.auth.hashers import make_password
import os

from django.views.decorators.csrf import csrf_protect

@csrf_protect
def temp_create_admin(request):
    flag_file = os.path.join(os.path.dirname(__file__), 'admin_created.flag')
    
    # Check if admin user already exists by checking flag file
    if os.path.exists(flag_file):
        return HttpResponse("Admin already created. This endpoint is disabled.", status=403)
    
    if request.method == 'POST':
        username = request.POST.get('username', 'admin')
        email = request.POST.get('email', 'admin@example.com')
        password = request.POST.get('password', 'admin123')
        
        # Import User inside the function to avoid circular imports
        from django.contrib.auth.models import User
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            # Create a flag file to indicate admin is created
            with open(flag_file, 'w') as f:
                f.write('admin created')
            
            return HttpResponse(f"Admin user '{username}' created successfully. Please remove this view for security.")
        else:
            return HttpResponse("Admin user already exists.")
    
    # Show a form to create admin with CSRF token
    from django.template import Context, Template
    from django.template.context_processors import csrf
    
    # Get CSRF token
    csrf_ctx = {}
    csrf_ctx.update(csrf(request))
    csrf_token = csrf_ctx['csrf_token']
    
    form_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Create Admin User</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif;
                background-color: #36393F;
                color: #DCDDDE;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                background-color: #2F3136;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.5);
                width: 300px;
            }}
            .form-group {{
                margin-bottom: 15px;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 5px;
            }}
            .form-group input {{
                width: 100%;
                padding: 8px;
                border: 1px solid #36393F;
                border-radius: 4px;
                background-color: #40444B;
                color: #DCDDDE;
                box-sizing: border-box;
            }}
            .btn {{
                width: 100%;
                padding: 10px;
                background-color: #5865F2;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            .btn:hover {{
                background-color: #4752C4;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Create Admin User</h2>
            <form method="post">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Create Admin</button>
            </form>
        </div>
    </body>
    </html>
    '''
    return HttpResponse(form_html)

@login_required
def remove_all_from_trade_list(request):
    """Remove all characters from the trade list for the current user and reload the page."""
    if request.method == 'POST':
        # Set in_trade_list to False for all characters of the current user
        Character.objects.filter(user=request.user, in_trade_list=True).update(in_trade_list=False)
        # Redirect back to the trade list page
        return HttpResponseRedirect(reverse('trade_list'))
    
    # If not a POST request, redirect back to the trade list page
    return HttpResponseRedirect(reverse('trade_list'))
import json
import zipfile
import os
import shutil
from django.shortcuts import render
from django.core.paginator import Paginator
from django.conf import settings
from .models import Character
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.urls import reverse

def upload_and_view(request):
    characters = []
    paginator = None
    page_obj = None
    error_message = None
    
    # Handle uploaded zip file
    if request.method == 'POST' and request.FILES.get('zip_file'):
        uploaded_file = request.FILES['zip_file']
        
        try:
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save uploaded file temporarily
            temp_path = os.path.join(upload_dir, uploaded_file.name)
            with open(temp_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Extract the zip file with security checks
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                # Security check: prevent zip slip vulnerability
                for member in zip_ref.namelist():
                    # Resolve the path to ensure it doesn't contain '..'
                    safe_path = os.path.realpath(os.path.join(upload_dir, 'extracted'))
                    extracted_path = os.path.realpath(os.path.join(upload_dir, 'extracted', member))
                    if not extracted_path.startswith(safe_path):
                        raise Exception("Unsafe zip file: contains directory traversal")
                
                extract_dir = os.path.join(upload_dir, 'extracted')
                os.makedirs(extract_dir, exist_ok=True)
                zip_ref.extractall(extract_dir)
            
            # Move images to MEDIA_ROOT so Django can serve them
            images_dir = os.path.join(settings.MEDIA_ROOT, 'images')
            os.makedirs(images_dir, exist_ok=True)
            
            # Find and move image files
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        src_path = os.path.join(root, file)
                        dest_path = os.path.join(images_dir, file)
                        # Security check: verify that source path is under extract_dir
                        if os.path.commonpath([extract_dir]) == os.path.commonpath([extract_dir, src_path]):
                            shutil.move(src_path, dest_path)
            
            # Look for data.json in the extracted files
            data_json_path = os.path.join(extract_dir, 'data.json')
            if os.path.exists(data_json_path):
                with open(data_json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Clear existing characters
                Character.objects.all().delete()
                
                # Save new characters to database with sort_order
                sort_order = 0
                for char_data in data['characters']:
                    image_path = char_data.get('image', '')
                    # Update the image path to point to the media directory
                    if image_path:
                        filename = os.path.basename(image_path)
                        new_image_path = f"images/{filename}"  # Store relative path to images folder
                    else:
                        new_image_path = ""
                    
                    Character.objects.create(
                        rank=char_data.get('rank', ''),
                        name=char_data.get('name', ''),
                        series=char_data.get('series', ''),
                        value=char_data.get('value', ''),
                        note=char_data.get('note', ''),
                        image=new_image_path,  # Store just the filename part
                        sort_order=sort_order,  # Add the order in which they appear in the JSON
                        in_trade_list=False,  # Initialize to not in trade list
                    )
                    sort_order += 1
        except zipfile.BadZipFile:
            # Handle invalid zip file
            error_message = "Invalid zip file format"
        except Exception as e:
            # Handle any other errors during upload processing
            error_message = f"Error processing uploaded file: {str(e)}"
        finally:
            # Clean up temporary files
            try:
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.remove(temp_path)
                if 'extract_dir' in locals() and os.path.exists(extract_dir):
                    import shutil
                    shutil.rmtree(extract_dir)
            except:
                pass  # Ignore cleanup errors
        
        # If there was an error, we should handle it appropriately
        if 'error_message' in locals() and error_message:
            # For now, just continue to show the page but with error handling
            # In the future, you might want to show the error differently
            pass
    
    # Handle search
    search_query = request.GET.get('search', '')
    
    # Handle sorting
    sort_by = request.GET.get('sort_by', 'default')  # default, rank, kakera
    
    # Get all characters from database
    if search_query:
        all_characters = Character.objects.filter(
            name__icontains=search_query
        )
    else:
        all_characters = Character.objects.all()
    
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
    
    # Prepare the page object with extra image existence check
    for character in page_obj:
        # Check if image file exists (add a property to indicate if image is available)
        if character.image:
            import os
            image_path = os.path.join(settings.MEDIA_ROOT, character.image)
            character.image_exists = os.path.exists(image_path)
        else:
            character.image_exists = False
    
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

def trade_list(request):
    # Handle search within the trade list
    search_query = request.GET.get('search', '')
    
    # Get all characters that are in the trade list
    trade_characters = Character.objects.filter(in_trade_list=True)
    
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
    
    # Prepare the page object with extra image existence check
    for character in page_obj:
        # Check if image file exists (add a property to indicate if image is available)
        if character.image:
            import os
            image_path = os.path.join(settings.MEDIA_ROOT, character.image)
            character.image_exists = os.path.exists(image_path)
        else:
            character.image_exists = False
    
    context = {
        'page_obj': page_obj,
        'MEDIA_URL': settings.MEDIA_URL,
        'search_query': search_query,
    }
    
    return render(request, 'character_viewer/trade_list.html', context)

@csrf_exempt
def toggle_trade_list(request):
    if request.method == 'POST':
        character_id = request.POST.get('character_id')
        try:
            character = Character.objects.get(id=character_id)
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


def clear_all(request):
    """Delete all characters from the database and reload the page."""
    if request.method == 'POST':
        # Delete all characters from the database
        Character.objects.all().delete()
        # Redirect back to the main page
        return HttpResponseRedirect(reverse('upload_and_view'))
    
    # If not a POST request, redirect back to the main page
    return HttpResponseRedirect(reverse('upload_and_view'))


def remove_all_from_trade_list(request):
    """Remove all characters from the trade list and reload the page."""
    if request.method == 'POST':
        # Set in_trade_list to False for all characters
        Character.objects.filter(in_trade_list=True).update(in_trade_list=False)
        # Redirect back to the trade list page
        return HttpResponseRedirect(reverse('trade_list'))
    
    # If not a POST request, redirect back to the trade list page
    return HttpResponseRedirect(reverse('trade_list'))
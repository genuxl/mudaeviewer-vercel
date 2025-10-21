# Mudae Viewer List

This is a Django web application that allows users to upload, view, and manage their Mudae character lists.

## Changes Made to Fix Authentication Issues

I have made several important changes to fix the server error 500 that was occurring with the register and login functions:

1. **Updated the registration view** (`character_viewer/views.py`):
   - Replaced the previous implementation that generated raw HTML with a proper Django template-based approach
   - Added proper error handling for database operations
   - Implemented proper user validation and error feedback
   - Added try-catch blocks to handle potential database connection issues

2. **Created a registration template** (`templates/registration/register.html`):
   - Added a clean, consistent registration form that matches the login page style
   - Implemented proper error message display
   - Added CSRF protection

3. **Fixed media file handling** (`character_viewer/cleanup.py`):
   - Improved the temporary media directory creation to better handle Render's ephemeral file system
   - Added fallback mechanisms in case the primary temp directory creation fails

4. **Resolved static files configuration** (`mudae_project/settings.py`):
   - Fixed the static files directory warning by conditionally adding the static directory only if it exists
   - Updated authentication redirect URLs to point to appropriate views

5. **Improved error handling**:
   - Added proper logging for debugging authentication issues
   - Added comprehensive error handling throughout the authentication flow

These changes address the server error 500 issues that were occurring with the registration and login functions, particularly in the Render deployment environment where database connections and file system access can be more restrictive.

To use this application:

1. Clone the repository
2. Install dependencies (`pip install -r requirements.txt`)
3. Run database migrations (`python manage.py migrate`)
4. Start the server (`python manage.py runserver`)

The application should now properly handle user registration and login without server errors.
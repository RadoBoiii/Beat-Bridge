import os
import secrets
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_oauthlib.client import OAuth
from dotenv import load_dotenv
from utils.helpers import extract_playlist_id, get_platform_name
from utils.validators import validate_playlist_url

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(16))
app.config['SESSION_TYPE'] = 'filesystem'

# Backend service URL
BACKEND_URL = os.getenv('CONVERSION_SERVICE_URL', 'http://localhost:5001')

# Set up OAuth
oauth = OAuth(app)

# Configure Spotify OAuth
spotify = oauth.remote_app(
    'spotify',
    consumer_key=os.getenv('SPOTIFY_CLIENT_ID'),
    consumer_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    request_token_params={'scope': 'playlist-read-private playlist-modify-public playlist-modify-private'},
    base_url='https://api.spotify.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.spotify.com/api/token',
    authorize_url='https://accounts.spotify.com/authorize'
)

@app.route('/')
def index():
    """Home page with playlist conversion form"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page with information about the service"""
    return render_template('about.html')

@app.route('/process', methods=['POST'])
def process():
    """Process the conversion form and start the authentication flow"""
    # Get form data
    source_platform = request.form.get('source_platform')
    destination_platform = request.form.get('destination_platform')
    playlist_url = request.form.get('playlist_url')
    
    # Validate inputs
    if not source_platform or not destination_platform:
        flash("Please select both source and destination platforms.", "error")
        return redirect(url_for('index'))
    
    if source_platform == destination_platform:
        flash("Source and destination platforms cannot be the same.", "error")
        return redirect(url_for('index'))
    
    # Validate playlist URL
    valid, message = validate_playlist_url(playlist_url, source_platform)
    if not valid:
        flash(message, "error")
        return redirect(url_for('index'))
    
    # Extract playlist ID from URL
    playlist_id = extract_playlist_id(playlist_url, source_platform)
    if not playlist_id:
        flash("Could not extract playlist ID from the URL. Please check the URL and try again.", "error")
        return redirect(url_for('index'))
    
    # Store in session for later use
    session['source_platform'] = source_platform
    session['destination_platform'] = destination_platform
    session['playlist_url'] = playlist_url
    session['playlist_id'] = playlist_id
    
    # Clear any previous conversion results
    if 'conversion_result' in session:
        del session['conversion_result']
    
    # Determine auth flow based on source platform
    if source_platform == 'spotify':
        return redirect(url_for('spotify_auth'))
    elif source_platform == 'apple_music':
        # For Apple Music, we need to use Apple's MusicKit JS
        # For this example, we'll simulate auth
        session['source_auth_complete'] = True
        return redirect(url_for('destination_auth'))
    elif source_platform == 'youtube_music':
        # For YouTube Music, use Google OAuth
        # For this example, we'll simulate auth
        session['source_auth_complete'] = True
        return redirect(url_for('destination_auth'))
    else:
        flash(f"Unsupported source platform: {source_platform}", "error")
        return redirect(url_for('index'))

@app.route('/destination-auth')
def destination_auth():
    """Start authentication flow for the destination platform"""
    destination = session.get('destination_platform')
    
    if not destination:
        flash("Session expired. Please try again.", "error")
        return redirect(url_for('index'))
    
    if destination == 'spotify':
        return redirect(url_for('spotify_auth', is_destination=True))
    elif destination == 'apple_music':
        # Simulate Apple Music auth
        session['destination_auth_complete'] = True
        return redirect(url_for('convert_playlist'))
    elif destination == 'youtube_music':
        # Simulate YouTube Music auth
        session['destination_auth_complete'] = True
        return redirect(url_for('convert_playlist'))
    else:
        flash(f"Unsupported destination platform: {destination}", "error")
        return redirect(url_for('index'))

@app.route('/spotify-auth')
def spotify_auth():
    """Authenticate with Spotify"""
    is_destination = request.args.get('is_destination', False)
    
    # Store whether this is source or destination auth
    if is_destination:
        session['spotify_auth_type'] = 'destination'
    else:
        session['spotify_auth_type'] = 'source'
    
    callback = url_for('spotify_callback', _external=True)
    return spotify.authorize(callback=callback)

@app.route('/spotify-callback')
def spotify_callback():
    """Callback from Spotify OAuth"""
    resp = spotify.authorized_response()
    if resp is None or 'access_token' not in resp:
        error_reason = request.args.get('error_reason', 'Unknown error')
        error_desc = request.args.get('error_description', 'No details available')
        flash(f"Access denied: {error_reason} - {error_desc}", "error")
        return redirect(url_for('index'))
    
    # Store token based on auth type
    auth_type = session.get('spotify_auth_type')
    if auth_type == 'source':
        session['spotify_source_token'] = resp['access_token']
        session['source_auth_complete'] = True
        return redirect(url_for('destination_auth'))
    else:  # destination
        session['spotify_destination_token'] = resp['access_token']
        session['destination_auth_complete'] = True
        return redirect(url_for('convert_playlist'))

@app.route('/apple-music-auth')
def apple_music_auth():
    """
    In a real implementation, this would redirect to a page with 
    Apple's MusicKit JS to handle authentication.
    For this example, we'll simulate the auth flow.
    """
    is_destination = request.args.get('is_destination', False)
    
    # Simulate successful auth
    if is_destination:
        session['destination_auth_complete'] = True
        return redirect(url_for('convert_playlist'))
    else:
        session['source_auth_complete'] = True
        return redirect(url_for('destination_auth'))

@app.route('/youtube-music-auth')
def youtube_music_auth():
    """
    In a real implementation, this would use Google OAuth.
    For this example, we'll simulate the auth flow.
    """
    is_destination = request.args.get('is_destination', False)
    
    # Simulate successful auth
    if is_destination:
        session['destination_auth_complete'] = True
        return redirect(url_for('convert_playlist'))
    else:
        session['source_auth_complete'] = True
        return redirect(url_for('destination_auth'))

@app.route('/convert')
def convert_playlist():
    """Start the playlist conversion process"""
    # Check if we have all necessary auth and data
    source = session.get('source_platform')
    destination = session.get('destination_platform')
    playlist_id = session.get('playlist_id')
    source_auth = session.get('source_auth_complete')
    destination_auth = session.get('destination_auth_complete')
    
    # Validate session data
    if not all([source, destination, playlist_id, source_auth, destination_auth]):
        flash("Session data is incomplete. Please try again.", "error")
        return redirect(url_for('index'))
    
    # Prepare data for the backend request
    payload = {
        'source_platform': source,
        'destination_platform': destination,
        'playlist_id': playlist_id,
    }
    
    # Add platform-specific tokens
    if source == 'spotify':
        payload['spotify_source_token'] = session.get('spotify_source_token')
    if destination == 'spotify':
        payload['spotify_destination_token'] = session.get('spotify_destination_token')
    
    # Make API call to our backend conversion service
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/convert",
            json=payload,
            timeout=10  # 10-second timeout
        )
        
        response.raise_for_status()  # Raise exception for HTTP errors
        result = response.json()
        
        if result.get('success'):
            # Store job ID for status polling
            session['conversion_job_id'] = result.get('job_id')
            return redirect(url_for('conversion_progress'))
        else:
            flash(f"Failed to start conversion: {result.get('message')}", "error")
            return redirect(url_for('index'))
            
    except requests.RequestException as e:
        flash(f"Error communicating with conversion service: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/progress')
def conversion_progress():
    """Show conversion progress page"""
    job_id = session.get('conversion_job_id')
    
    if not job_id:
        flash("No active conversion job found. Please try again.", "error")
        return redirect(url_for('index'))
    
    # Get source and destination platform names for the UI
    source = get_platform_name(session.get('source_platform', ''))
    destination = get_platform_name(session.get('destination_platform', ''))
    
    return render_template(
        'progress.html',
        job_id=job_id,
        source_platform=source,
        destination_platform=destination
    )

@app.route('/api/status/<job_id>')
def check_status(job_id):
    """API endpoint to check conversion status"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/status/{job_id}",
            timeout=5
        )
        
        if response.status_code == 404:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
            
        result = response.json()
        
        # If job is complete, store result in session
        if result.get('status') == 'completed':
            session['conversion_result'] = result.get('result')
        
        return jsonify(result)
        
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'message': f"Error communicating with conversion service: {str(e)}"
        }), 500

@app.route('/result')
def show_result():
    """Show conversion result page"""
    result = session.get('conversion_result')
    
    if not result:
        flash("No conversion result found. Please try again.", "error")
        return redirect(url_for('index'))
    
    # Get source and destination platform names for the UI
    source = get_platform_name(session.get('source_platform', ''))
    destination = get_platform_name(session.get('destination_platform', ''))
    
    return render_template(
        'result.html',
        success=result.get('success', False),
        message=result.get('message', ''),
        playlist_url=result.get('playlist_url', ''),
        failed_tracks=result.get('failed_tracks', []),
        source_platform=source,
        destination_platform=destination
    )

@app.route('/clear')
def clear_session():
    """Clear session data and return to home page"""
    session.clear()
    flash("Session cleared. You can start a new conversion.", "info")
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, message="Server error"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
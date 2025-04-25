"""Database models for the BeatBridge application."""

from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ConversionJob(db.Model):
    """Model to store playlist conversion jobs."""
    
    id = db.Column(db.String(36), primary_key=True)
    source_platform = db.Column(db.String(50), nullable=False)
    destination_platform = db.Column(db.String(50), nullable=False)
    source_playlist_id = db.Column(db.String(255), nullable=False)
    source_playlist_name = db.Column(db.String(255), nullable=True)
    destination_playlist_id = db.Column(db.String(255), nullable=True)
    destination_playlist_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)
    total_tracks = db.Column(db.Integer, default=0)
    matched_tracks = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Store the list of failed tracks as JSON
    _failed_tracks = db.Column('failed_tracks', db.Text, nullable=True)
    
    @property
    def failed_tracks(self):
        """Get the failed tracks as a list of dictionaries."""
        if self._failed_tracks:
            return json.loads(self._failed_tracks)
        return []
    
    @failed_tracks.setter
    def failed_tracks(self, value):
        """Set the failed tracks from a list of dictionaries."""
        if value:
            self._failed_tracks = json.dumps(value)
        else:
            self._failed_tracks = None
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': self.id,
            'source_platform': self.source_platform,
            'destination_platform': self.destination_platform,
            'source_playlist_id': self.source_playlist_id,
            'source_playlist_name': self.source_playlist_name,
            'destination_playlist_id': self.destination_playlist_id,
            'destination_playlist_url': self.destination_playlist_url,
            'status': self.status,
            'progress': self.progress,
            'total_tracks': self.total_tracks,
            'matched_tracks': self.matched_tracks,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'failed_tracks': self.failed_tracks
        }
    
    def __repr__(self):
        """String representation of the model."""
        return f'<ConversionJob {self.id}>'


class User(db.Model):
    """Model to store user information (optional for advanced features)."""
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    spotify_refresh_token = db.Column(db.String(255), nullable=True)
    apple_music_token = db.Column(db.String(255), nullable=True)
    youtube_refresh_token = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship with conversion jobs
    jobs = db.relationship('ConversionJob', backref='user', lazy=True)
    
    def to_dict(self):
        """Convert the model to a dictionary (excluding sensitive fields)."""
        return {
            'id': self.id,
            'email': self.email,
            'has_spotify_token': bool(self.spotify_refresh_token),
            'has_apple_music_token': bool(self.apple_music_token),
            'has_youtube_token': bool(self.youtube_refresh_token),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        """String representation of the model."""
        return f'<User {self.email}>'
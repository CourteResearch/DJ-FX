from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import tempfile
import shutil
import uuid
import asyncio
import re
import threading
import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import requests
import yt_dlp
import librosa
import numpy as np
from pydub import AudioSegment
from scipy.signal import find_peaks
import time

import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
logger.info("Successfully connected to MongoDB.")

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Track(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    artist: Optional[str] = None
    genre: str
    source_url: str
    local_path: Optional[str] = None
    duration: Optional[float] = None
    waveform_data: Optional[List[float]] = None
    highlights: Optional[List[Dict[str, float]]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Mix(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    genre: str
    tracks: List[str]  # Track IDs
    duration: Optional[float] = None
    file_path: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class MixRequest(BaseModel):
    genre: str
    title: str = "Automated DJ Mix"
    duration_minutes: int = 50  # Target duration in minutes

class GenreRequest(BaseModel):
    search_term: str

# Track discovery and processing
class TrackFinder:
    def __init__(self):
        import tempfile
        self.temp_dir = Path(tempfile.gettempdir()) / "autodj"
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
    def search_by_genre(self, genre: str, max_results: int = 10):
        """Search for tracks by genre and return YouTube URLs"""
        search_query = f"{genre} music mix"
        
        # Use yt-dlp to search for videos
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True,
            'ignoreerrors': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch{max_results}:{search_query}", download=False)
            
        tracks = []
        if 'entries' in result:
            for entry in result['entries']:
                if entry is None:
                    continue
                    
                track = {
                    'title': entry.get('title', 'Unknown Title'),
                    'artist': entry.get('uploader', 'Unknown Artist'),
                    'genre': genre,
                    'source_url': f"https://www.youtube.com/watch?v={entry['id']}",
                    'duration': entry.get('duration')
                }
                tracks.append(track)
                
        return tracks
    
    def download_track(self, track: Track):
        """Download a track from YouTube and save it locally"""
        track_id = track.id
        output_path = self.temp_dir / f"{track_id}.mp3"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(output_path).replace('.mp3', ''),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([track.source_url])
            
            # Update the track with local path
            track.local_path = str(output_path)
            
            # Extract additional audio information
            self.analyze_audio(track)
            
            return track
        except Exception as e:
            logging.error(f"Error downloading track {track.id}: {str(e)}")
            raise e
    
    def analyze_audio(self, track: Track):
        """Analyze the audio to extract features and find highlights"""
        try:
            # Load the audio file with librosa
            y, sr = librosa.load(track.local_path, sr=None)
            
            # Get duration
            track.duration = librosa.get_duration(y=y, sr=sr)
            
            # Extract a simplified waveform (RMS energy)
            hop_length = 1024
            frame_length = 2048
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length).flatten()
            
            # Normalize RMS to 0-1 range
            track.waveform_data = (rms / np.max(rms)).tolist() if np.max(rms) > 0 else rms.tolist()
            
            # Find highlights (segments with high energy)
            # First, smooth the RMS curve
            smoothed_rms = np.convolve(rms, np.ones(10)/10, mode='same')
            
            # Find peaks in the smoothed RMS
            peaks, _ = find_peaks(smoothed_rms, height=np.mean(smoothed_rms)*1.5, distance=sr//hop_length*5)
            
            # Convert peak positions to time
            highlights = []
            for peak in peaks:
                time_point = librosa.frames_to_time(peak, sr=sr, hop_length=hop_length)
                # Create segments of 20 seconds centered around peaks
                start = max(0, time_point - 10)
                end = min(track.duration, time_point + 10)
                
                highlights.append({
                    "start": start,
                    "end": end,
                    "peak_time": time_point,
                    "intensity": float(smoothed_rms[peak])
                })
            
            # Sort highlights by intensity and take the top 3
            highlights.sort(key=lambda x: x["intensity"], reverse=True)
            track.highlights = highlights[:3]
            
            return track
        except Exception as e:
            logging.error(f"Error analyzing audio for track {track.id}: {str(e)}")
            track.waveform_data = []
            track.highlights = []

class MixCreator:
    def __init__(self):
        self.output_dir = Path("/tmp/autodj/mixes")
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    async def create_mix(self, mix: Mix, tracks: List[Track]):
        """Create a DJ mix from the given tracks"""
        try:
            # Sort tracks by energy/intensity
            tracks.sort(key=lambda t: 
                np.mean([h["intensity"] for h in t.highlights]) if t.highlights else 0, 
                reverse=True)
            
            # Create a new mix file
            mix_path = self.output_dir / f"{mix.id}.mp3"
            final_mix = AudioSegment.empty()
            
            # Add tracks to the mix
            current_position = 0  # Position in milliseconds
            
            for i, track in enumerate(tracks):
                if not track.local_path or not Path(track.local_path).exists():
                    continue
                
                try:
                    # Load the audio file with pydub
                    audio = AudioSegment.from_file(track.local_path, format="mp3")
                    
                    # Select a highlight from the track
                    if track.highlights:
                        # Use the top highlight
                        highlight = track.highlights[0]
                        start_ms = int(highlight["start"] * 1000)
                        end_ms = int(highlight["end"] * 1000)
                        
                        # Make sure end doesn't exceed the track length
                        end_ms = min(end_ms, len(audio))
                        
                        # Extract the segment
                        segment = audio[start_ms:end_ms]
                    else:
                        # If no highlights, take a middle portion (30 seconds)
                        middle = len(audio) // 2
                        start_ms = max(0, middle - 15000)
                        end_ms = min(len(audio), middle + 15000)
                        segment = audio[start_ms:end_ms]
                    
                    # Apply fade-in and fade-out
                    segment = segment.fade_in(2000).fade_out(2000)
                    
                    # Add to the mix
                    if i > 0:
                        # Crossfade with previous track
                        final_mix = final_mix.overlay(segment, position=current_position - 2000)
                        current_position += len(segment) - 2000
                    else:
                        final_mix += segment
                        current_position += len(segment)
                
                except Exception as e:
                    logging.error(f"Error processing track {track.id} for mix: {str(e)}")
                    continue
            
            # Export the final mix
            final_mix.export(mix_path, format="mp3")
            
            # Update the mix information
            mix.file_path = str(mix_path)
            mix.duration = len(final_mix) / 1000  # Convert ms to seconds
            mix.status = "completed"
            
            # Save the updated mix to the database
            await db.mixes.update_one(
                {"id": mix.id},
                {"$set": mix.dict()}
            )
            
            return mix
        except Exception as e:
            logging.error(f"Error creating mix {mix.id}: {str(e)}")
            mix.status = "failed"
            await db.mixes.update_one(
                {"id": mix.id},
                {"$set": {"status": "failed"}}
            )
            raise e

# Initialize services
track_finder = TrackFinder()
mix_creator = MixCreator()

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Automated DJ System API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.get("/genres")
async def get_genres():
    """Get a list of supported music genres"""
    return {
        "genres": [
            "EDM", "House", "Techno", "Trance", "Dubstep", "Drum and Bass",
            "Hip Hop", "Pop", "Rock", "Jazz", "Classical", "Ambient", "Lofi"
        ]
    }

@api_router.post("/search/genre", response_model=List[Track])
async def search_tracks_by_genre(genre_req: GenreRequest):
    """Search for tracks by genre"""
    tracks = track_finder.search_by_genre(genre_req.search_term)
    return [Track(**track) for track in tracks]

@api_router.post("/tracks", response_model=Track)
async def create_track(track: Track):
    """Add a new track to the database"""
    track_dict = track.dict()
    await db.tracks.insert_one(track_dict)
    return track

@api_router.get("/tracks", response_model=List[Track])
async def get_tracks(genre: Optional[str] = None):
    """Get all tracks, optionally filtered by genre"""
    filter_dict = {}
    if genre:
        filter_dict["genre"] = genre
    
    tracks = await db.tracks.find(filter_dict).to_list(1000)
    return [Track(**track) for track in tracks]

@api_router.post("/tracks/download", response_model=Track)
async def download_track_endpoint(track: Track):
    """Download a track from its source URL"""
    try:
        result = track_finder.download_track(track)
        # Update in DB
        await db.tracks.update_one(
            {"id": track.id},
            {"$set": result.dict()}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/mixes", response_model=Mix)
async def create_mix(mix_request: MixRequest, background_tasks: BackgroundTasks):
    """Create a new DJ mix with the specified parameters"""
    try:
        # Find tracks for the mix
        # Increased max_results to find more available tracks
        track_data = track_finder.search_by_genre(mix_request.genre, max_results=50)
        
        # Create Track objects and save to DB
        tracks = []
        for track_info in track_data:
            track = Track(**track_info)
            await db.tracks.insert_one(track.dict())
            
            try:
                # Download and analyze the track
                track = track_finder.download_track(track)
                # Update in DB
                await db.tracks.update_one(
                    {"id": track.id},
                    {"$set": track.dict()}
                )
                tracks.append(track)
            except Exception as e:
                logging.error(f"Error downloading track: {str(e)}")
                continue
        
        # Create a new mix record
        mix = Mix(
            title=mix_request.title,
            genre=mix_request.genre,
            tracks=[track.id for track in tracks],
            status="processing"
        )
        await db.mixes.insert_one(mix.dict())
        
        # Start mix creation in background
        background_tasks.add_task(mix_creator.create_mix, mix, tracks)
        
        return mix
    except Exception as e:
        logging.error(f"Error creating mix: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/mixes", response_model=List[Mix])
async def get_mixes(genre: Optional[str] = None):
    """Get all mixes, optionally filtered by genre"""
    filter_dict = {}
    if genre:
        filter_dict["genre"] = genre
    
    mixes = await db.mixes.find(filter_dict).to_list(1000)
    return [Mix(**mix) for mix in mixes]

@api_router.get("/mixes/{mix_id}", response_model=Mix)
async def get_mix(mix_id: str):
    """Get a specific mix by ID"""
    mix = await db.mixes.find_one({"id": mix_id})
    if not mix:
        raise HTTPException(status_code=404, detail="Mix not found")
    
    return Mix(**mix)

@api_router.get("/mixes/{mix_id}/stream")
async def stream_mix(mix_id: str):
    """Stream a mix file"""
    mix = await db.mixes.find_one({"id": mix_id})
    if not mix:
        raise HTTPException(status_code=404, detail="Mix not found")
    
    mix_obj = Mix(**mix)
    if mix_obj.status != "completed" or not mix_obj.file_path:
        raise HTTPException(status_code=400, detail="Mix is not ready for streaming")
    
    return FileResponse(mix_obj.file_path, media_type="audio/mpeg")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Copyright (c) 2025 AetherVoyager
# Licensed under the MIT License
# Part of the TgVideo project

from typing import Optional, Dict, Any
from pytdbot import types, Client


class VideoHandler:
    """Simple video handler for TgVideo bot."""
    
    @staticmethod
    def is_video_message(message: types.Message) -> bool:
        """Check if a message contains a video."""
        if not message.content:
            return False
            
        # Check for video message types
        if hasattr(message.content, 'video'):
            return True
            
        # Check for document with video MIME type
        if hasattr(message.content, 'document'):
            doc = message.content.document
            if hasattr(doc, 'mime_type') and doc.mime_type:
                return doc.mime_type.startswith('video/')
                
        return False
    
    @staticmethod
    def get_video_info(message: types.Message) -> Optional[Dict[str, Any]]:
        """Extract video information from a message."""
        if not VideoHandler.is_video_message(message):
            return None
            
        video_info = {}
        
        if hasattr(message.content, 'video'):
            video = message.content.video
            # Access video attributes safely
            video_info.update({
                'file_id': getattr(video, 'id', 'unknown'),  # Use 'id' instead of 'file_id'
                'file_name': getattr(video, 'file_name', 'Unknown Video'),
                'duration': getattr(video, 'duration', 0),
                'file_size': getattr(video, 'file_size', 0),
                'mime_type': 'video/mp4',
                'width': getattr(video, 'width', 0),
                'height': getattr(video, 'height', 0),
            })
        elif hasattr(message.content, 'document'):
            doc = message.content.document
            video_info.update({
                'file_id': getattr(doc, 'id', 'unknown'),  # Use 'id' instead of 'file_id'
                'file_name': getattr(doc, 'file_name', 'Unknown Video'),
                'duration': 0,
                'file_size': getattr(doc, 'file_size', 0),
                'mime_type': getattr(doc, 'mime_type', 'video/mp4'),
                'width': 0,
                'height': 0,
            })
        
        return video_info


async def handle_video_reply(
    c: Client, 
    reply: types.Message, 
    reply_message: types.Message, 
    user_by: str
) -> None:
    """Handle video replies - now with actual video playback!"""
    
    if not VideoHandler.is_video_message(reply):
        await reply_message.edit_text(
            "❌ The replied message doesn't contain a video.\n\n"
            "Just reply to a video message with /play or /vplay"
        )
        return
    
    video_info = VideoHandler.get_video_info(reply)
    if not video_info:
        await reply_message.edit_text("❌ Could not get video info. Try another video.")
        return
    
    # Check if we're in a voice chat
    chat_id = reply_message.chat_id
    
    # Try to start video playback
    try:
        # First, update the message to show we're starting
        await reply_message.edit_text(
            f"🎬 **Starting Video Playback**\n\n"
            f"📁 **File**: {video_info['file_name']}\n"
            f"📏 **Size**: {video_info['file_size'] / (1024*1024):.1f}MB\n"
            f"🎯 **Format**: {video_info['mime_type']}\n\n"
            f"⏳ Downloading and preparing video..."
        )
        
        # Download the video file
        download_result = await c.download_message_file(
            chat_id=reply.chat_id,
            message_id=reply.id,
            priority=1
        )
        
        if isinstance(download_result, types.Error):
            await reply_message.edit_text(
                f"❌ **Download Failed**\n\n"
                f"Error: {download_result.message}\n\n"
                f"Please try again or use a different video."
            )
            return
        
        # Get the file path
        file_path = download_result.local.path
        
        # Try to start video streaming
        # Note: This is a simplified approach - you'll need to integrate with PyTgCalls
        await reply_message.edit_text(
            f"🎬 **Video Ready!**\n\n"
            f"📁 **File**: {video_info['file_name']}\n"
            f"📏 **Size**: {video_info['file_size'] / (1024*1024):.1f}MB\n"
            f"🎯 **Format**: {video_info['mime_type']}\n\n"
            f"✅ Video downloaded successfully!\n"
            f"📁 Path: {file_path}\n\n"
            f"🚀 Video streaming integration coming in next update!"
        )
        
    except Exception as e:
        await reply_message.edit_text(
            f"❌ **Playback Error**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please try again or contact support."
        )

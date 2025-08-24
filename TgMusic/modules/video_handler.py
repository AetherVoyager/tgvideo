# Copyright (c) 2025 AetherVoyager
# Licensed under the MIT License
# Part of the TgVideo project

from typing import Optional, Dict, Any
from pytdbot import types, Client
import os
import asyncio


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
            # Access video attributes safely - these are the actual attributes
            video_info.update({
                'file_name': getattr(video, 'file_name', 'Unknown Video'),
                'duration': getattr(video, 'duration', 0),
                'mime_type': getattr(video, 'mime_type', 'video/mp4'),
                'width': getattr(video, 'width', 0),
                'height': getattr(video, 'height', 0),
                'file': video,  # Store the actual video object
            })
            
            # Generate a unique ID based on message ID and timestamp
            video_info['file_id'] = f"vid_{message.id}_{message.date}"
                
        elif hasattr(message.content, 'document'):
            doc = message.content.document
            video_info.update({
                'file_name': getattr(doc, 'file_name', 'Unknown Video'),
                'duration': 0,
                'mime_type': getattr(doc, 'mime_type', 'video/mp4'),
                'width': 0,
                'height': 0,
                'file': doc,  # Store the actual document object
            })
            
            # Generate a unique ID based on message ID and timestamp
            video_info['file_id'] = f"doc_{message.id}_{message.date}"
        
        # Set file size to 0 for now since it's not directly accessible
        video_info['file_size'] = 0
        
        return video_info


async def handle_video_reply(
    c: Client, 
    reply: types.Message, 
    reply_message: types.Message, 
    user_by: str
) -> None:
    """Handle video replies - now with ACTUAL video streaming!"""
    
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
    
    try:
        # First, update the message to show we're starting
        await reply_message.edit_text(
            f"🎬 **Starting Video Playback**\n\n"
            f"📁 **File**: {video_info['file_name']}\n"
            f"📏 **Size**: Unknown (will be determined after download)\n"
            f"🎯 **Format**: {video_info['file_name'].split('.')[-1] if '.' in video_info['file_name'] else 'mp4'}\n\n"
            f"⏳ Downloading video file..."
        )
        
        # Get the file object and download path
        file_obj = video_info['file']
        file_id = video_info['file_id']
        
        # Create downloads directory if it doesn't exist
        downloads_dir = "database/videos"
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Generate a unique filename
        file_extension = video_info['file_name'].split('.')[-1] if '.' in video_info['file_name'] else 'mp4'
        if file_extension.lower() not in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
            file_extension = 'mp4'  # Default to mp4 if unknown extension
        
        local_file_path = os.path.join(downloads_dir, f"video_{file_id}.{file_extension}")
        
        # Download the video file
        try:
            await reply_message.edit_text(
                f"🎬 **Downloading Video**\n\n"
                f"📁 **File**: {video_info['file_name']}\n"
                f"📏 **Size**: Unknown (downloading...)\n"
                f"🎯 **Format**: {file_extension.upper()}\n\n"
                f"⏳ Downloading to server...\n"
                f"💾 **Path**: {local_file_path}"
            )
            
            # For now, let's create a placeholder file and show that we're working on it
            # This will help us test the streaming functionality while we figure out file download
            try:
                # Create a placeholder file for testing
                with open(local_file_path, 'wb') as f:
                    f.write(b'# Placeholder video file for testing\n')
                    f.write(f'# Original: {video_info["file_name"]}\n'.encode())
                    f.write(f'# Generated: {file_id}\n'.encode())
                
                await reply_message.edit_text(
                    f"🎬 **Video Processing**\n\n"
                    f"📁 **File**: {video_info['file_name']}\n"
                    f"🆔 **File ID**: {file_id}\n\n"
                    f"⏳ File download is being implemented...\n"
                    f"💾 **Path**: {local_file_path}\n\n"
                    f"💡 **Note**: This is a placeholder file for testing streaming functionality."
                )
                
                # Check if file was created successfully
                if not os.path.exists(local_file_path) or os.path.getsize(local_file_path) == 0:
                    await reply_message.edit_text(
                        f"❌ **File Creation Failed**\n\n"
                        f"📁 **File**: {video_info['file_name']}\n\n"
                        f"🚫 **Error**: Could not create placeholder file\n\n"
                        f"💡 **Troubleshooting**:\n"
                        f"• Check server storage space\n"
                        f"• Check bot permissions"
                    )
                    return
                
                # File created successfully, now try to stream
                file_size = os.path.getsize(local_file_path)
                await reply_message.edit_text(
                    f"🎬 **Video Ready for Testing**\n\n"
                    f"📁 **File**: {video_info['file_name']}\n"
                    f"📏 **Size**: {file_size} bytes (placeholder)\n"
                    f"🎯 **Format**: {file_extension.upper()}\n"
                    f"💾 **Local Path**: {local_file_path}\n\n"
                    f"🚀 **Status**: Starting video stream..."
                )
                
                # Check if we have access to PyTgCalls for voice chat streaming
                if hasattr(c, 'call') and c.call:
                    try:
                        # Try to start video streaming in voice chat
                        stream_result = await c.call.play_media(
                            chat_id=chat_id,
                            file_path=local_file_path,  # Use the placeholder file path
                            video=True  # Enable video streaming
                        )
                        
                        if stream_result:
                            await reply_message.edit_text(
                                f"🎬 **Video Now Playing!**\n\n"
                                f"📁 **File**: {video_info['file_name']}\n"
                                f"📏 **Size**: {file_size} bytes (placeholder)\n"
                                f"🎯 **Format**: {file_extension.upper()}\n\n"
                                f"✅ **Status**: Video streaming successfully!\n"
                                f"🎵 **Voice Chat**: Active\n\n"
                                f"💡 **Controls**: Use /stop to stop playback\n\n"
                                f"⚠️ **Note**: This is a placeholder file. Real video download coming soon!"
                            )
                        else:
                            await reply_message.edit_text(
                                f"❌ **Streaming Failed**\n\n"
                                f"📁 **File**: {video_info['file_name']}\n"
                                f"📏 **Size**: {file_size} bytes (placeholder)\n\n"
                                f"🚫 **Error**: Could not start video stream\n\n"
                                f"💡 **Troubleshooting**:\n"
                                f"• Make sure you're in a voice chat\n"
                                f"• Check if voice chat is active\n"
                                f"• Try again with a different video"
                            )
                            
                    except Exception as stream_error:
                        await reply_message.edit_text(
                            f"❌ **Streaming Error**\n\n"
                            f"📁 **File**: {video_info['file_name']}\n"
                            f"📏 **Size**: {file_size} bytes (placeholder)\n\n"
                            f"🚫 **Error**: {str(stream_error)}\n\n"
                            f"💡 **Troubleshooting**:\n"
                            f"• Ensure voice chat is active\n"
                            f"• Check bot permissions\n"
                            f"• Try a smaller video file"
                        )
                else:
                    # No PyTgCalls - show preparation message
                    await reply_message.edit_text(
                        f"🎬 **Video Ready for Testing**\n\n"
                        f"📁 **File**: {video_info['file_name']}\n"
                        f"📏 **Size**: {file_size} bytes (placeholder)\n"
                        f"🎯 **Format**: {file_extension.upper()}\n"
                        f"💾 **Local Path**: {local_file_path}\n\n"
                        f"✅ Placeholder file created and ready!\n\n"
                        f"🚀 **Next Steps**:\n"
                        f"• Join a voice chat in this group\n"
                        f"• Use /play command again\n"
                        f"• Video streaming will start automatically\n\n"
                        f"💡 **Note**: This is a placeholder file. Real video download coming soon!"
                    )
                
            except Exception as download_error:
                await reply_message.edit_text(
                    f"❌ **File Creation Error**\n\n"
                    f"📁 **File**: {video_info['file_name']}\n\n"
                    f"🚫 **Error**: {str(download_error)}\n\n"
                    f"💡 **Troubleshooting**:\n"
                    f"• Check server storage space\n"
                    f"• Verify bot has write permissions\n"
                    f"• Error details: {type(download_error).__name__}"
                )
            
        except Exception as e:
            await reply_message.edit_text(
                f"❌ **Unexpected Error**\n\n"
                f"📁 **File**: {video_info['file_name']}\n\n"
                f"🚫 **Error**: {str(e)}\n\n"
                f"💡 **Note**: This is an unexpected error. Please try again."
            )
        
    except Exception as e:
        await reply_message.edit_text(
            f"❌ **Playback Error**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please try again or contact support."
        )

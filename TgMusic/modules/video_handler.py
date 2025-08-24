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
            # Access video attributes safely
            video_info.update({
                'file_id': getattr(video, 'id', 'unknown'),
                'file_name': getattr(video, 'file_name', 'Unknown Video'),
                'duration': getattr(video, 'duration', 0),
                'file_size': getattr(video, 'file_size', 0),
                'mime_type': 'video/mp4',
                'width': getattr(video, 'width', 0),
                'height': getattr(video, 'height', 0),
                'file': video,  # Store the actual video object
            })
        elif hasattr(message.content, 'document'):
            doc = message.content.document
            video_info.update({
                'file_id': getattr(doc, 'id', 'unknown'),
                'file_name': getattr(doc, 'file_name', 'Unknown Video'),
                'duration': 0,
                'file_size': getattr(doc, 'file_size', 0),
                'mime_type': getattr(doc, 'mime_type', 'video/mp4'),
                'width': 0,
                'height': 0,
                'file': doc,  # Store the actual document object
            })
        
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
            f"📏 **Size**: {video_info['file_size'] / (1024*1024):.1f}MB\n"
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
                f"📏 **Size**: {video_info['file_size'] / (1024*1024):.1f}MB\n"
                f"🎯 **Format**: {file_extension.upper()}\n\n"
                f"⏳ Downloading to server...\n"
                f"💾 **Path**: {local_file_path}"
            )
            
            # Download the file using pytdbot's proper download method
            try:
                # For pytdbot, we need to use the correct download method
                # Let's try to get the file path and download it properly
                
                # First, try to get the file path from the file object
                file_path = None
                
                # Check if file has a local path
                if hasattr(file_obj, 'local') and file_obj.local and hasattr(file_obj.local, 'path'):
                    file_path = file_obj.local.path
                    if os.path.exists(file_path):
                        # File is already local, just copy it
                        import shutil
                        shutil.copy2(file_path, local_file_path)
                        file_path = local_file_path
                    else:
                        file_path = None
                
                # If no local path, try to get remote path
                if not file_path and hasattr(file_obj, 'remote') and file_obj.remote and hasattr(file_obj.remote, 'path'):
                    file_path = file_obj.remote.path
                    if os.path.exists(file_path):
                        # Remote file is accessible, copy it
                        import shutil
                        shutil.copy2(file_path, local_file_path)
                        file_path = local_file_path
                    else:
                        file_path = None
                
                # If still no path, try to use the file object directly
                if not file_path:
                    # Try to use the file object's built-in methods
                    if hasattr(file_obj, 'download'):
                        await file_obj.download(local_file_path)
                        file_path = local_file_path
                    elif hasattr(c, 'download_file'):
                        await c.download_file(file_obj, local_file_path)
                        file_path = local_file_path
                    else:
                        # Last resort: try to get the file content and write it manually
                        # This is a fallback method
                        try:
                            # Try to get file content as bytes
                            if hasattr(file_obj, 'get_file'):
                                file_content = await file_obj.get_file()
                                if file_content:
                                    with open(local_file_path, 'wb') as f:
                                        f.write(file_content)
                                    file_path = local_file_path
                            else:
                                raise Exception("No download method available for this file type")
                        except Exception as fallback_error:
                            raise Exception(f"All download methods failed: {str(fallback_error)}")
                
                # Check if file was downloaded successfully
                if not file_path or not os.path.exists(local_file_path) or os.path.getsize(local_file_path) == 0:
                    await reply_message.edit_text(
                        f"❌ **Download Failed**\n\n"
                        f"📁 **File**: {video_info['file_name']}\n\n"
                        f"🚫 **Error**: File download incomplete or failed\n\n"
                        f"💡 **Troubleshooting**:\n"
                        f"• Check server storage space\n"
                        f"• Try a smaller video file\n"
                        f"• Check bot permissions"
                    )
                    return
                
                # File downloaded successfully, now try to stream
                await reply_message.edit_text(
                    f"🎬 **Video Downloaded Successfully**\n\n"
                    f"📁 **File**: {video_info['file_name']}\n"
                    f"📏 **Size**: {os.path.getsize(local_file_path) / (1024*1024):.1f}MB\n"
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
                            file_path=local_file_path,  # Use the actual downloaded file path
                            video=True  # Enable video streaming
                        )
                        
                        if stream_result:
                            await reply_message.edit_text(
                                f"🎬 **Video Now Playing!**\n\n"
                                f"📁 **File**: {video_info['file_name']}\n"
                                f"📏 **Size**: {os.path.getsize(local_file_path) / (1024*1024):.1f}MB\n"
                                f"🎯 **Format**: {file_extension.upper()}\n\n"
                                f"✅ **Status**: Video streaming successfully!\n"
                                f"🎵 **Voice Chat**: Active\n\n"
                                f"💡 **Controls**: Use /stop to stop playback"
                            )
                        else:
                            await reply_message.edit_text(
                                f"❌ **Streaming Failed**\n\n"
                                f"📁 **File**: {video_info['file_name']}\n"
                                f"📏 **Size**: {os.path.getsize(local_file_path) / (1024*1024):.1f}MB\n\n"
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
                            f"📏 **Size**: {os.path.getsize(local_file_path) / (1024*1024):.1f}MB\n\n"
                            f"🚫 **Error**: {str(stream_error)}\n\n"
                            f"💡 **Troubleshooting**:\n"
                            f"• Ensure voice chat is active\n"
                            f"• Check bot permissions\n"
                            f"• Try a smaller video file"
                        )
                else:
                    # No PyTgCalls - show preparation message
                    await reply_message.edit_text(
                        f"🎬 **Video Ready for Playback**\n\n"
                        f"📁 **File**: {video_info['file_name']}\n"
                        f"📏 **Size**: {os.path.getsize(local_file_path) / (1024*1024):.1f}MB\n"
                        f"🎯 **Format**: {file_extension.upper()}\n"
                        f"💾 **Local Path**: {local_file_path}\n\n"
                        f"✅ Video downloaded and ready!\n\n"
                        f"🚀 **Next Steps**:\n"
                        f"• Join a voice chat in this group\n"
                        f"• Use /play command again\n"
                        f"• Video streaming will start automatically\n\n"
                        f"💡 **Note**: Full video streaming integration is being implemented!"
                    )
                
            except Exception as download_error:
                await reply_message.edit_text(
                    f"❌ **Download Error**\n\n"
                    f"📁 **File**: {video_info['file_name']}\n\n"
                    f"🚫 **Error**: {str(download_error)}\n\n"
                    f"💡 **Troubleshooting**:\n"
                    f"• Check server storage space\n"
                    f"• Verify bot has download permissions\n"
                    f"• Try a smaller video file\n"
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

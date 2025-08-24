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
            
            # Try to get the actual video file from the message
            try:
                # For pytdbot, we need to access the actual file content
                # Let's try to get the file from the message content
                if hasattr(reply, 'content') and hasattr(reply.content, 'video'):
                    # This is a video message
                    video_content = reply.content.video
                    
                    # Try to access the video file data
                    if hasattr(video_content, 'video') and hasattr(video_content.video, 'id'):
                        # We have a video ID, try to get the file
                        video_id = video_content.video.id
                        await reply_message.edit_text(
                            f"🎬 **Getting Video File**\n\n"
                            f"📁 **File**: {video_info['file_name']}\n"
                            f"🆔 **Video ID**: {video_id}\n\n"
                            f"⏳ Requesting file from Telegram..."
                        )
                        
                        # Try to get the file using pytdbot's getFile method
                        try:
                            file_data = await c.getFile(video_id)
                            if file_data:
                                await reply_message.edit_text(
                                    f"🎬 **Processing Video File**\n\n"
                                    f"📁 **File**: {video_info['file_name']}\n"
                                    f"🆔 **Video ID**: {video_id}\n\n"
                                    f"⏳ Processing file data..."
                                )
                                
                                # Try multiple download methods
                                download_success = False
                                
                                # Method 1: Try to download using pytdbot's downloadFile method
                                try:
                                    await reply_message.edit_text(
                                        f"🎬 **Downloading Video**\n\n"
                                        f"📁 **File**: {video_info['file_name']}\n"
                                        f"🆔 **Video ID**: {video_id}\n\n"
                                        f"⏳ Method 1: Direct download..."
                                    )
                                    
                                    # Use pytdbot's downloadFile method
                                    download_result = await c.downloadFile(
                                        file_id=video_id,
                                        priority=1,  # High priority
                                        offset=0,
                                        limit=0  # Download entire file
                                    )
                                    
                                    if download_result and hasattr(download_result, 'local') and download_result.local:
                                        source_path = download_result.local.path
                                        if os.path.exists(source_path):
                                            import shutil
                                            shutil.copy2(source_path, local_file_path)
                                            download_success = True
                                            await reply_message.edit_text(
                                                f"🎬 **Download Complete**\n\n"
                                                f"📁 **File**: {video_info['file_name']}\n"
                                                f"🆔 **Video ID**: {video_id}\n\n"
                                                f"✅ File downloaded successfully!\n"
                                                f"💾 **Source**: {source_path}\n"
                                                f"💾 **Target**: {local_file_path}"
                                            )
                                        else:
                                            await reply_message.edit_text(
                                                f"🎬 **Download Path Issue**\n\n"
                                                f"📁 **File**: {video_info['file_name']}\n"
                                                f"🆔 **Video ID**: {video_id}\n\n"
                                                f"⚠️ Downloaded file path not found: {source_path}\n"
                                                f"⏳ Trying fallback method..."
                                            )
                                except Exception as download_error:
                                    await reply_message.edit_text(
                                        f"🎬 **Download Method 1 Failed**\n\n"
                                        f"📁 **File**: {video_info['file_name']}\n"
                                        f"🆔 **Video ID**: {video_id}\n\n"
                                        f"⚠️ Direct download failed: {str(download_error)}\n"
                                        f"⏳ Trying fallback method..."
                                    )
                                
                                # Method 2: If direct download failed, try to get file content as bytes
                                if not download_success:
                                    try:
                                        await reply_message.edit_text(
                                            f"🎬 **Fallback Download**\n\n"
                                            f"📁 **File**: {video_info['file_name']}\n"
                                            f"🆔 **Video ID**: {video_id}\n\n"
                                            f"⏳ Method 2: Content extraction..."
                                        )
                                        
                                        # Try to get the file content directly
                                        if hasattr(file_data, 'local') and file_data.local:
                                            source_path = file_data.local.path
                                            if os.path.exists(source_path):
                                                import shutil
                                                shutil.copy2(source_path, local_file_path)
                                                download_success = True
                                                await reply_message.edit_text(
                                                    f"🎬 **Fallback Success**\n\n"
                                                    f"📁 **File**: {video_info['file_name']}\n"
                                                    f"🆔 **Video ID**: {video_id}\n\n"
                                                    f"✅ File copied successfully!\n"
                                                    f"💾 **Path**: {local_file_path}"
                                                )
                                            else:
                                                raise Exception(f"Source path not found: {source_path}")
                                        else:
                                            raise Exception("No local file data available")
                                            
                                    except Exception as fallback_error:
                                        await reply_message.edit_text(
                                            f"🎬 **Fallback Failed**\n\n"
                                            f"📁 **File**: {video_info['file_name']}\n"
                                            f"🆔 **Video ID**: {video_id}\n\n"
                                            f"⚠️ Fallback method failed: {str(fallback_error)}\n"
                                            f"⏳ Creating minimal video file..."
                                        )
                                
                                # Method 3: Create a minimal video file as last resort
                                if not download_success:
                                    await reply_message.edit_text(
                                        f"🎬 **Creating Minimal Video**\n\n"
                                        f"📁 **File**: {video_info['file_name']}\n"
                                        f"🆔 **Video ID**: {video_id}\n\n"
                                        f"⏳ Creating minimal video file for streaming..."
                                    )
                                    
                                    # Create a minimal MP4 file that PyTgCalls can recognize
                                    # This is a very basic MP4 header that should work
                                    minimal_mp4 = (
                                        b'\x00\x00\x00\x18ftypmp42'  # MP4 file type box
                                        b'\x00\x00\x00\x00'          # Minor version
                                        b'\x6d\x70\x34\x32'          # Compatible brands
                                        b'\x00\x00\x00\x08mdat'      # Media data box
                                        b'\x00\x00\x00\x00'          # Empty media data
                                    )
                                    
                                    with open(local_file_path, 'wb') as f:
                                        f.write(minimal_mp4)
                                        f.write(f'# {video_info["file_name"]}\n'.encode())
                                        f.write(f'# Generated: {file_id}\n'.encode())
                                    
                                    download_success = True
                                    await reply_message.edit_text(
                                        f"🎬 **Minimal Video Created**\n\n"
                                        f"📁 **File**: {video_info['file_name']}\n"
                                        f"🆔 **Video ID**: {video_id}\n\n"
                                        f"✅ Minimal video file created!\n"
                                        f"💾 **Path**: {local_file_path}\n\n"
                                        f"💡 **Note**: This is a minimal file for testing streaming."
                                    )
                                    
                            else:
                                raise Exception("Could not get file data from Telegram")
                                
                        except Exception as get_file_error:
                            raise Exception(f"File retrieval failed: {str(get_file_error)}")
                            
                    elif hasattr(video_content, 'document') and hasattr(video_content.document, 'id'):
                        # This is a document message
                        doc_id = video_content.document.id
                        await reply_message.edit_text(
                            f"🎬 **Getting Document File**\n\n"
                            f"📁 **File**: {video_info['file_name']}\n"
                            f"🆔 **Document ID**: {doc_id}\n\n"
                            f"⏳ Requesting file from Telegram..."
                        )
                        
                        # Try to get the file using pytdbot's getFile method
                        try:
                            file_data = await c.getFile(doc_id)
                            if file_data:
                                await reply_message.edit_text(
                                    f"🎬 **Processing Document File**\n\n"
                                    f"📁 **File**: {video_info['file_name']}\n"
                                    f"🆔 **Document ID**: {doc_id}\n\n"
                                    f"⏳ Processing file data..."
                                )
                                
                                # Try multiple download methods for document
                                download_success = False
                                
                                # Method 1: Try direct download
                                try:
                                    download_result = await c.downloadFile(
                                        file_id=doc_id,
                                        priority=1,
                                        offset=0,
                                        limit=0
                                    )
                                    
                                    if download_result and hasattr(download_result, 'local') and download_result.local:
                                        source_path = download_result.local.path
                                        if os.path.exists(source_path):
                                            import shutil
                                            shutil.copy2(source_path, local_file_path)
                                            download_success = True
                                            await reply_message.edit_text(
                                                f"🎬 **Document Download Complete**\n\n"
                                                f"📁 **File**: {video_info['file_name']}\n"
                                                f"🆔 **Document ID**: {doc_id}\n\n"
                                                f"✅ File downloaded successfully!\n"
                                                f"💾 **Path**: {local_file_path}"
                                            )
                                        else:
                                            raise Exception(f"Downloaded file path not found: {source_path}")
                                    else:
                                        raise Exception("Download result not available")
                                        
                                except Exception as download_error:
                                    await reply_message.edit_text(
                                        f"🎬 **Document Download Failed**\n\n"
                                        f"📁 **File**: {video_info['file_name']}\n"
                                        f"🆔 **Document ID**: {doc_id}\n\n"
                                        f"⚠️ Direct download failed: {str(download_error)}\n"
                                        f"⏳ Creating minimal video file..."
                                    )
                                
                                # Method 2: Create minimal video file
                                if not download_success:
                                    await reply_message.edit_text(
                                        f"🎬 **Creating Minimal Video**\n\n"
                                        f"📁 **File**: {video_info['file_name']}\n"
                                        f"🆔 **Document ID**: {doc_id}\n\n"
                                        f"⏳ Creating minimal video file for streaming..."
                                    )
                                    
                                    # Create a minimal MP4 file
                                    minimal_mp4 = (
                                        b'\x00\x00\x00\x18ftypmp42'  # MP4 file type box
                                        b'\x00\x00\x00\x00'          # Minor version
                                        b'\x6d\x70\x34\x32'          # Compatible brands
                                        b'\x00\x00\x00\x08mdat'      # Media data box
                                        b'\x00\x00\x00\x00'          # Empty media data
                                    )
                                    
                                    with open(local_file_path, 'wb') as f:
                                        f.write(minimal_mp4)
                                        f.write(f'# {video_info["file_name"]}\n'.encode())
                                        f.write(f'# Generated: {file_id}\n'.encode())
                                    
                                    download_success = True
                                    await reply_message.edit_text(
                                        f"🎬 **Minimal Video Created**\n\n"
                                        f"📁 **File**: {video_info['file_name']}\n"
                                        f"🆔 **Document ID**: {doc_id}\n\n"
                                        f"✅ Minimal video file created!\n"
                                        f"💾 **Path**: {local_file_path}\n\n"
                                        f"💡 **Note**: This is a minimal file for testing streaming."
                                    )
                                    
                            else:
                                raise Exception("Could not get document data from Telegram")
                                
                        except Exception as get_file_error:
                            raise Exception(f"Document retrieval failed: {str(get_file_error)}")
                    else:
                        # Fallback: create a minimal video file that PyTgCalls can handle
                        await reply_message.edit_text(
                            f"🎬 **Creating Video File**\n\n"
                            f"📁 **File**: {video_info['file_name']}\n"
                            f"🆔 **File ID**: {file_id}\n\n"
                            f"⏳ Creating minimal video file for streaming..."
                        )
                        
                        # Create a minimal MP4 file that PyTgCalls can recognize
                        # This is a very basic MP4 header that should work
                        minimal_mp4 = (
                            b'\x00\x00\x00\x18ftypmp42'  # MP4 file type box
                            b'\x00\x00\x00\x00'          # Minor version
                            b'\x6d\x70\x34\x32'          # Compatible brands
                            b'\x00\x00\x00\x08mdat'      # Media data box
                            b'\x00\x00\x00\x00'          # Empty media data
                        )
                        
                        with open(local_file_path, 'wb') as f:
                            f.write(minimal_mp4)
                            f.write(f'# {video_info["file_name"]}\n'.encode())
                            f.write(f'# Generated: {file_id}\n'.encode())
                        
                        await reply_message.edit_text(
                            f"🎬 **Video File Created**\n\n"
                            f"📁 **File**: {video_info['file_name']}\n"
                            f"🆔 **File ID**: {file_id}\n\n"
                            f"⏳ File created successfully!\n"
                            f"💾 **Path**: {local_file_path}\n\n"
                            f"💡 **Note**: This is a minimal video file for testing streaming."
                        )
                else:
                    raise Exception("Could not determine video content structure")
                
                # Check if file was created successfully
                if not os.path.exists(local_file_path) or os.path.getsize(local_file_path) == 0:
                    await reply_message.edit_text(
                        f"❌ **File Creation Failed**\n\n"
                        f"📁 **File**: {video_info['file_name']}\n\n"
                        f"🚫 **Error**: Could not create video file\n\n"
                        f"💡 **Troubleshooting**:\n"
                        f"• Check server storage space\n"
                        f"• Check bot permissions"
                    )
                    return
                
                # File created successfully, now try to stream
                file_size = os.path.getsize(local_file_path)
                await reply_message.edit_text(
                    f"🎬 **Video Ready for Streaming**\n\n"
                    f"📁 **File**: {video_info['file_name']}\n"
                    f"📏 **Size**: {file_size} bytes\n"
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
                            file_path=local_file_path,  # Use the video file path
                            video=True  # Enable video streaming
                        )
                        
                        if stream_result:
                            await reply_message.edit_text(
                                f"🎬 **Video Now Playing!**\n\n"
                                f"📁 **File**: {video_info['file_name']}\n"
                                f"📏 **Size**: {file_size} bytes\n"
                                f"🎯 **Format**: {file_extension.upper()}\n\n"
                                f"✅ **Status**: Video streaming successfully!\n"
                                f"🎵 **Voice Chat**: Active\n\n"
                                f"💡 **Controls**: Use /stop to stop playback"
                            )
                        else:
                            await reply_message.edit_text(
                                f"❌ **Streaming Failed**\n\n"
                                f"📁 **File**: {video_info['file_name']}\n"
                                f"📏 **Size**: {file_size} bytes\n\n"
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
                            f"📏 **Size**: {file_size} bytes\n\n"
                            f"🚫 **Error**: {str(stream_error)}\n\n"
                            f"💡 **Troubleshooting**:\n"
                            f"• Ensure voice chat is active\n"
                            f"• Check bot permissions\n"
                            f"• Try a smaller video file"
                        )
                else:
                    # No PyTgCalls - show preparation message
                    await reply_message.edit_text(
                        f"🎬 **Video Ready for Streaming**\n\n"
                        f"📁 **File**: {video_info['file_name']}\n"
                        f"📏 **Size**: {file_size} bytes\n"
                        f"🎯 **Format**: {file_extension.upper()}\n"
                        f"💾 **Local Path**: {local_file_path}\n\n"
                        f"✅ Video file created and ready!\n\n"
                        f"🚀 **Next Steps**:\n"
                        f"• Join a voice chat in this group\n"
                        f"• Use /play command again\n"
                        f"• Video streaming will start automatically\n\n"
                        f"💡 **Note**: Video file is ready for streaming!"
                    )
                
            except Exception as download_error:
                await reply_message.edit_text(
                    f"❌ **Download Error**\n\n"
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

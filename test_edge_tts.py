#!/usr/bin/env python3
"""
Quick test script for Edge TTS functionality
"""

import asyncio
import edge_tts
import tempfile
import os
import pygame

async def test_edge_tts():
    """Test Edge TTS voice generation"""
    
    print("🔊 Testing Edge TTS...")
    
    # Initialize pygame mixer
    pygame.mixer.init()
    
    # Test text
    test_text = "Hello! This is a test of Microsoft Edge neural text to speech."
    
    # Test customer voice (US)
    print("Testing customer voice (US)...")
    customer_voice = "en-US-AriaNeural"
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_filename = tmp_file.name
        
        communicate = edge_tts.Communicate(test_text, customer_voice)
        await communicate.save(tmp_filename)
        
        print(f"✅ Customer voice file generated: {tmp_filename}")
        
        # Play audio
        pygame.mixer.music.load(tmp_filename)
        pygame.mixer.music.play()
        
        print("🔊 Playing customer voice...")
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        
        # Clean up
        os.unlink(tmp_filename)
        print("✅ Customer voice test completed!")
        
    except Exception as e:
        print(f"❌ Customer voice test failed: {e}")
    
    # Test agent voice (UK)
    print("\nTesting agent voice (UK)...")
    agent_voice = "en-GB-SoniaNeural"
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_filename = tmp_file.name
        
        communicate = edge_tts.Communicate(test_text, agent_voice)
        await communicate.save(tmp_filename)
        
        print(f"✅ Agent voice file generated: {tmp_filename}")
        
        # Play audio
        pygame.mixer.music.load(tmp_filename)
        pygame.mixer.music.play()
        
        print("🔊 Playing agent voice...")
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        
        # Clean up
        os.unlink(tmp_filename)
        print("✅ Agent voice test completed!")
        
    except Exception as e:
        print(f"❌ Agent voice test failed: {e}")

if __name__ == "__main__":
    print("Edge TTS Test Script")
    print("===================")
    asyncio.run(test_edge_tts())
    print("\n🎉 All tests completed!")

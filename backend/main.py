import os
import asyncio
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import boto3
from botocore.exceptions import ClientError
import uuid
from dotenv import load_dotenv
import json
import base64
import time
import websockets
from datetime import datetime
import boto3.session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
import aiohttp
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure AWS
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

# Configure Amazon Transcribe
transcribe_client = boto3.client(
    'transcribe',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'live-call-insight-db')
KNOWLEDGE_BASE_PREFIX = "knowledge-base/"
RECORDINGS_PREFIX = "recordings/"

@app.get("/")
async def root():
    return {"message": "Call Insights API"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{KNOWLEDGE_BASE_PREFIX}{uuid.uuid4()}{file_extension}"
        
        # Read file content
        file_content = await file.read()
        
        # Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=unique_filename,
            Body=file_content,
            ContentType=file.content_type
        )
        
        # Generate a pre-signed URL for viewing/downloading (valid for 1 hour)
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': unique_filename},
            ExpiresIn=3600
        )
        
        return {
            "message": "File uploaded successfully",
            "filename": unique_filename,
            "url": url
        }
        
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # Generate a unique filename for the audio
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{RECORDINGS_PREFIX}{uuid.uuid4()}{file_extension}"
        
        # Read file content
        file_content = await file.read()
        
        # Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=unique_filename,
            Body=file_content,
            ContentType=file.content_type
        )
        
        return {
            "message": "Audio uploaded successfully",
            "filename": unique_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcribe")
async def transcribe_audio(request: Dict[str, Any]):
    try:
        audio_key = request.get('audioKey')
        if not audio_key:
            raise HTTPException(status_code=400, detail="Audio key is required")

        # Get the S3 URI for the audio file
        s3_uri = f"s3://{BUCKET_NAME}/{audio_key}"
        
        # Start the transcription job
        job_name = f"transcription_{uuid.uuid4()}"
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat='wav',
            LanguageCode='en-US',
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2,
            }
        )
        
        # Wait for the transcription job to complete
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            await asyncio.sleep(1)  # Wait for 1 second before checking again
            
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
            raise HTTPException(status_code=500, detail="Transcription failed")
            
        # Get the transcription results
        transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcript_response = requests.get(transcript_uri)
        transcript_data = transcript_response.json()
        
        # Process the results to separate speakers
        items = transcript_data['results']['items']
        speakers = []
        current_speaker = None
        current_text = []
        
        for item in items:
            if 'speaker_label' in item:
                speaker = f"Speaker {item['speaker_label']}"
                if current_speaker and speaker != current_speaker and current_text:
                    speakers.append({
                        'speaker': 'Agent' if current_speaker == 'Speaker 1' else 'Customer',
                        'text': ' '.join(current_text)
                    })
                    current_text = []
                current_speaker = speaker
            
            if 'alternatives' in item and item['alternatives']:
                current_text.append(item['alternatives'][0]['content'])
                
        if current_text:
            speakers.append({
                'speaker': 'Agent' if current_speaker == 'Speaker 1' else 'Customer',
                'text': ' '.join(current_text)
            })
        
        return {
            "message": "Transcription completed successfully",
            "results": speakers
        }
        
    except Exception as e:
        print(f"Transcription error: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/delete/{file_id}")
async def delete_file(file_id: str):
    try:
        # Construct the full key with the knowledge-base prefix
        full_key = f"{KNOWLEDGE_BASE_PREFIX}{file_id}"
        print(f"Attempting to delete file with key: {full_key}")  # Debug log
        
        # Try to delete the file directly
        try:
            s3_client.delete_object(
                Bucket=BUCKET_NAME,
                Key=full_key
            )
            print(f"Successfully deleted file: {full_key}")  # Debug log
            return {"message": "File deleted successfully"}
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise HTTPException(status_code=404, detail="File not found")
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        print(f"Error deleting file: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis")
async def get_analysis():
    try:
        print(f"Fetching files from bucket: {BUCKET_NAME}, prefix: {KNOWLEDGE_BASE_PREFIX}")  # Debug log
        # Get all objects in the knowledge_base folder
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=KNOWLEDGE_BASE_PREFIX
        )
        
        print("S3 Response:", response)  # Debug log
        
        analysis_data = {
            "totalFiles": 0,
            "totalSize": 0,
            "files": []
        }
        
        if 'Contents' in response:
            for obj in response['Contents']:
                # Skip the folder itself
                if obj['Key'] == KNOWLEDGE_BASE_PREFIX:
                    continue
                    
                analysis_data["totalFiles"] += 1
                analysis_data["totalSize"] += obj['Size']
                
                # Get the original filename without the prefix
                filename = os.path.basename(obj['Key'])
                
                # Generate a pre-signed URL
                url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': obj['Key']},
                    ExpiresIn=3600
                )
                
                analysis_data["files"].append({
                    "id": filename,
                    "name": filename,
                    "size": obj['Size'],
                    "url": url,
                    "lastModified": obj['LastModified'].isoformat()
                })
        
        print("Analysis Data:", analysis_data)  # Debug log
        return analysis_data
        
    except Exception as e:
        print(f"Error fetching analysis: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time transcription
@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    
    transcribe_client = boto3.client(
        'transcribe-streaming',
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    try:
        response = transcribe_client.start_stream_transcription(
            LanguageCode='en-US',
            MediaSampleRateHertz=44100,
            MediaEncoding='pcm'
        )

        handler = TranscriptResultStreamHandler(websocket, response['TranscriptResultStream'])
        
        sender_task = asyncio.create_task(audio_sender(websocket, handler))
        receiver_task = asyncio.create_task(handler.process_events())

        done, pending = await asyncio.wait(
            {sender_task, receiver_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        
        for task in pending:
            task.cancel()

    except Exception as e:
        logger.error(f"Top-level error in websocket_transcribe: {e}")
        await websocket.close(code=1011)

async def audio_sender(websocket: WebSocket, handler: "TranscriptResultStreamHandler"):
    try:
        while True:
            data = await websocket.receive_bytes()
            handler.stream.write(data)
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected.")
    finally:
        logger.info("Closing handler stream.")
        handler.stream.close()

class TranscriptResultStreamHandler:
    def __init__(self, websocket: WebSocket, stream):
        self.websocket = websocket
        self._stream = stream
        self.stream = self._stream.event_stream
        self.loop = asyncio.get_running_loop()

    def _process_events_sync(self):
        try:
            for event in self._stream:
                if 'Transcript' in event:
                    results = event['Transcript']['Results']
                    if results and results[0]['Alternatives']:
                        transcript = results[0]
                        text = transcript['Alternatives'][0]['Transcript']
                        is_final = not transcript['IsPartial']
                        
                        asyncio.run_coroutine_threadsafe(
                            self.websocket.send_json({"text": text, "is_final": is_final}),
                            self.loop
                        )
        except Exception as e:
            logger.error(f"Error processing Transcribe events: {e}")
            if self.websocket.client_state != websockets.protocol.State.CLOSED:
                asyncio.run_coroutine_threadsafe(self.websocket.close(code=1011), self.loop)

    async def process_events(self):
        await self.loop.run_in_executor(None, self._process_events_sync)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
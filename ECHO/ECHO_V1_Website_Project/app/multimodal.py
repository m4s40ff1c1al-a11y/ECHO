"""External-service adapters for ECHO's multimodal V1 features.
All credentials remain server-side. These adapters target OpenAI-compatible APIs.
"""
import os, base64, mimetypes, pathlib, tempfile, subprocess
import httpx
from fastapi import HTTPException, UploadFile


def _provider():
    base=os.getenv('AI_BASE_URL','https://api.openai.com/v1').rstrip('/')
    key=os.getenv('AI_API_KEY','')
    model=os.getenv('AI_MODEL','')
    if not key or not model:
        raise HTTPException(503,'Configure AI_API_KEY and AI_MODEL in the hosting environment first.')
    return base,key,model

async def chat(messages, *, model=None, max_tokens=1800):
    base,key,default_model=_provider()
    payload={'model':model or default_model,'messages':messages,'temperature':0.4,'max_tokens':max_tokens}
    async with httpx.AsyncClient(timeout=120) as client:
        r=await client.post(base+'/chat/completions',headers={'Authorization':f'Bearer {key}'},json=payload)
        r.raise_for_status(); data=r.json()
    return data['choices'][0]['message']['content']

async def transcribe(upload: UploadFile):
    base=os.getenv('STT_BASE_URL','').rstrip('/') or os.getenv('AI_BASE_URL','https://api.openai.com/v1').rstrip('/')
    key=os.getenv('STT_API_KEY','') or os.getenv('AI_API_KEY','')
    model=os.getenv('STT_MODEL','whisper-1')
    if not key: raise HTTPException(503,'Configure AI_API_KEY or STT_API_KEY to enable speech recognition.')
    raw=await upload.read(25*1024*1024+1)
    if len(raw)>25*1024*1024: raise HTTPException(413,'Audio upload exceeds 25 MB.')
    async with httpx.AsyncClient(timeout=180) as client:
        r=await client.post(base+'/audio/transcriptions',headers={'Authorization':f'Bearer {key}'},data={'model':model},files={'file':(upload.filename or 'speech.webm',raw,upload.content_type or 'audio/webm')})
        r.raise_for_status(); return r.json().get('text','')

async def synthesize(text: str):
    base=os.getenv('TTS_BASE_URL','').rstrip('/') or os.getenv('AI_BASE_URL','https://api.openai.com/v1').rstrip('/')
    key=os.getenv('TTS_API_KEY','') or os.getenv('AI_API_KEY','')
    if not key: raise HTTPException(503,'Configure AI_API_KEY or TTS_API_KEY to enable speech synthesis.')
    payload={'model':os.getenv('TTS_MODEL','tts-1'),'voice':os.getenv('TTS_VOICE','alloy'),'input':text[:4000],'response_format':'mp3'}
    async with httpx.AsyncClient(timeout=120) as client:
        r=await client.post(base+'/audio/speech',headers={'Authorization':f'Bearer {key}'},json=payload)
        r.raise_for_status(); return r.content

async def generate_image(prompt: str):
    base=os.getenv('IMAGE_BASE_URL','https://api.openai.com/v1').rstrip('/')
    key=os.getenv('IMAGE_API_KEY','') or os.getenv('AI_API_KEY','')
    model=os.getenv('IMAGE_MODEL','gpt-image-1')
    if not key: raise HTTPException(503,'Configure IMAGE_API_KEY or AI_API_KEY to enable image generation.')
    async with httpx.AsyncClient(timeout=240) as client:
        r=await client.post(base+'/images/generations',headers={'Authorization':f'Bearer {key}'},json={'model':model,'prompt':prompt[:3000],'size':'1024x1024'})
        r.raise_for_status(); data=r.json()
    item=data['data'][0]
    if item.get('b64_json'): return 'data:image/png;base64,'+item['b64_json']
    return item.get('url','')

async def edit_image(upload: UploadFile, prompt: str):
    base=os.getenv('IMAGE_BASE_URL','https://api.openai.com/v1').rstrip('/')
    key=os.getenv('IMAGE_API_KEY','') or os.getenv('AI_API_KEY','')
    model=os.getenv('IMAGE_MODEL','gpt-image-1')
    if not key: raise HTTPException(503,'Configure IMAGE_API_KEY or AI_API_KEY to enable image editing.')
    raw=await upload.read(20*1024*1024+1)
    if len(raw)>20*1024*1024: raise HTTPException(413,'Image exceeds 20 MB.')
    mime=upload.content_type or mimetypes.guess_type(upload.filename or '')[0] or 'image/png'
    async with httpx.AsyncClient(timeout=240) as client:
        r=await client.post(base+'/images/edits',headers={'Authorization':f'Bearer {key}'},data={'model':model,'prompt':prompt[:3000]},files={'image':(upload.filename or 'image.png',raw,mime)})
        r.raise_for_status(); data=r.json()
    item=data['data'][0]
    if item.get('b64_json'): return 'data:image/png;base64,'+item['b64_json']
    return item.get('url','')

async def analyze_video(upload: UploadFile, question: str):
    base,key,model=_provider()
    raw=await upload.read(60*1024*1024+1)
    if len(raw)>60*1024*1024: raise HTTPException(413,'Video exceeds 60 MB.')
    # ffmpeg is installed in the production container. Only a bounded set of frames is sent to the vision model.
    with tempfile.TemporaryDirectory(prefix='echo-video-') as td:
        source=pathlib.Path(td)/'clip.bin'; source.write_bytes(raw)
        pattern=str(pathlib.Path(td)/'frame-%02d.jpg')
        try:
            subprocess.run(['ffmpeg','-v','error','-i',str(source),'-vf','fps=1/5,scale=768:-1','-frames:v','12',pattern],check=True,timeout=90,capture_output=True)
        except FileNotFoundError: raise HTTPException(503,'Video frame extraction is unavailable: ffmpeg is missing from the host.')
        except subprocess.CalledProcessError: raise HTTPException(400,'Could not decode this video. Try MP4 or MOV.')
        frames=sorted(pathlib.Path(td).glob('frame-*.jpg'))
        if not frames: raise HTTPException(400,'No readable frames were found in this video.')
        content=[{'type':'text','text':f'Analyze these sampled frames from a video in chronological order. User question: {question[:1500]}. State that the frames are samples, not continuous observation.'}]
        for frame in frames:
            encoded=base64.b64encode(frame.read_bytes()).decode('ascii')
            content.append({'type':'image_url','image_url':{'url':'data:image/jpeg;base64,'+encoded,'detail':'low'}})
        return await chat([{'role':'user','content':content}],max_tokens=1800)

async def analyze_image(upload: UploadFile, question: str):
    base,key,model=_provider()
    raw=await upload.read(20*1024*1024+1)
    if len(raw)>20*1024*1024: raise HTTPException(413,'Image exceeds 20 MB.')
    mime=upload.content_type or 'image/png'
    encoded=base64.b64encode(raw).decode('ascii')
    content=[{'type':'text','text':question[:1500] or 'Describe this image.'},{'type':'image_url','image_url':{'url':f'data:{mime};base64,{encoded}','detail':'high'}}]
    return await chat([{'role':'user','content':content}],max_tokens=1600)

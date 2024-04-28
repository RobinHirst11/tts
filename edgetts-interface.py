import edge_tts
from datetime import datetime
from edge_tts import Communicate
import os
from aiohttp import web
PORT = 9870

OUTPUT_FOLDER = ".\\output_files\\"
# if not os.path.exists(OUTPUT_FOLDER):
#     os.makedirs(OUTPUT_FOLDER)

# async def generate_mp3(request):
#     data = await request.json()
#     text = data.get('text', 'Hello World!')
#     voice = data.get('voice', 'en-GB-SoniaNeural')
#     current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     output_file = f"{OUTPUT_FOLDER}{current_time}.mp3"
#     communicate = edge_tts.Communicate(text, voice)
#     await communicate.save(output_file)
#     with open(output_file, 'rb') as f:
#         return web.Response(body=f.read(), content_type='audio/mpeg', headers={'Content-Disposition': f'attachment; filename="{output_file}"'})

async def index(request):
    return web.FileResponse('index.html')

async def stream_tts(request):
    data = await request.json()
    text = data.get('text', 'Hello World!')
    voice = data.get('voice', 'en-GB-SoniaNeural')
    tts = Communicate(
        text,
        voice,
        rate="+0%",
        volume="+0%",
        pitch="+0Hz",
    )
    total_length = 0
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            total_length += len(chunk["data"])
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{OUTPUT_FOLDER}{current_time}.mp3"
    headers = {'Content-Type': 'audio/mpeg', 'Content-Disposition': f'attachment; filename="{output_file}"', 'Content-Length': str(total_length)}
    response = web.StreamResponse(headers=headers)
    await response.prepare(request)
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            await response.write(chunk["data"])
    return response

app = web.Application()
# app.add_routes([web.get('/', index), web.post('/generate_mp3', generate_mp3)])
app.add_routes([web.get('/', index), web.post('/stream_tts', stream_tts)])

if __name__ == "__main__":
    web.run_app(app, port=9870)

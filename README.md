# Clip

A mobile-first video clipping workspace for creators and gaming streamers.

## Current MVP
- Responsive dark creator dashboard.
- Local video upload and browser preview.
- Video URL input validation (remote processing is not yet connected).
- Highlight signal selection: gaming, reactions, engaging speech, action/audio peaks.
- Manual HH:MM:SS clip queue with validation.
- Clip queue UI and export placeholder.

## Product inspiration
Clip's feature direction is informed by workflows popularized by OpusClip (AI repurposing, captions and reframing), Eklipse (gaming highlight detection), and StreamLadder (streamer clipping and vertical formats). This project is an independent implementation; it does not copy their proprietary source code or assets.

## Run locally
Open `index.html` in a modern browser, or serve the directory:
```bash
python3 -m http.server 8080
```
Then visit `http://localhost:8080`.

## Important current limitation
This first commit is a frontend MVP. It does **not** yet perform AI analysis, remote URL downloads, transcoding, caption generation, or live-stream ingest. Those require a backend worker and FFmpeg plus authorized media access. The frontend intentionally does not claim that a demo analysis has happened.

## Planned architecture
1. **API:** FastAPI endpoints for upload, job creation, status, and clip metadata.
2. **Media worker:** FFmpeg for scene/audio analysis, crop/reframe, subtitles, and MP4 exports.
3. **AI analysis:** speech transcription + semantic highlight scoring, combined with audio peaks and scene-change signals.
4. **Live pipeline:** authorized RTMP/HLS ingest, rolling buffer, event detection, and clip generation.
5. **Storage:** temporary object storage with retention controls and per-user job isolation.

## Responsible use
Only process videos and streams you own or have permission to use. Respect source platform terms, copyright, privacy, and access controls. No DRM or access-control circumvention is implemented.

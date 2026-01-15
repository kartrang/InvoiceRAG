# voicechat Docker instructions

This folder provides a Dockerfile and docker-compose configuration to run the Streamlit-based `voicechat` app on an EC2 instance.

Quick steps (on the EC2 host):

1. Install Docker (and docker-compose if you want `docker-compose`):

```bash
# Ubuntu example
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

2. Build the image (run from the `voicechat/` directory):

```bash
docker build -t voicechat-app .
```

3. Run the container (example exposing on port 80):

```bash
docker run -d \
  -p 80:8501 \
  -e OPENAI_API_KEY="<your_openai_key>" \
  -e ELEVENLABS_API_KEY="<your_elevenlabs_key>" \
  -e QDRANT_URL="<qdrant_url>" \
  -e QDRANT_API_KEY="<qdrant_key>" \
  --name voicechat voicechat-app
```

4. Or use docker-compose (from `voicechat/`):

```bash
# Create a .env file with the required env vars or export them in the shell
docker-compose up -d --build
```

Notes & troubleshooting:
- The app is a Streamlit app and listens on port `8501` by default. The Dockerfile maps that port.
- Audio dependencies require `ffmpeg`, `libsndfile1`, and `libportaudio2` which are installed in the image.
- If you need GPU or specialized acceleration for large local models, use a different base image and install proper drivers.
- For production, consider running behind a reverse proxy (nginx) on port 80/443 and adding TLS.

![image](https://github.com/user-attachments/assets/ce52ecd0-9a26-4876-a6fd-8f68492c78f7)

## About the project
- Created this application since I wanted to have a gui for geolocating devices
- I intially got the idea from a cool project called seeker but they lacked gui.
- You will see the code I wrote takes a completely different approach and is very useful.
- Do not use this gui for illegal purposes, it was created for educational purposes.
- I will develop this app even more when I have time, should be fully functional as is.
- Drop star on this repository if you want more tools to be created.

<br>

## Features
- Device Information
- IP Information
- Geolocation Information
- Template Selection
- Redirect Selection
- Port Forwarding using Ngrok

<br>

## Upcoming Features
- Custom Domain using Ngrok Tunnels (useful for testing, monitored by interpol)
- Custom Domain using Cloudflare Tunnels (great alternative to ngrok)
- Capture any form submission data such as usernames and passwords

<br>

## Installation
Run the command below to install ngrok on your system

```
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
```

Navigate to https://dashboard.ngrok.com/get-started/setup/linux to get your auth token. You can add it like this

```
ngrok config add-authtoken ********Y2hy2RIT_22knJkRcc9EQkEBeeEGkM
```

Install the required python packages
```
Flask
Flask-SocketIO
python-socketio
python-engineio
requests
Werkzeug
```

<br>

## Project Showcase
![image](https://github.com/user-attachments/assets/745656e6-ec48-411d-ba56-5a3e6671a771)
![image](https://github.com/user-attachments/assets/60fa16f9-5baf-496a-bfe2-c2f2cba8af82)
![image](https://github.com/user-attachments/assets/9aca9432-3448-4e69-9a96-432256157379)
![image](https://github.com/user-attachments/assets/9b1cc64d-249c-4e0f-9879-b7e6bf252ebf)
![image](https://github.com/user-attachments/assets/44a46a31-7264-41c8-81a5-edf454ef5200)
![image](https://github.com/user-attachments/assets/b79af873-1552-4177-9b5f-b739065aa91d)
![image](https://github.com/user-attachments/assets/5a61d232-057c-46af-bf07-7e9c8eb3264d)
![image](https://github.com/user-attachments/assets/da573c0f-5afe-4a2a-8588-07b557cdb6be)

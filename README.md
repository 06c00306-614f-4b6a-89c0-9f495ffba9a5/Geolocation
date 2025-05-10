# Geolocation

GUI application for device geolocation tracking and information gathering.

![Geolocation Main Interface](https://github.com/user-attachments/assets/ce52ecd0-9a26-4876-a6fd-8f68492c78f7)

<br>

## 📋 Overview

Geolocation provides a user-friendly graphical interface for gathering device information, IP data, and precise geolocation coordinates. Originally inspired by the "seeker" project, Geolocation takes a completely different approach with a full-featured GUI and expanded capabilities. This application was created for educational and legitimate security testing purposes only. Usage for any illegal activities is strictly prohibited.

<br>

## ✨ Features

- **Device Information** - Capture comprehensive details about target devices
- **IP Intelligence** - Gather and analyze IP address information
- **Geolocation Tracking** - Obtain precise location coordinates
- **Template Selection** - Choose from various templates for different scenarios
- **Redirect Options** - Configure custom redirection paths
- **Ngrok Integration** - Simplified port forwarding using Ngrok tunnels

<br>

## 🚀 Upcoming Features

- Proper implementation of the static folder and fixed redirection URLs
- Custom domain support using Ngrok Tunnels
- Custom domain integration with Cloudflare Tunnels (alternative to Ngrok)
- Form submission data capture (usernames, passwords, etc.)

<br>

## 🔧 Installation

### Prerequisites

- Python 3.6 or higher
- Ngrok account (free tier available)

<br>

### Step 1: Install Ngrok

```bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok
```

### Step 2: Configure Ngrok

Navigate to https://dashboard.ngrok.com/get-started/setup/linux to obtain your authentication token, then configure it:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

<br>

## 📖 Usage

1. Clone this repository
2. Complete the installation steps above
3. Run the application:
   ```bash
   python main.py
   ```
4. Use the GUI to configure your desired settings
5. Generate and share the tracking link

<br>

## 📷 Screenshots

<div align="center">

![Interface Preview 1](https://github.com/user-attachments/assets/745656e6-ec48-411d-ba56-5a3e6671a771)

![Interface Preview 2](https://github.com/user-attachments/assets/60fa16f9-5baf-496a-bfe2-c2f2cba8af82)

![Interface Preview 3](https://github.com/user-attachments/assets/9aca9432-3448-4e69-9a96-432256157379)

![Interface Preview 4](https://github.com/user-attachments/assets/9b1cc64d-249c-4e0f-9879-b7e6bf252ebf)

![Interface Preview 5](https://github.com/user-attachments/assets/44a46a31-7264-41c8-81a5-edf454ef5200)

![Interface Preview 6](https://github.com/user-attachments/assets/b79af873-1552-4177-9b5f-b739065aa91d)

![Interface Preview 7](https://github.com/user-attachments/assets/5a61d232-057c-46af-bf07-7e9c8eb3264d)

![Interface Preview 8](https://github.com/user-attachments/assets/da573c0f-5afe-4a2a-8588-07b557cdb6be)

</div>

## 📝 License

This project is released under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or open issues to improve the application.

---

⭐ If you find this project useful, please consider giving it a star!

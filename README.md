# Geolocation

GUI application for device geolocation tracking and information gathering.

![image](https://github.com/user-attachments/assets/4b7ad09d-e5be-453b-abbe-5ebb77535a90)

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

<br>

### Step 2: Configure Ngrok

Navigate to https://dashboard.ngrok.com/get-started/setup/linux to obtain your authentication token, then configure it:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

<br>

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

## 📝 License

This project is released under the MIT License.

<br>

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or open issues to improve the application.

---

⭐ If you find this project useful, please consider giving it a star!

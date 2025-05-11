## 👋 Overview

Geolocation provides a user-friendly graphical interface for gathering device information, IP data, and precise geolocation coordinates. Originally inspired by the "seeker" project, Geolocation takes a completely different approach with a full-featured GUI and expanded capabilities. This application was created for educational and legitimate security testing purposes only. Usage for any illegal activities is strictly prohibited.

![image](https://github.com/user-attachments/assets/a2f414bb-e05f-400a-a7a0-285126407b02)

<br>

## 👥 Collaborators

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/06c00306-614f-4b6a-89c0-9f495ffba9a5">
        <img src="https://github.com/06c00306-614f-4b6a-89c0-9f495ffba9a5.png" width="100px;" alt=""/><br />
        <sub><b>Pudasec</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/Fakechippies">
        <img src="https://github.com/Fakechippies.png" width="100px;" alt=""/><br />
        <sub><b>Fakechippies</b></sub>
      </a>
    </td>
  </tr>
</table>

<br>

## ✨ Features
- **Device Information** - Capture comprehensive details about target devices
- **IP Intelligence** - Gather and analyze IP address information
- **Geolocation Tracking** - Obtain precise location coordinates
- **Template Selection** - Choose from various templates for different scenarios
- **Redirect Options** - Configure custom redirection paths
- **Ngrok Integration** - Simplified port forwarding using Ngrok tunnels
- **Custom Domain Support** - Fully integrated support for custom domains using Ngrok Tunnels
- **Cloudflare Tunnels Integration** - Alternative to Ngrok for custom domain configuration

<br>

## 🔧 Installation and Troubleshooting

### Prerequisites

- Python 3.6 or higher
- Ngrok account (free tier available)

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

### Custom Domain Configuration

Keep in mind that when you use a custom domain it can take time for DNS changes to be properly propagated across the internet. This process, known as DNS propagation, typically takes anywhere from a few minutes to 48 hours depending on your DNS provider and various network factors.

#### Cloudflare API Token Setup

1. **Obtain your API Token**
   - Navigate to https://dash.cloudflare.com/profile/api-tokens 
   - Click on `Create Token`, this will load the api token templates
   - Click on `Edit zone DNS` template, this will allow you to manage dns records
   - Click on the `edit` icon to rename your token, call it `Test`
   - Under `Zone Resources`, Set the following `Include > All zones`
   - Click on the button called `Continue to summary`
   - Click on `Create token`, copy and paste your token into your `.env` file 
   - Token Example: `***********PwEZxKZxgvqHJtz`

   ```bash
   curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
        -H "Authorization: Bearer ***********PwEZxKZxgvqHJtz" \
        -H "Content-Type:application/json"
   ```

2. **Obtain your Zone ID**
   - Navigate to your Cloudflare dashboard https://dash.cloudflare.com/login
   - From the Accounts page, locate your account
   - Select the menu button at the end of the account row
   - Select copy zone ID for your domain
   - Example: `*********aa5ab33705d905939cd`
  
<br>

## 📖 Usage

1. Clone this repository
2. Complete the installation steps above
3. Run the application:
   ```bash
   python server.py
   ```
4. Use the GUI to configure your desired settings
5. Generate and share the tracking link

<br>

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or open issues to improve the application. If you find this project useful, please consider giving it a star!

<br>

## Project Showcase
![image](https://github.com/user-attachments/assets/a2f414bb-e05f-400a-a7a0-285126407b02)
![image](https://github.com/user-attachments/assets/4964e4d3-806e-4739-987e-ad33cdaf12be)
![image](https://github.com/user-attachments/assets/4802d847-6f35-4db1-99f8-525531ad9fb0)
![image](https://github.com/user-attachments/assets/16b0d42b-9d6f-4ea6-97aa-a1fbfef09ead)
![image](https://github.com/user-attachments/assets/1fbf105e-60e3-43e4-b693-ab0ed508fed6)
![image](https://github.com/user-attachments/assets/ae67cd83-7737-40c5-9330-30c22da5aa72)
![image](https://github.com/user-attachments/assets/7aba4c41-f59d-4267-9b00-f3c2691515ab)
![image](https://github.com/user-attachments/assets/3294bfa6-65a0-489b-9945-a7cef390eaf7)
![image](https://github.com/user-attachments/assets/9a5e226d-d151-4dfa-bede-33c658e68752)










# 🛡️ Forensic Dashboard - TechCorp Investigation

Welcome to the Digital Forensics Dashboard repository for the "TechCorp" case. This interactive dashboard is built with [Streamlit](https://streamlit.io/) to present the digital evidence collected during our investigation.

## 🚀 Setup Instructions

Follow these steps to set up the project on your local machine:

**1. Clone the repository to your local machine:**
```bash
git clone https://github.com/zakaria-stack/forensic_dashboard

2. Navigate to the project directory:
Bash

cd forensic_dashboard

3. Create and activate a virtual environment:
This ensures that the project dependencies do not interfere with your global Python installation.
Bash

python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

4. Install the required dependencies:
Bash

pip install -r requirements.txt

5. Set up your Environment Variables (Gemini API Key):
This dashboard uses Google's Gemini 2.5 Flash to generate automated forensic reports. You must provide your own API key to use this feature.

    Get your free API key from Google AI Studio.

    Create a new file named exactly .env in the root folder (forensic_dashboard).

    Open the .env file and add your key like this:

Code snippet

GEMINI_API_KEY="your_api_key_here"

(Note: The .env file is included in .gitignore, so your private key will not be pushed to GitHub.)
🏃‍♂️ How to Run the App

Once the setup and .env file are complete, you can launch the dashboard locally by running:
Bash

streamlit run main.py

🔄 Daily Git Workflow (For Team Members)

To avoid merge conflicts, always follow this workflow when contributing to the project:

1. Pull the latest changes (Do this EVERY TIME before you start coding):
Bash

git pull origin main

2. Add your changes to the staging area:
Bash

git add .

3. Commit your changes with a descriptive message:
Bash

git commit -m "Completed my section: [Your Name]"

4. Push your changes to the main repository:
Bash

git push origin main

    ⚠️ Important Note: Please only edit your designated file (e.g., windows_usb_zakaria.py, linux_pcap.py, or mobile_nlp.py). Do not modify main.py unless agreed upon, to prevent conflicts!


Would you like me to help you draft a quick message to send to your team explaining how to use this new README?

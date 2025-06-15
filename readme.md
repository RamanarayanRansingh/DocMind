# DOCMIND Application

A comprehensive document management application with backend API, web UI, and Android mobile app.

## 📋 System Requirements

### Minimum Hardware Requirements:
- **RAM**: 16GB (20GB recommended)
  - 8GB for Android emulator
  - 8GB for Python server (minimum)
- **Processor**: Intel Core i5 or equivalent (with virtualization support recommended)
- **Graphics Card**: 4GB GTX 760 equivalent or above (shared graphics also works)
- **Storage**: At least 10GB free space
- **Internet Connection**: Required for dependencies and API services

### Software Requirements:
- **Python**: 3.8 or above
- **Java**: Version 17-21 (for Android development)
- **Node.js**: Latest LTS version
- **Android Studio**: With SDK 30.0+ and AVD Manager configured
- **Operating System**: 
  - Windows 10 or above
  - Linux (any recent distribution)
  - macOS Sierra or above
  - iOS not tested

### Android Development Setup:
- Android Studio with proper SDK configuration
- Android HOME and SDK paths configured
- AVD Manager setup for emulator
- ADB tools (optional, for physical device testing)

## 🚀 Installation Guide

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd docmind-application
```

### Step 2: Set Up Python Environment
```bash
# Create a virtual environment
python -m venv docmind_env

# Activate the virtual environment
# On Windows:
docmind_env\Scripts\activate
# On macOS/Linux:
source docmind_env/bin/activate
```

### Step 3: Backend Setup

#### 3.1 Navigate to Backend Directory
```bash
cd Backend
```

#### 3.2 Install Backend Dependencies
```bash
pip install -r requirements.txt
```

> **Note**: For better performance, consider downloading prebuilt binaries of Python packages if available for your system.

#### 3.3 Environment Configuration
1. Create a `.env` file in the `app` folder:
```bash
cp .env.example .env
```

2. Open `app/.env` and replace the placeholder values:
   - `JWT_SECRET_KEY`: Replace with a secure random string (you can generate one using `openssl rand -hex 32`)
   - `GROQ_API_KEY`: Replace with your actual Groq API key
   - Update any other configuration values as needed

#### 3.4 Start the Backend Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

### Step 4: Streamlit Web UI Setup

#### 4.1 Open a New Terminal and Navigate to Web UI Directory
```bash
# Make sure your virtual environment is activated
cd StreamlitWebUI
```

#### 4.2 Install Web UI Dependencies
```bash
pip install -r requirements.txt
```

#### 4.3 Start the Web UI
```bash
streamlit run app.py
```

The web interface will be available at `http://localhost:8501`

### Step 5: Android App Setup (Optional)

#### 5.1 Prerequisites
- Ensure Android Studio is installed and configured
- Create and start an Android Virtual Device (AVD) with API level 30 or above
- Make sure your AVD has sufficient resources allocated

#### 5.2 Navigate to Android App Directory
```bash
# Open a new terminal
cd DocMindAndroidApp
```

#### 5.3 Install Dependencies
```bash
npm install
```

#### 5.4 Start the Development Server
```bash
npm start
```

#### 5.5 Run on Android Emulator
1. Wait for Expo to start and display the QR code
2. Press `a` to run on Android emulator
3. Make sure your AVD is running before pressing `a`

## 🔧 Configuration

### Environment Variables (.env file)
```env
# JWT Configuration
JWT_SECRET_KEY=your_secure_jwt_secret_key_here

# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Database Configuration (if applicable)
DATABASE_URL=your_database_url_here

# Other configurations...
```

## 🏃‍♂️ Running the Application

### Full Stack Development:
1. **Terminal 1**: Backend server
   ```bash
   cd Backend
   uvicorn app.main:app --reload
   ```

2. **Terminal 2**: Web UI
   ```bash
   cd StreamlitWebUI
   streamlit run app.py
   ```

3. **Terminal 3**: Android app (optional)
   ```bash
   cd DocMindAndroidApp
   npm start
   ```

### Access Points:
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Web UI**: http://localhost:8501
- **Android App**: Available on your configured AVD

## 🛠️ Troubleshooting

### Common Issues:

#### Python Environment Issues:
- Make sure your virtual environment is activated
- Verify Python version: `python --version`
- Update pip: `pip install --upgrade pip`

#### Backend Issues:
- Check if port 8000 is available
- Verify `.env` file configuration
- Check Python dependencies are installed correctly

#### Android Development Issues:
- Ensure Android Studio and SDK are properly configured
- Verify AVD is running and has sufficient resources
- Check if virtualization is enabled in BIOS (for Windows/Linux)
- Make sure ANDROID_HOME environment variable is set

#### Network Issues:
- Ensure stable internet connection
- Check firewall settings if accessing from other devices
- Verify API endpoints are accessible

### Performance Tips:
- Allocate sufficient RAM to your AVD (4GB recommended)
- Close unnecessary applications to free up system resources
- Use SSD storage for better performance
- Enable hardware acceleration for Android emulator

## 📝 Development Notes

- The backend must be running before starting the web UI
- Make sure to activate your Python virtual environment in each terminal session
- Keep your API keys secure and never commit them to version control
- For production deployment, use environment variables instead of `.env` files

## 🤝 Contributing

Please ensure you follow the setup instructions completely before submitting any issues or pull requests.

## 📞 Support

If you encounter any issues during setup, please check the troubleshooting section first. For additional support, create an issue with detailed information about your system and the specific error messages you're encountering.
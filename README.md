# Aerial Threat Detection System

A desktop application built with Electron and Vue.js for detecting aerial threats using YOLO object detection. The application provides real-time threat detection capabilities through an intuitive desktop interface.

## Features

- **Desktop Application**: Cross-platform Electron app for Windows, macOS, and Linux
- **Real-time Detection**: YOLO-based object detection for aerial threats
- **Vue.js Frontend**: Modern, responsive user interface
- **Python Backend**: FastAPI server for image processing and detection
- **File Upload**: Support for image and video file analysis
- **Detection Results**: Visual output with threat identification and confidence scores

## Tech Stack

- **Frontend**: Vue 3 + Vite + Electron
- **Backend**: Python + FastAPI + YOLO
- **Object Detection**: YOLOv11 model
- **Desktop Framework**: Electron

## Prerequisites

Before installing the application, ensure you have the following installed:

### Required Software

- **Node.js**: v20.19.0 or v22.12.0+ (check with `node --version`)
- **npm**: v8.0.0 or higher (check with `npm --version`)
- **Python**: 3.8 - 3.11 (check with `python --version`)
- **pip**: Python package installer (check with `pip --version`)
- **Git**: For version control (optional but recommended)

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Ubuntu 18.04+
- **RAM**: Minimum 8GB (16GB recommended for better performance)
- **Storage**: At least 2GB free space
- **GPU**: Optional (CUDA-compatible GPU for faster inference)

## Installation Guide

Follow these steps carefully to set up the Aerial Threat Detection System:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "AerialThreat Detection"
```

### 2. Frontend Setup (Node.js Dependencies)

**Install all frontend dependencies:**

```bash
npm install
```

**Frontend Dependencies Installed:**

- `vue` (^3.5.25) - Progressive JavaScript framework
- `vue-router` (^4.6.3) - Official router for Vue.js
- `pinia` (^3.0.4) - State management for Vue.js
- `axios` (^1.13.2) - HTTP client for API calls
- `electron` (^39.2.5) - Desktop application framework
- `vite` (^7.2.4) - Build tool and development server
- Additional development tools (ESLint, Prettier, Vitest)

### 3. Backend Setup (Python Dependencies)

**Navigate to backend directory:**

```bash
cd backend
```

**Install Python dependencies:**

```bash
# For Windows
pip install -r requirements.txt

# For macOS/Linux (if you encounter permission issues)
sudo pip install -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

**Python Dependencies Installed:**

- `flask` (3.0.0) - Web framework for API server
- `flask-cors` (4.0.0) - Cross-Origin Resource Sharing support
- `ultralytics` (8.1.0) - YOLO object detection framework
- `opencv-python` (4.9.0.80) - Computer vision library
- `numpy` (1.24.3) - Numerical computing library
- `torch` (2.1.0) - PyTorch machine learning framework
- `torchvision` (0.16.0) - Computer vision datasets and transforms
- `Pillow` (10.2.0) - Python Imaging Library
- `werkzeug` (3.0.1) - WSGI utility library

### 4. Verify Installation

**Check if all dependencies are installed correctly:**

```bash
# Return to root directory
cd ..

# Verify Node.js dependencies
npm list --depth=0

# Verify Python dependencies
cd backend
pip list
```

### 5. Download YOLO Model

The YOLOv11 model file (`yolo11s.pt`) should be present in the root directory. If missing:

```bash
# The model will be automatically downloaded when first running the detection
# Or manually download from Ultralytics if needed
```

## Development

### Run as Desktop Application (Electron)

```sh
npm run electron-dev
```

This will:

- Start the Vue.js development server
- Launch the Electron desktop application
- Enable hot-reload for development

### Run as Web Application

```sh
npm run dev
```

### Start Backend Server

```sh
cd backend
python server.py
```

The backend server will run on `http://localhost:8000`

## Production

### Build for Production

```sh
npm run build
```

### Package Electron App

```sh
npm run electron-build
```

## Project Structure

```
├── src/                    # Vue.js frontend source
│   ├── App.vue            # Main Vue application component
│   ├── main.js            # Vue application entry point
│   ├── components/         # Vue components
│   │   └── DetectionView.vue # Main detection interface component
│   ├── router/            # Vue router configuration
│   │   └── index.js       # Router setup
│   ├── services/          # API services
│   └── stores/            # Pinia stores
│       └── counter.js     # Application state management
├── electron/              # Electron main process
│   └── main.js           # Electron entry point
├── backend/               # Python backend
│   ├── server.py         # FastAPI server
│   ├── detect.py         # YOLO detection logic
│   ├── requirements.txt  # Python dependencies
│   ├── uploads/          # Uploaded files directory
│   └── outputs/          # Detection results directory
├── public/                # Static assets
├── index.html            # Main HTML template
├── package.json          # Node.js dependencies and scripts
├── vite.config.js        # Vite build configuration
├── vitest.config.js      # Vitest testing configuration
├── eslint.config.js      # ESLint configuration
├── jsconfig.json         # JavaScript/TypeScript configuration
└── yolo11s.pt            # YOLOv11 model file
```

## Usage

1. Launch the desktop application using `npm run electron-dev`
2. Upload an image or video file for analysis
3. View detection results with identified threats and confidence scores
4. Save or export results as needed

## Development Tools

### Lint Code

```sh
npm run lint
```

### Run Tests

```sh
npm run test:unit
```

## Troubleshooting

### Common Installation Issues

#### Node.js Issues

- **"node: command not found"**: Install Node.js from [nodejs.org](https://nodejs.org/)
- **Version conflicts**: Use Node Version Manager (nvm) to manage Node.js versions
- **npm install fails**: Try `npm cache clean --force` and reinstall

#### Python Issues

- **"python: command not found"**: Ensure Python is added to your system PATH
- **pip install fails**: Try upgrading pip with `python -m pip install --upgrade pip`
- **Torch installation issues**: Visit [PyTorch](https://pytorch.org/) for platform-specific installation commands
- **OpenCV issues**: May require additional system libraries on Linux

#### Electron Issues

- **Electron fails to start**: Ensure ports 5173 is available
- **"wait-on" timeout**: Backend server might not be running

#### Backend Server Issues

- **Port 8000 already in use**: Change port in `server.py` or kill existing process
- **YOLO model loading fails**: Ensure `yolo11s.pt` file is present and not corrupted

### Getting Help

- Check console/terminal output for specific error messages
- Ensure all prerequisites are properly installed
- Try running components individually to isolate issues

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur)

**Recommended VS Code Extensions:**

- Vue - Official (Vue.volar)
- Python (ms-python.python)
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)

## License

This project is for educational/research purposes.

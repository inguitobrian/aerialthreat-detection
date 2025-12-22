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

- Node.js (v16 or higher)
- Python 3.8 or higher
- npm or yarn

## Project Setup

### 1. Install Frontend Dependencies

```sh
npm install
```

### 2. Install Python Dependencies

```sh
cd backend
pip install -r requirements.txt
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

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur)

## License

This project is for educational/research purposes.

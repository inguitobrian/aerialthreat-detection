<template>
  <div class="detection-container">
    <header class="header">
      <h1>Aerial Threat Detection System</h1>
      <p class="subtitle">Soldier and Civilian Classification using Deep Learning</p>
    </header>

    <div class="main-content">
      <!-- Upload Section -->
      <div class="upload-section" v-if="!processing && !result">
        <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
          <input
            type="file"
            ref="fileInput"
            @change="handleFileSelect"
            accept="image/*,video/*"
            style="display: none"
          />
          <div class="upload-icon">📁</div>
          <h2>Upload Image or Video</h2>
          <p>Drag and drop or click to select</p>
          <button @click="$refs.fileInput.click()" class="btn-primary">Select File</button>
          <p class="file-info">Supported: JPG, PNG, MP4</p>

          <!-- Speed Mode Selector for Videos -->
          <div class="speed-mode-selector">
            <h4>🚀 Video Processing Speed</h4>
            <div class="speed-options">
              <label class="speed-option">
                <input type="radio" v-model="speedMode" value="fast" name="speed" />
                <span class="speed-label">
                  <span class="speed-title">⚡ Fast</span>
                  <span class="speed-desc">Skip frames • ~3x faster</span>
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- Model Info -->
        <div class="model-info" v-if="modelInfo">
          <h3>📊 Model Information</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">Model:</span>
              <span class="value">{{ modelInfo.model_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">Classes:</span>
              <span class="value">{{ getClassNames(modelInfo.classes) }}</span>
            </div>
            <div class="info-item">
              <span class="label">Status:</span>
              <span class="value status-active">● Active</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Processing Section -->
      <div class="processing-section" v-if="processing">
        <div class="spinner"></div>
        <h2>Processing {{ fileType }}...</h2>
        <p>{{ statusMessage }}</p>
        <div class="progress-bar" v-if="progress > 0">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <p class="progress-text" v-if="progress > 0">{{ progress.toFixed(1) }}%</p>
      </div>

      <!-- Results Section -->
      <div class="results-section" v-if="result && !processing">
        <div class="results-header">
          <h2>🎯 Detection Results</h2>
          <button @click="reset" class="btn-secondary">Upload New File</button>
        </div>

        <!-- Image Results -->
        <div v-if="result.type === 'image'" class="image-result">
          <div class="result-image">
            <img :src="'data:image/jpeg;base64,' + result.annotated_image" alt="Detected" />
            <div class="image-actions">
              <button
                @click="downloadImage"
                class="btn-download"
                title="Save the image with detection boxes and labels"
              >
                💾 Save Detected Image
              </button>
              <button
                @click="downloadOriginalImage"
                class="btn-download"
                v-if="result.original_image"
                title="Save the original image without annotations"
              >
                📷 Save Original Image
              </button>
              <button
                @click="downloadBothImages"
                class="btn-download"
                v-if="result.original_image"
                title="Download both original and detected images"
              >
                📦 Save Both Images
              </button>
            </div>
          </div>
          <div class="detections-summary">
            <h3>📋 Summary</h3>
            <div class="summary-stats">
              <div class="stat-card">
                <div class="stat-number">{{ result.total_detections }}</div>
                <div class="stat-label">Total Detections</div>
              </div>
              <div class="stat-card" v-if="soldierCount > 0">
                <div class="stat-number soldier">{{ soldierCount }}</div>
                <div class="stat-label">Soldiers</div>
              </div>
              <div class="stat-card" v-if="civilianCount > 0">
                <div class="stat-number civilian">{{ civilianCount }}</div>
                <div class="stat-label">Civilians</div>
              </div>
            </div>

            <!-- Detection Details -->
            <div class="detections-list" v-if="result.detections.length > 0">
              <h4>Detection Details:</h4>
              <div
                v-for="(detection, index) in result.detections"
                :key="index"
                class="detection-item"
                :class="detection.class"
              >
                <span class="detection-index">{{ index + 1 }}.</span>
                <span class="detection-class">{{ detection.class.toUpperCase() }}</span>
                <span class="detection-confidence">
                  {{ (detection.confidence * 100).toFixed(1) }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Video Results -->
        <div v-if="result.type === 'video'" class="video-result">
          <div class="video-header">
            <h3>📹 Processed Video with Detections</h3>
          </div>

          <div class="video-player-container">
            <video
              :src="videoUrl"
              controls
              preload="metadata"
              class="processed-video"
              @loadeddata="onVideoLoaded"
              @error="onVideoError"
            >
              Your browser does not support the video tag.
            </video>
            <div class="video-actions">
              <button
                @click="downloadVideo"
                class="btn-download"
                title="Download the processed video with detections"
              >
                💾 Download Video
              </button>
            </div>
          </div>

          <div class="video-info">
            <div class="summary-stats">
              <div class="stat-card">
                <div class="stat-number">{{ result.total_detections }}</div>
                <div class="stat-label">Total Detections</div>
              </div>
              <div class="stat-card">
                <div class="stat-number">{{ result.filename }}</div>
                <div class="stat-label">Processed File</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error Section -->
      <div class="error-section" v-if="error">
        <div class="error-box">
          <h3>⚠️ Error</h3>
          <p>{{ error }}</p>
          <button @click="reset" class="btn-primary">Try Again</button>
        </div>
      </div>

      <!-- Notification -->
      <div class="notification" v-if="notification" :class="notification.type">
        <span>{{ notification.message }}</span>
        <button @click="notification = null" class="notification-close">×</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DetectionView',
  data() {
    return {
      selectedFile: null,
      processing: false,
      result: null,
      error: null,
      modelInfo: null,
      progress: 0,
      statusMessage: '',
      fileType: '',
      videoUrl: null,
      speedMode: 'fast', // Default to fast processing
      notification: null, // For showing save notifications
    }
  },
  computed: {
    soldierCount() {
      if (!this.result?.detections) return 0
      return this.result.detections.filter((d) => d.class === 'soldier').length
    },
    civilianCount() {
      if (!this.result?.detections) return 0
      return this.result.detections.filter((d) => d.class === 'civilian').length
    },
  },
  mounted() {
    this.loadModelInfo()
    // Add keyboard shortcut for saving
    document.addEventListener('keydown', this.handleKeydown)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
  },
  methods: {
    getClassNames(classes) {
      if (Array.isArray(classes)) {
        return classes.join(', ')
      } else if (typeof classes === 'object' && classes !== null) {
        return Object.values(classes).join(', ')
      }
      return 'Unknown'
    },
    async loadModelInfo() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/model/info')
        this.modelInfo = response.data
      } catch (err) {
        console.error('Failed to load model info:', err)
      }
    },
    handleDrop(e) {
      const files = e.dataTransfer.files
      if (files.length > 0) {
        this.processFile(files[0])
      }
    },
    handleFileSelect(e) {
      const files = e.target.files
      if (files.length > 0) {
        this.processFile(files[0])
      }
    },
    async processFile(file) {
      this.selectedFile = file
      this.error = null
      this.result = null
      this.processing = true
      this.progress = 0

      // Determine file type
      const isVideo = file.type.startsWith('video/')
      this.fileType = isVideo ? 'video' : 'image'

      // Update status message based on speed mode for videos
      if (isVideo) {
        const speedLabels = {
          fast: '⚡ Fast processing mode',
          normal: '⚖️ Balanced processing mode',
          high_quality: '🎯 High quality processing mode',
        }
        this.statusMessage = `${speedLabels[this.speedMode]} - Processing ${this.fileType}...`
      } else {
        this.statusMessage = `Analyzing ${this.fileType}...`
      }

      const formData = new FormData()
      formData.append('file', file)

      // Add speed mode for videos
      if (isVideo) {
        formData.append('speed_mode', this.speedMode)
      }

      try {
        const response = await axios.post('http://127.0.0.1:5000/api/detect', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            this.progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          },
        })

        this.result = response.data

        // Set video URL if it's a video result
        if (response.data.type === 'video' && response.data.video_url) {
          this.videoUrl = `http://127.0.0.1:5000${response.data.video_url}`
        }

        this.processing = false
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to process file'
        this.processing = false
      }
    },
    onVideoLoaded() {
      console.log('Video loaded successfully')
    },
    onVideoError(event) {
      console.error('Video error:', event)
      this.error = 'Error loading processed video'
    },
    downloadVideo() {
      if (this.videoUrl) {
        const link = document.createElement('a')
        link.href = this.videoUrl
        link.download = this.result.output_video
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        this.showNotification('✅ Video downloaded successfully!')
      }
    },
    showNotification(message, type = 'success') {
      this.notification = { message, type }
      setTimeout(() => {
        this.notification = null
      }, 3000)
    },
    downloadImage() {
      if (this.result && this.result.annotated_image) {
        this.downloadBase64Image(this.result.annotated_image, 'detected_')
        this.showNotification('✅ Detected image saved successfully!')
      }
    },
    downloadOriginalImage() {
      if (this.result && this.result.original_image) {
        this.downloadBase64Image(this.result.original_image, 'original_')
        this.showNotification('✅ Original image saved successfully!')
      }
    },
    async downloadBothImages() {
      if (this.result && this.result.annotated_image && this.result.original_image) {
        // Download detected image
        this.downloadBase64Image(this.result.annotated_image, 'detected_')

        // Wait a bit to avoid browser blocking multiple downloads
        setTimeout(() => {
          this.downloadBase64Image(this.result.original_image, 'original_')
          this.showNotification('✅ Both images saved successfully!')
        }, 500)
      }
    },
    downloadBase64Image(base64Data, prefix = '') {
      if (base64Data) {
        const fileName = this.result.filename
          ? `${prefix}${this.result.filename}`
          : `${prefix}detection_result_${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.jpg`

        // Convert base64 to blob
        const byteCharacters = atob(base64Data)
        const byteNumbers = new Array(byteCharacters.length)
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i)
        }
        const byteArray = new Uint8Array(byteNumbers)
        const blob = new Blob([byteArray], { type: 'image/jpeg' })

        // Create download link
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = fileName
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        // Clean up
        URL.revokeObjectURL(url)
      }
    },
    async saveImageToServer() {
      // Alternative method to save image via backend endpoint
      if (this.result && this.result.annotated_image) {
        try {
          const response = await axios.post(
            'http://127.0.0.1:5000/api/download/image',
            {
              image_data: this.result.annotated_image,
              filename: this.result.filename,
            },
            {
              responseType: 'blob',
            },
          )

          // Create download link from response
          const url = window.URL.createObjectURL(new Blob([response.data]))
          const link = document.createElement('a')
          link.href = url
          link.download = this.result.filename
            ? `detected_${this.result.filename}`
            : 'detection_result.jpg'
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)
        } catch (error) {
          console.error('Error saving image:', error)
          this.error = 'Failed to save image'
        }
      }
    },
    downloadDetectionReport() {
      if (this.result) {
        // Create detection report data
        const reportData = {
          metadata: {
            filename: this.result.filename,
            type: this.result.type,
            timestamp: new Date().toISOString(),
            total_detections: this.result.total_detections,
          },
          detections: this.result.detections,
          summary: {
            soldiers: this.soldierCount,
            civilians: this.civilianCount,
          },
        }

        // Add additional metadata for images
        if (this.result.type === 'image' && this.result.image_dimensions) {
          reportData.metadata.image_dimensions = this.result.image_dimensions
        }

        // Add processing info for videos
        if (this.result.type === 'video' && this.result.processing_info) {
          reportData.metadata.processing_info = this.result.processing_info
          reportData.metadata.speed_mode = this.result.speed_mode
        }

        // Convert to JSON
        const jsonData = JSON.stringify(reportData, null, 2)
        const blob = new Blob([jsonData], { type: 'application/json' })

        // Create download link
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = this.result.filename
          ? `detection_report_${this.result.filename.split('.')[0]}.json`
          : `detection_report_${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)

        // Clean up
        URL.revokeObjectURL(url)
        this.showNotification('✅ Detection report saved successfully!')
      }
    },
    handleKeydown(event) {
      // Ctrl+S or Cmd+S to save main result
      if ((event.ctrlKey || event.metaKey) && event.key === 's' && this.result) {
        event.preventDefault()
        if (this.result.type === 'image') {
          this.downloadImage()
        } else if (this.result.type === 'video') {
          this.downloadVideo()
        }
      }
      // Ctrl+Shift+S or Cmd+Shift+S to save report
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'S' && this.result) {
        event.preventDefault()
        this.downloadDetectionReport()
      }
    },
    reset() {
      this.selectedFile = null
      this.processing = false
      this.result = null
      this.error = null
      this.progress = 0
      this.statusMessage = ''
      this.videoUrl = null
      this.notification = null
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },
  },
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Roboto+Mono:wght@400;500;700&display=swap');

.detection-container {
  min-height: 100vh;
  background:
    linear-gradient(45deg, rgba(10, 20, 10, 0.9) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(10, 20, 10, 0.9) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, rgba(15, 30, 15, 0.8) 75%),
    linear-gradient(-45deg, transparent 75%, rgba(15, 30, 15, 0.8) 75%),
    linear-gradient(135deg, #0a1f0a 0%, #1a3d1a 25%, #2d5a2d 50%, #1a3d1a 75%, #0a1f0a 100%);
  background-size:
    60px 60px,
    60px 60px,
    60px 60px,
    60px 60px,
    100% 100%;
  background-position:
    0 0,
    0 30px,
    30px -30px,
    -30px 0px,
    0 0;
  padding: 20px;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  color: #00ff41;
  position: relative;
}

.header {
  text-align: center;
  color: #00ff41;
  margin-bottom: 40px;
  position: relative;
  padding: 30px;
  background: rgba(0, 0, 0, 0.8);
  border: 2px solid #00ff41;
  border-radius: 15px;
  box-shadow:
    0 0 20px rgba(0, 255, 65, 0.3),
    inset 0 0 20px rgba(0, 255, 65, 0.1);
}

.header::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #00ff41, #008f2f, #00ff41);
  border-radius: 15px;
  z-index: -1;
  animation: borderGlow 2s ease-in-out infinite alternate;
}

@keyframes borderGlow {
  0% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

.header h1 {
  font-family: 'Orbitron', monospace;
  font-size: 3rem;
  font-weight: 900;
  margin-bottom: 10px;
  text-shadow:
    0 0 10px #00ff41,
    0 0 20px #00ff41,
    0 0 30px #00ff41;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.8;
  font-family: 'Roboto Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #66ff66;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
}

.upload-section {
  display: grid;
  gap: 30px;
}

.upload-area {
  background:
    linear-gradient(45deg, rgba(0, 30, 0, 0.9) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(0, 30, 0, 0.9) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, rgba(0, 40, 0, 0.9) 75%),
    linear-gradient(-45deg, transparent 75%, rgba(0, 40, 0, 0.9) 75%), rgba(0, 20, 0, 0.95);
  background-size:
    30px 30px,
    30px 30px,
    30px 30px,
    30px 30px,
    100% 100%;
  border: 2px solid #00ff41;
  border-radius: 15px;
  padding: 60px 40px;
  text-align: center;
  box-shadow:
    0 10px 30px rgba(0, 0, 0, 0.8),
    0 0 20px rgba(0, 255, 65, 0.2),
    inset 0 0 30px rgba(0, 255, 65, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.upload-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 255, 65, 0.1), transparent);
  transition: left 0.5s;
}

.upload-area:hover::before {
  left: 100%;
}

.upload-area:hover {
  transform: translateY(-5px);
  box-shadow:
    0 15px 40px rgba(0, 0, 0, 0.9),
    0 0 30px rgba(0, 255, 65, 0.4),
    inset 0 0 40px rgba(0, 255, 65, 0.15);
  border-color: #66ff66;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  filter: hue-rotate(90deg) brightness(1.2);
  text-shadow: 0 0 10px #00ff41;
}

.upload-area h2 {
  color: #00ff41;
  margin-bottom: 10px;
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
}

.upload-area p {
  color: #66ff66;
  margin-bottom: 20px;
  font-family: 'Roboto Mono', monospace;
}

.btn-primary {
  background: linear-gradient(135deg, #003d00 0%, #00ff41 50%, #003d00 100%);
  color: #000;
  border: 2px solid #00ff41;
  padding: 15px 35px;
  border-radius: 25px;
  font-size: 1.1rem;
  font-weight: 700;
  font-family: 'Orbitron', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow:
    0 5px 15px rgba(0, 255, 65, 0.3),
    inset 0 0 20px rgba(255, 255, 255, 0.1);
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.btn-primary:hover::before {
  left: 100%;
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow:
    0 8px 25px rgba(0, 255, 65, 0.5),
    inset 0 0 30px rgba(255, 255, 255, 0.2);
  text-shadow: 0 0 10px rgba(0, 0, 0, 0.8);
}

.btn-secondary {
  background: rgba(0, 0, 0, 0.8);
  color: #00ff41;
  border: 2px solid #00ff41;
  padding: 12px 28px;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Orbitron', monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
}

.btn-secondary:hover {
  background: #00ff41;
  color: #000;
  box-shadow: 0 0 25px rgba(0, 255, 65, 0.6);
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.8);
}

.file-info {
  font-size: 0.9rem;
  color: #66ff66;
  margin-top: 15px;
  font-family: 'Roboto Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.model-info {
  background:
    linear-gradient(45deg, rgba(0, 20, 0, 0.95) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(0, 20, 0, 0.95) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, rgba(0, 30, 0, 0.95) 75%),
    linear-gradient(-45deg, transparent 75%, rgba(0, 30, 0, 0.95) 75%), rgba(0, 15, 0, 0.98);
  background-size:
    20px 20px,
    20px 20px,
    20px 20px,
    20px 20px,
    100% 100%;
  border: 2px solid #00ff41;
  border-radius: 15px;
  padding: 30px;
  box-shadow:
    0 10px 30px rgba(0, 0, 0, 0.8),
    0 0 20px rgba(0, 255, 65, 0.2),
    inset 0 0 30px rgba(0, 255, 65, 0.05);
}

.model-info h3 {
  color: #00ff41;
  margin-bottom: 20px;
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
}

.info-grid {
  display: grid;
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  border: 1px solid #00ff41;
  border-radius: 8px;
  background: rgba(0, 255, 65, 0.05);
  transition: all 0.3s ease;
}

.info-item:hover {
  background: rgba(0, 255, 65, 0.1);
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
}

.label {
  font-weight: 600;
  color: #66ff66;
  font-family: 'Roboto Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.value {
  color: #00ff41;
  font-family: 'Roboto Mono', monospace;
  font-weight: 500;
}

.status-active {
  color: #00ff41;
  font-weight: 700;
  text-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.processing-section {
  background:
    linear-gradient(45deg, rgba(0, 15, 0, 0.95) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(0, 15, 0, 0.95) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, rgba(0, 25, 0, 0.95) 75%),
    linear-gradient(-45deg, transparent 75%, rgba(0, 25, 0, 0.95) 75%), rgba(0, 10, 0, 0.98);
  background-size:
    40px 40px,
    40px 40px,
    40px 40px,
    40px 40px,
    100% 100%;
  border: 2px solid #00ff41;
  border-radius: 15px;
  padding: 60px 40px;
  text-align: center;
  box-shadow:
    0 10px 30px rgba(0, 0, 0, 0.8),
    0 0 30px rgba(0, 255, 65, 0.3),
    inset 0 0 40px rgba(0, 255, 65, 0.1);
}

.processing-section h2 {
  color: #00ff41;
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 20px;
  text-shadow: 0 0 15px rgba(0, 255, 65, 0.8);
}

.processing-section p {
  color: #66ff66;
  font-family: 'Roboto Mono', monospace;
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 6px solid rgba(0, 255, 65, 0.2);
  border-top: 6px solid #00ff41;
  border-radius: 50%;
  animation:
    spin 1s linear infinite,
    glow 2s ease-in-out infinite alternate;
  margin: 0 auto 20px;
  box-shadow: 0 0 30px rgba(0, 255, 65, 0.5);
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes glow {
  0% {
    box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
  }
  100% {
    box-shadow: 0 0 40px rgba(0, 255, 65, 0.8);
  }
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: rgba(0, 0, 0, 0.8);
  border: 1px solid #00ff41;
  border-radius: 8px;
  overflow: hidden;
  margin: 20px 0 10px;
  box-shadow: inset 0 0 10px rgba(0, 255, 65, 0.2);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #003d00 0%, #00ff41 50%, #66ff66 100%);
  transition: width 0.3s ease;
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.6);
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 100%
  );
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-text {
  color: #00ff41;
  font-weight: 700;
  font-family: 'Roboto Mono', monospace;
  font-size: 1.1rem;
  text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
}

.results-section {
  background:
    linear-gradient(45deg, rgba(0, 20, 0, 0.95) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(0, 20, 0, 0.95) 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, rgba(0, 30, 0, 0.95) 75%),
    linear-gradient(-45deg, transparent 75%, rgba(0, 30, 0, 0.95) 75%), rgba(0, 15, 0, 0.98);
  background-size:
    50px 50px,
    50px 50px,
    50px 50px,
    50px 50px,
    100% 100%;
  border: 2px solid #00ff41;
  border-radius: 15px;
  padding: 30px;
  box-shadow:
    0 10px 30px rgba(0, 0, 0, 0.8),
    0 0 25px rgba(0, 255, 65, 0.2),
    inset 0 0 35px rgba(0, 255, 65, 0.08);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #00ff41;
}

.results-header h2 {
  color: #00ff41;
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 15px rgba(0, 255, 65, 0.8);
}

.image-result {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.result-image {
  border-radius: 10px;
  overflow: hidden;
  box-shadow:
    0 10px 30px rgba(0, 0, 0, 0.8),
    0 0 20px rgba(0, 255, 65, 0.3);
  border: 2px solid #00ff41;
}

.result-image img {
  width: 100%;
  height: auto;
  display: block;
  filter: brightness(1.1) contrast(1.1);
}

.detections-summary h3 {
  color: #00ff41;
  margin-bottom: 20px;
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
}

.video-header h3 {
  color: #00ff41;
  margin-bottom: 25px;
  text-align: center;
  font-family: 'Orbitron', monospace;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-size: 1.8rem;
  text-shadow: 0 0 15px rgba(0, 255, 65, 0.8);
}

.summary-stats {
  display: grid;
  gap: 20px;
  margin-bottom: 30px;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.stat-card {
  background: linear-gradient(
    135deg,
    rgba(0, 40, 0, 0.9) 0%,
    rgba(0, 60, 0, 0.9) 50%,
    rgba(0, 40, 0, 0.9) 100%
  );
  color: #00ff41;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  border: 2px solid #00ff41;
  box-shadow:
    0 8px 25px rgba(0, 0, 0, 0.6),
    0 0 20px rgba(0, 255, 65, 0.3),
    inset 0 0 20px rgba(0, 255, 65, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 255, 65, 0.2), transparent);
  transition: left 0.5s;
}

.stat-card:hover::before {
  left: 100%;
}

.stat-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow:
    0 12px 35px rgba(0, 0, 0, 0.8),
    0 0 30px rgba(0, 255, 65, 0.5),
    inset 0 0 30px rgba(0, 255, 65, 0.15);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-number.soldier {
  color: #ef4444;
}

.stat-number.civilian {
  color: #22c55e;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.detections-list {
  margin-top: 20px;
}

.detections-list h4 {
  color: #00ff41;
  margin-bottom: 15px;
  font-family: 'Orbitron', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.detection-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  margin-bottom: 10px;
  background: rgba(0, 255, 65, 0.05);
  border-radius: 10px;
  border: 1px solid #00ff41;
  transition: all 0.3s ease;
}

.detection-item:hover {
  background: rgba(0, 255, 65, 0.1);
  box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
  transform: translateX(5px);
}

.detection-item.soldier {
  border-left: 4px solid #ff4444;
  background: rgba(255, 68, 68, 0.05);
}

.detection-item.soldier:hover {
  background: rgba(255, 68, 68, 0.1);
  box-shadow: 0 0 20px rgba(255, 68, 68, 0.3);
}

.detection-item.civilian {
  border-left: 4px solid #44ff44;
  background: rgba(68, 255, 68, 0.05);
}

.detection-item.civilian:hover {
  background: rgba(68, 255, 68, 0.1);
  box-shadow: 0 0 20px rgba(68, 255, 68, 0.3);
}

.detection-index {
  font-weight: 700;
  color: #66ff66;
  font-family: 'Roboto Mono', monospace;
  font-size: 1.1rem;
}

.detection-class {
  flex: 1;
  font-weight: 700;
  color: #00ff41;
  font-family: 'Orbitron', monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.detection-confidence {
  color: #00ff41;
  font-weight: 700;
  font-family: 'Roboto Mono', monospace;
  background: rgba(0, 255, 65, 0.1);
  padding: 5px 10px;
  border-radius: 15px;
  border: 1px solid #00ff41;
}

.video-result {
  text-align: center;
}

.video-header h3 {
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.video-player-container {
  margin: 20px 0;
  border-radius: 15px;
  overflow: hidden;
  box-shadow:
    0 15px 40px rgba(0, 0, 0, 0.9),
    0 0 30px rgba(0, 255, 65, 0.3),
    inset 0 0 20px rgba(0, 255, 65, 0.1);
  background: #000;
  border: 2px solid #00ff41;
  position: relative;
}

.video-player-container::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #00ff41, #003d00, #00ff41);
  border-radius: 15px;
  z-index: -1;
  animation: videoGlow 3s ease-in-out infinite alternate;
}

@keyframes videoGlow {
  0% {
    opacity: 0.5;
  }
  100% {
    opacity: 0.8;
  }
}

.processed-video {
  width: 100%;
  max-width: 900px;
  height: auto;
  display: block;
  margin: 0 auto;
  filter: brightness(1.1) contrast(1.1);
}

.video-controls {
  margin-top: 20px;
  text-align: center;
}

.btn-download {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
}

.btn-download:hover {
  transform: scale(1.05);
  box-shadow:
    0 5px 15px rgba(34, 197, 94, 0.4),
    0 0 30px rgba(0, 255, 65, 0.5);
}

.image-actions,
.video-actions {
  margin-top: 20px;
  text-align: center;
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.image-actions .btn-download,
.video-actions .btn-download {
  flex: 0 1 auto;
  min-width: 160px;
}

.video-result {
  text-align: center;
}

.video-info h3 {
  color: #333;
  margin-bottom: 20px;
}

.video-note {
  color: #22c55e;
  font-weight: 600;
  margin-top: 20px;
  padding: 15px;
  background: #f0fdf4;
  border-radius: 8px;
}

.error-section {
  background: white;
  border-radius: 15px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.error-box {
  color: #ef4444;
}

.error-box h3 {
  margin-bottom: 15px;
}

.error-box p {
  margin-bottom: 20px;
  color: #666;
}

/* Speed mode selector styling */
.speed-mode-section {
  background: rgba(0, 30, 0, 0.8);
  border: 1px solid #00ff41;
  border-radius: 10px;
  padding: 20px;
  margin: 20px 0;
  box-shadow:
    0 5px 15px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(0, 255, 65, 0.1);
}

.speed-mode-title {
  font-family: 'Orbitron', monospace;
  font-size: 1.2rem;
  font-weight: 700;
  color: #00ff41;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 15px;
  text-align: center;
  text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
}

.speed-options {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
}

.speed-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 15px;
  border: 1px solid rgba(0, 255, 65, 0.3);
  border-radius: 8px;
  background: rgba(0, 20, 0, 0.6);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.speed-option:hover {
  border-color: #00ff41;
  background: rgba(0, 40, 0, 0.8);
  box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
}

.speed-option input[type='radio'] {
  appearance: none;
  width: 18px;
  height: 18px;
  border: 2px solid #00ff41;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.speed-option input[type='radio']:checked {
  background: #00ff41;
  box-shadow:
    0 0 10px rgba(0, 255, 65, 0.8),
    inset 0 0 5px rgba(0, 0, 0, 0.5);
  animation: radioGlow 1s ease-in-out;
}

.speed-option input[type='radio']:checked::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  background: #000;
  border-radius: 50%;
}

@keyframes radioGlow {
  0% {
    box-shadow: 0 0 5px rgba(0, 255, 65, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(0, 255, 65, 1);
  }
  100% {
    box-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
  }
}

.speed-option label {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.95rem;
  font-weight: 500;
  color: #66ff66;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: color 0.3s ease;
}

.speed-option input[type='radio']:checked + label {
  color: #00ff41;
  font-weight: 700;
  text-shadow: 0 0 8px rgba(0, 255, 65, 0.6);
}

.speed-description {
  font-size: 0.8rem;
  color: rgba(102, 255, 102, 0.7);
  text-align: center;
  margin-top: 10px;
  font-family: 'Roboto Mono', monospace;
}

@media (max-width: 768px) {
  .detection-container {
    padding: 15px;
  }

  .header h1 {
    font-size: 2.5rem;
  }

  .speed-options {
    flex-direction: column;
    gap: 15px;
  }

  .speed-option {
    justify-content: center;
  }

  .image-result {
    grid-template-columns: 1fr;
  }

  .results-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .summary-stats {
    grid-template-columns: 1fr;
  }

  .processed-video {
    max-width: 100%;
  }

  .upload-area {
    padding: 40px 20px;
  }

  .stat-number {
    font-size: 2.5rem;
  }
}

@media (max-width: 480px) {
  .header h1 {
    font-size: 2rem;
  }

  .btn-primary,
  .btn-secondary,
  .btn-download {
    padding: 12px 20px;
    font-size: 1rem;
  }

  .stat-number {
    font-size: 2rem;
  }

  .detection-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

/* Additional military-themed effects */
.detection-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(circle at 20% 50%, rgba(0, 255, 65, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(0, 255, 65, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(0, 255, 65, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: -1;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 12px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 20, 0, 0.8);
  border-radius: 6px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #00ff41 0%, #003d00 100%);
  border-radius: 6px;
  border: 1px solid #00ff41;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #66ff66 0%, #00ff41 100%);
  box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
}

/* Selection styling */
::selection {
  background: rgba(0, 255, 65, 0.3);
  color: #00ff41;
}

/* Focus styles */
button:focus,
input:focus {
  outline: 2px solid #00ff41;
  outline-offset: 2px;
}

/* Notification Styles */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 300px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease-out;
}

.notification.success {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  border: 1px solid #00ff41;
}

.notification.error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border: 1px solid #ff4444;
}

.notification-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  margin-left: 15px;
  padding: 0;
  line-height: 1;
}

.notification-close:hover {
  opacity: 0.7;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>

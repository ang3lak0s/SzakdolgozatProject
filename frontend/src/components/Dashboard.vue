<template>
  <div class="dashboard-container">
    <div class="dashboard-grid">

      <!-- ================================================================= -->
      <!-- LEFT COLUMN: Workflow Controller, Diagnostic HUD & Target Flash  -->
      <!-- ================================================================= -->
      <div class="main-column">

        <!-- Header / Status Banner -->
        <div class="card glass-card header-card">
          <div class="header-content">
            <div>
              <h2>{{ t('dashTitle') }}</h2>
              <p class="subtitle">{{ t('dashSubtitle') }}</p>
            </div>
            <div class="port-connection-wrapper">
              <div class="port-connection-box">
                <span class="status-indicator" :class="{ 'online': isConnected, 'offline': !isConnected }"></span>
                <span class="status-text">{{ isConnected ? t('portConnected') : t('portDisconnected') }}</span>
                <button @click="toggleSerial" class="btn-port" :class="{ 'connected': isConnected }">
                  {{ isConnected ? t('btnDisconnect') : t('btnConnect') }}
                </button>
              </div>
              <span class="linux-hint">{{ t('linuxDialoutHint') }}</span>
            </div>
          </div>

          <!-- Workflow Stepper -->
          <div class="stepper-bar">
            <div class="step-item" :class="{ 'active': currentStep >= 1, 'current': currentStep === 1, 'done': currentStep > 1 }">
              <div class="step-circle">1</div>
              <div class="step-label">{{ t('step1') }}</div>
            </div>
            <div class="step-divider" :class="{ 'filled': currentStep > 1 }"></div>
            <div class="step-item" :class="{ 'active': currentStep >= 2, 'current': currentStep === 2, 'done': currentStep > 2, 'failed': diagState.result === 'FAIL' }">
              <div class="step-circle">
                <span v-if="diagState.result === 'PASS'">PASS</span>
                <span v-else-if="diagState.result === 'FAIL'">FAIL</span>
                <span v-else>2</span>
              </div>
              <div class="step-label">{{ t('step2') }}</div>
            </div>
            <div class="step-divider" :class="{ 'filled': currentStep > 2 && diagState.result === 'PASS' }"></div>
            <div class="step-item" :class="{ 'active': currentStep >= 3, 'current': currentStep === 3, 'done': currentStep === 3 && isFlashingDone }">
              <div class="step-circle">3</div>
              <div class="step-label">{{ t('step3') }}</div>
            </div>
          </div>
        </div>

        <!-- STAGE 1: Diagnostic HUD -->
        <div class="card glass-card diag-hud-card">
          <div class="card-header-flex">
            <div class="title-with-badge">
              <h3>{{ t('stage1Title') }}</h3>
              <span v-if="diagState.status === 'RUNNING'" class="badge badge-running pulse">{{ t('badgeRunning') }}</span>
              <span v-else-if="diagState.result === 'PASS'" class="badge badge-success">{{ t('badgeSuccess') }}</span>
              <span v-else-if="diagState.result === 'FAIL'" class="badge badge-danger">{{ t('badgeDanger') }}</span>
              <span v-else class="badge badge-idle">{{ t('badgeIdle') }}</span>
            </div>

            <!-- Diag Trigger Buttons -->
            <div class="diag-action-bar">
              <button @click="startDiagnostics(false)" :disabled="!isConnected || diagState.status === 'RUNNING' || isFlashing" class="btn-sub btn-diag">
                {{ t('btnStartDiag') }}
              </button>
              <button @click="startDiagnostics(true)" :disabled="!isConnected || diagState.status === 'RUNNING' || isFlashing" class="btn-sub btn-fault" :title="t('btnSimFaultTitle')">
                {{ t('btnSimFault') }}
              </button>
            </div>
          </div>

          <!-- Diagnostic Telemetry Gauges Grid -->
          <div class="telemetry-grid">
            <!-- Free RAM Gauge -->
            <div class="telemetry-box">
              <div class="telemetry-label">{{ t('ramLabel') }}</div>
              <div class="telemetry-val" :class="getRamClass">
                {{ diagState.ram.free !== null ? `${diagState.ram.free} B` : '--' }}
                <span class="telemetry-sub" v-if="diagState.ram.total">/ {{ diagState.ram.total }} B</span>
              </div>
              <div class="progress-bar-bg" v-if="diagState.ram.total">
                <div class="progress-bar-fill" :style="{ width: `${(diagState.ram.free / diagState.ram.total) * 100}%` }"></div>
              </div>
            </div>

            <!-- Vcc Supply Voltage -->
            <div class="telemetry-box">
              <div class="telemetry-label">{{ t('vccLabel') }}</div>
              <div class="telemetry-val" :class="getVccClass">
                {{ diagState.vcc.volts !== null ? `${diagState.vcc.volts.toFixed(2)} V` : '--' }}
              </div>
              <span class="telemetry-sub">{{ diagState.vcc.status || t('vccSub') }}</span>
            </div>

            <!-- I2C Bus & Devices -->
            <div class="telemetry-box">
              <div class="telemetry-label">{{ t('i2cLabel') }}</div>
              <div class="telemetry-val text-cyan">
                {{ diagState.i2c.status ? diagState.i2c.status : '--' }}
              </div>
              <span class="telemetry-sub">
                {{ diagState.i2c.devices.length > 0 ? `${t('i2cDevicesFound')} ${diagState.i2c.devices.join(', ')}` : (diagState.i2c.status ? t('i2cNoDevices') : t('i2cNotScanned')) }}
              </span>
            </div>

            <!-- System Clock / Timer -->
            <div class="telemetry-box">
              <div class="telemetry-label">{{ t('clockLabel') }}</div>
              <div class="telemetry-val text-violet">
                {{ diagState.clock.freq || '--' }}
              </div>
              <span class="telemetry-sub">{{ diagState.clock.status === 'OK' ? t('clockSubOk') : (diagState.clock.status || t('clockSubCalib')) }}</span>
            </div>
          </div>

          <!-- Digital & Analog Pin Matrix -->
          <div class="pin-matrix-container">
            <div class="matrix-title">{{ t('pinMatrixTitle') }}</div>

            <!-- Digital Pins D2-D13 -->
            <div class="pin-group">
              <span class="group-tag">{{ t('digitalPinsGroup') }}</span>
              <div class="pins-row">
                <div
                  v-for="pin in digitalPins"
                  :key="'d' + pin"
                  class="pin-badge"
                  :class="getPinBadgeClass(pin)"
                >
                  <span class="pin-num">D{{ pin }}</span>
                  <span class="pin-state">{{ getPinStateText(pin) }}</span>
                </div>
              </div>
            </div>

            <!-- Analog Pins A0-A5 -->
            <div class="pin-group">
              <span class="group-tag">{{ t('analogPinsGroup') }}</span>
              <div class="pins-row">
                <div
                  v-for="aPin in analogPins"
                  :key="aPin"
                  class="pin-badge"
                  :class="getAnalogPinBadgeClass(aPin)"
                >
                  <span class="pin-num">{{ aPin }}</span>
                  <span class="pin-state">{{ getAnalogPinStateText(aPin) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Diagnostic Result Alert Banner -->
          <div v-if="diagState.result" class="diag-banner" :class="{ 'pass-banner': diagState.result === 'PASS', 'fail-banner': diagState.result === 'FAIL' }">
            <div class="banner-icon">
              <svg v-if="diagState.result === 'PASS'" class="banner-status-svg pass-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
              <svg v-else class="banner-status-svg fail-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div class="banner-text">
              <strong>{{ diagState.result === 'PASS' ? t('diagPassTitle') : t('diagFailTitle') }}</strong>
              <p v-if="diagState.result === 'PASS'">
                {{ t('diagPassDesc', diagState.totalChecks) }}
              </p>
              <p v-else>
                {{ t('diagFailDesc', diagState.failedChecks) }}
              </p>
            </div>
          </div>
        </div>

        <!-- STAGE 2: Target Firmware & Flashing Control -->
        <div class="card glass-card flash-card">
          <div class="card-header-flex">
            <h3>{{ t('stage2Title') }}</h3>
            <span v-if="isFlashing" class="badge badge-running pulse">{{ t('badgeFlashing') }}</span>
            <span v-else-if="isFlashingDone" class="badge badge-success">{{ t('badgeFirmwareRunning') }}</span>
          </div>

          <div class="flash-form-grid">
            <!-- Active Preset / Firmware Info -->
            <div class="form-group">
              <label>{{ t('selectedPresetLabel') }}</label>
              <div v-if="loadedFirmwareUrl" class="loaded-firmware-banner">
                <div class="file-meta">
                  <svg class="file-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                    <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                    <line x1="12" y1="22.08" x2="12" y2="12"></line>
                  </svg>
                  <strong>{{ presetName || 'Preset' }}</strong>
                  <span class="file-name">({{ getFilename(loadedFirmwareUrl) }})</span>
                </div>
                <button type="button" class="btn-text-clear" @click="clearLoadedFile">{{ t('changeFileBtn') }}</button>
              </div>

              <div v-else class="file-upload-wrapper">
                <input type="file" @change="handleFileChange" accept=".hex,.bin" ref="fileInput" id="firmwareUpload" class="file-input-hidden" />
                <label for="firmwareUpload" class="file-upload-dropzone">
                  <svg class="upload-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                  </svg>
                  <span v-if="firmwareFile">{{ firmwareFile.name }} ({{ (firmwareFile.size / 1024).toFixed(1) }} KB)</span>
                  <span v-else>{{ t('dropzoneText') }}</span>
                </label>
              </div>
            </div>

            <!-- Optional Preset Name & Info for saving -->
            <div class="form-row-2col">
              <div class="form-group">
                <label>{{ t('presetNameLabel') }}</label>
                <input type="text" v-model="presetName" :placeholder="t('presetNamePlaceholder')" class="text-input" />
              </div>
              <div class="form-group">
                <label>{{ t('presetDescLabel') }}</label>
                <input type="text" v-model="presetDescription" :placeholder="t('presetDescPlaceholder')" class="text-input" />
              </div>
            </div>
          </div>

          <!-- Flashing Progress Bar -->
          <div v-if="isFlashing" class="flashing-progress-box">
            <div class="flashing-progress-bar-bg">
              <div class="flashing-progress-bar-fill" :style="{ width: `${flashProgress}%` }"></div>
            </div>
            <div class="flashing-progress-labels">
              <span>STK500 Bootloader Flashing</span>
              <span>{{ flashProgress }}%</span>
            </div>
          </div>

          <!-- Master Action Buttons -->
          <div class="master-action-row">
            <button
              type="button"
              class="btn-master btn-primary-two-stage"
              @click="runTwoStageVerificationAndFlash"
              :disabled="!isConnected || isFlashing || diagState.status === 'RUNNING' || (!firmwareFile && !loadedFirmwareUrl)"
            >
              <span>{{ t('btnTwoStageFlash') }}</span>
            </button>

            <button
              type="button"
              class="btn-master btn-direct-flash"
              @click="flashTargetFirmwareDirectly"
              :disabled="!isConnected || isFlashing || diagState.status === 'RUNNING' || (!firmwareFile && !loadedFirmwareUrl)"
            >
              <span>{{ t('btnDirectFlash') }}</span>
            </button>

            <button
              type="button"
              class="btn-master btn-save-preset"
              @click="savePreset"
              :disabled="isUploading || isFlashing || !firmwareFile || !presetName"
            >
              <span>{{ isUploading ? t('btnSaving') : t('btnSavePreset') }}</span>
            </button>
          </div>

          <p v-if="flashMessage" class="feedback-msg" :class="{ 'msg-error': isError, 'msg-success': !isError }">
            {{ flashMessage }}
          </p>
        </div>

        <!-- Serial Monitor Console -->
        <div class="card glass-card monitor-card">
          <div class="monitor-header">
            <div class="monitor-title-box">
              <span class="live-dot" :class="{ 'live-active': isConnected }"></span>
              <h3>{{ t('monitorTitle') }}</h3>
            </div>
            <div class="monitor-controls">
              <button class="btn-icon" @click="clearLog" :title="t('btnClearLog')">{{ t('btnClearLog') }}</button>
              <label class="autoscroll-toggle">
                <input type="checkbox" v-model="autoScroll" /> {{ t('autoscroll') }}
              </label>
            </div>
          </div>

          <div class="console-wrapper">
            <textarea
              readonly
              class="monitor-console"
              v-model="serialLog"
              ref="consoleOutput"
              :placeholder="t('consolePlaceholder')"
            ></textarea>
          </div>

          <!-- Quick Serial Command Sender -->
          <form @submit.prevent="sendCustomCommand" class="command-bar">
            <input
              type="text"
              v-model="customCommand"
              :placeholder="t('cmdPlaceholder')"
              class="command-input"
              :disabled="!isConnected || isFlashing"
            />
            <button type="submit" class="btn-send-cmd" :disabled="!isConnected || !customCommand || isFlashing">{{ t('btnSendCmd') }}</button>
          </form>
        </div>

      </div>

      <!-- ================================================================= -->
      <!-- RIGHT COLUMN: Saved Presets & User Profile                       -->
      <!-- ================================================================= -->
      <div class="side-column">

        <!-- User Profile Card -->
        <div class="card glass-card user-card">
          <div class="user-card-header">
            <div class="user-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="user-svg">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
            <div class="user-info">
              <h4>{{ t('userPanelTitle') }}</h4>
              <span class="user-status-pill">{{ t('userLoggedIn') }}</span>
            </div>
          </div>
          <button class="btn-logout" @click="logout">{{ t('btnLogout') }}</button>
        </div>

        <!-- Saved Presets Card -->
        <div class="card glass-card presets-card">
          <div class="card-header-flex">
            <h3>{{ t('savedPresetsTitle') }}</h3>
            <span class="preset-count-badge">{{ t('presetCountBadge', presets.length) }}</span>
          </div>

          <div v-if="presets.length > 0" class="presets-list">
            <div
              class="preset-item-card"
              v-for="preset in presets"
              :key="preset.id"
              :class="{ 'active-preset': loadedPresetId === preset.id }"
            >
              <div class="preset-header-row">
                <strong class="preset-title">{{ preset.name }}</strong>
                <span class="preset-date">{{ new Date(preset.created_at).toLocaleDateString() }}</span>
              </div>
              <p v-if="preset.description" class="preset-desc">{{ preset.description }}</p>
              <div class="preset-footer-row">
                <span class="firmware-tag">{{ t('hexAttachedTag') }}</span>
                <button class="btn-load-preset" @click="loadPresetToForm(preset)">
                  {{ loadedPresetId === preset.id ? t('btnLoadedPreset') : t('btnLoadPreset') }}
                </button>
              </div>
            </div>
          </div>

          <div v-else class="empty-presets-state">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="empty-svg">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            <p>{{ t('emptyPresetsTitle') }}</p>
            <span class="empty-sub">{{ t('emptyPresetsSub') }}</span>
          </div>
        </div>

        <!-- Quick Info Guide -->
        <div class="card glass-card guide-card">
          <h4>{{ t('guideTitle') }}</h4>
          <ul class="guide-list">
            <li>{{ t('guidePoint1') }}</li>
            <li>{{ t('guidePoint2') }}</li>
            <li>{{ t('guidePoint3') }}</li>
          </ul>
        </div>

      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { t } from '../i18n';
import { flashFirmwareSTK500 } from '../utils/stk500';

export default {
  data() {
    return {
      // Form & Preset Data
      presetName: '',
      presetDescription: '',
      firmwareFile: null,
      loadedFirmwareUrl: null,
      loadedPresetId: null,
      isUploading: false,
      flashMessage: '',
      isError: false,
      presets: [],

      // Workflow Stepper (1: Port, 2: Diag, 3: Flash)
      currentStep: 1,
      isFlashing: false,
      isFlashingDone: false,
      flashProgress: 0,
      isPausedForFlashing: false,

      // Serial Connection State
      port: null,
      reader: null,
      isConnected: false,
      serialLog: '',
      autoScroll: true,
      customCommand: '',

      // Stage 1: Hardware Diagnostic State
      diagState: {
        status: 'IDLE', // 'IDLE', 'RUNNING', 'COMPLETED'
        result: null,   // 'PASS', 'FAIL'
        totalChecks: 0,
        failedChecks: 0,
        ram: { free: null, total: 2048, status: null },
        vcc: { volts: null, status: null },
        gpio: {},       // { 2: 'OK', 4: 'SHORTED_GND', ... }
        analog: {},     // { 'A0': 512, ... }
        i2c: { sda: null, scl: null, status: null, devices: [] },
        clock: { freq: null, status: null }
      },

      diagTimeout: null,

      // Defined Pins for Matrix
      digitalPins: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
      analogPins: ['A0', 'A1', 'A2', 'A3', 'A4', 'A5']
    };
  },

  computed: {
    getRamClass() {
      if (!this.diagState.ram.free) return '';
      if (this.diagState.ram.free > 500) return 'text-emerald';
      if (this.diagState.ram.free > 200) return 'text-amber';
      return 'text-rose';
    },
    getVccClass() {
      if (this.diagState.vcc.volts === null) return '';
      const v = this.diagState.vcc.volts;
      if (v >= 4.5 && v <= 5.5) return 'text-emerald';
      if (v >= 3.0 && v < 4.5) return 'text-amber';
      return 'text-rose';
    }
  },

  mounted() {
    this.loadPresets();
  },

  methods: {
    t,
    // =========================================================================
    // Web Serial Connection
    // =========================================================================
    async toggleSerial() {
      if (this.isConnected) {
        await this.disconnectSerial();
      } else {
        await this.connectSerial();
      }
    },

    async connectSerial() {
      if (!('serial' in navigator)) {
        alert('A böngésződ nem támogatja a Web Serial API-t. Kérlek használj Chrome-ot vagy Edge-et! / Your browser does not support Web Serial API.');
        return;
      }

      this.resetDiagnosticState();
      this.diagState.status = 'IDLE';

      try {
        this.port = await navigator.serial.requestPort();
        await this.port.open({ baudRate: 115200 });
        this.isConnected = true;
        this.currentStep = 2;
        this.writeToLog('>> [KAPCSOLAT / CONNECTION] ' + (this.t('portConnected')) + ' @ 115200 baud.\n');
        this.readSerialLoop();
      } catch (err) {
        console.error('Serial connection error:', err);
        this.writeToLog(`>> [HIBA / ERROR] ${err.message}\n`);
      }
    },

    async disconnectSerial() {
      this.isConnected = false;
      this.currentStep = 1;
      if (this.diagTimeout) {
        clearTimeout(this.diagTimeout);
        this.diagTimeout = null;
      }
      this.resetDiagnosticState();
      this.diagState.status = 'IDLE';
      this.digitalPins.forEach(p => (this.diagState.gpio[p] = null));

      if (this.reader) {
        try {
          await this.reader.cancel();
        } catch (e) {}
      }
      if (this.port) {
        try {
          await this.port.close();
        } catch (e) {}
      }
      this.port = null;
      this.writeToLog('>> [KAPCSOLAT / CONNECTION] ' + (this.t('portDisconnected')) + '.\n');
    },

    async pauseSerialReader() {
      this.isPausedForFlashing = true;
      if (this.reader) {
        try {
          await this.reader.cancel();
        } catch (_) {}
      }
      // Small pause to guarantee lock is released
      await new Promise(r => setTimeout(r, 60));
    },

    resumeSerialReader() {
      this.isPausedForFlashing = false;
      if (this.isConnected && this.port && this.port.readable) {
        this.readSerialLoop();
      }
    },

    async readSerialLoop() {
      let buffer = '';
      while (this.port && this.port.readable && this.isConnected && !this.isPausedForFlashing) {
        try {
          this.reader = this.port.readable.getReader();
          while (true) {
            const { value, done } = await this.reader.read();
            if (done) break;

            const chunk = new TextDecoder().decode(value);
            this.writeToLog(chunk);
            buffer += chunk;

            // Process full lines
            while (buffer.includes('\n')) {
              const lineIndex = buffer.indexOf('\n');
              const line = buffer.substring(0, lineIndex).trim();
              buffer = buffer.substring(lineIndex + 1);

              if (line) {
                this.parseDiagnosticLine(line);
              }
            }
          }
        } catch (error) {
          if (this.isConnected && !this.isPausedForFlashing) {
            console.error('Serial stream read error:', error);
          }
        } finally {
          if (this.reader) {
            try {
              this.reader.releaseLock();
            } catch (_) {}
            this.reader = null;
          }
        }
      }
    },

    writeToLog(text) {
      this.serialLog += text;
      if (this.autoScroll) {
        this.$nextTick(() => {
          const el = this.$refs.consoleOutput;
          if (el) el.scrollTop = el.scrollHeight;
        });
      }
    },

    clearLog() {
      this.serialLog = '';
    },

    async sendCustomCommand() {
      if (!this.customCommand || !this.isConnected || this.isFlashing) return;
      await this.sendSerialText(this.customCommand);
      this.customCommand = '';
    },

    async sendSerialText(text) {
      if (!this.port || !this.port.writable) return;
      const writer = this.port.writable.getWriter();
      try {
        const encoder = new TextEncoder();
        await writer.write(encoder.encode('\n' + text.trim() + '\n'));
      } finally {
        writer.releaseLock();
      }
    },

    // =========================================================================
    // Stage 1: Diagnostic Parser & Protocol Handler
    // =========================================================================
    resetDiagnosticState() {
      if (this.diagTimeout) {
        clearTimeout(this.diagTimeout);
        this.diagTimeout = null;
      }
      this.diagState = {
        status: 'IDLE',
        result: null,
        totalChecks: 0,
        failedChecks: 0,
        ram: { free: null, total: 2048, status: null },
        vcc: { volts: null, status: null },
        gpio: {},
        analog: {},
        i2c: { sda: null, scl: null, status: null, devices: [] },
        clock: { freq: null, status: null }
      };
    },

    async startDiagnostics(simulateFault = false) {
      if (!this.isConnected) {
        alert(t('msgPortError'));
        return;
      }

      this.resetDiagnosticState();
      this.diagState.status = 'RUNNING';
      this.digitalPins.forEach(p => (this.diagState.gpio[p] = 'TESTING'));

      this.writeToLog(`\n>> [DIAGNOSTICS] Starting suite (Simulate fault: ${simulateFault})...\n`);

      // Watchdog timer: If device doesn't respond within 5 seconds, recover safely
      this.diagTimeout = setTimeout(() => {
        if (this.diagState.status === 'RUNNING') {
          this.diagState.status = 'IDLE';
          this.digitalPins.forEach(p => (this.diagState.gpio[p] = null));
          this.writeToLog('>> [TIMEOUT] Nem érkezett válasz a mikrokontrollertől. Próbáld újra!\n');
        }
      }, 5000);

      const cmd = simulateFault ? 'CMD:SIM_FAULT' : 'CMD:DIAG_START';
      await this.sendSerialText(cmd);
    },

    parseDiagnosticLine(line) {
      if (!line.startsWith('[DIAG:')) return;

      const content = line.substring(6, line.length - 1);
      const parts = content.split(':');
      const category = parts[0];
      const paramsStr = parts.slice(1).join(':');

      const params = {};
      paramsStr.split(';').forEach(pair => {
        const [k, v] = pair.split('=');
        if (k) params[k.trim()] = v ? v.trim() : true;
      });

      if (category === 'START') {
        this.resetDiagnosticState();
        this.diagState.status = 'RUNNING';
      } else if (category === 'RAM') {
        this.diagState.ram.free = parseInt(params.FREE, 10);
        this.diagState.ram.total = parseInt(params.TOTAL || '2048', 10);
        this.diagState.ram.status = params.STATUS || 'OK';
      } else if (category === 'VCC') {
        this.diagState.vcc.volts = parseFloat(params.VOLTS);
        this.diagState.vcc.status = params.STATUS || 'OK';
      } else if (category === 'GPIO') {
        const pin = parseInt(params.PIN, 10);
        this.diagState.gpio[pin] = params.STATE || params.STATUS || 'OK';
      } else if (category === 'ANALOG') {
        const pin = params.PIN;
        this.diagState.analog[pin] = parseInt(params.RAW, 10);
      } else if (category === 'I2C') {
        this.diagState.i2c.status = `${params.SDA || 'OK'}/${params.SCL || 'OK'}`;
      } else if (category === 'I2C_DEV') {
        if (params.ADDR) this.diagState.i2c.devices.push(params.ADDR);
      } else if (category === 'CLOCK') {
        this.diagState.clock.freq = params.FREQ || '16 MHz';
        this.diagState.clock.status = params.STATUS || 'OK';
      } else if (category === 'COMPLETE') {
        if (this.diagTimeout) {
          clearTimeout(this.diagTimeout);
          this.diagTimeout = null;
        }
        this.diagState.status = 'COMPLETED';
        this.diagState.result = params.RESULT === 'PASS' ? 'PASS' : 'FAIL';
        this.diagState.totalChecks = parseInt(params.CHECKS || '21', 10);
        this.diagState.failedChecks = parseInt(params.FAILED || '0', 10);

        if (this.diagState.result === 'PASS') {
          this.currentStep = 3;
        }
      }
    },

    getPinBadgeClass(pin) {
      const state = this.diagState.gpio[pin];
      if (!state) return 'pin-idle';
      if (state === 'TESTING') return 'pin-testing pulse';
      if (state === 'OK') return 'pin-pass';
      return 'pin-fail';
    },

    getPinStateText(pin) {
      const state = this.diagState.gpio[pin];
      if (!state) return t('pinStateIdle');
      if (state === 'TESTING') return t('pinStateTesting');
      if (state === 'OK') return 'OK';
      return state;
    },

    getAnalogPinBadgeClass(aPin) {
      const val = this.diagState.analog[aPin];
      if (val === undefined) return 'pin-idle';
      return 'pin-pass';
    },

    getAnalogPinStateText(aPin) {
      const val = this.diagState.analog[aPin];
      if (val === undefined) return t('pinStateIdle');
      return `${val} (OK)`;
    },

    // =========================================================================
    // Stage 2: Target Firmware Flashing (STK500 Bootloader Protocol)
    // =========================================================================
    async runTwoStageVerificationAndFlash() {
      if (!this.isConnected || !this.port) {
        this.flashMessage = t('msgPortError');
        this.isError = true;
        return;
      }
      if (!this.firmwareFile && !this.loadedFirmwareUrl) {
        this.flashMessage = t('msgSelectHexError');
        this.isError = true;
        return;
      }

      this.writeToLog('\n========================================================\n');
      this.writeToLog('>> [2-STAGE VERIFICATION] Stage 1: Initiating Hardware Self-Test...\n');

      // 1. Fázis: Diagnosztika futtatása
      await this.startDiagnostics(false);

      const startTime = Date.now();
      const waitForDiag = () =>
        new Promise(resolve => {
          const checkInterval = setInterval(() => {
            if (this.diagState.status === 'COMPLETED' || Date.now() - startTime > 8000) {
              clearInterval(checkInterval);
              resolve();
            }
          }, 150);
        });

      await waitForDiag();

      if (this.diagState.result !== 'PASS') {
        this.flashMessage = t('msgDiagHaltError');
        this.isError = true;
        this.writeToLog('>> [SAFETY INTERLOCK] Flashing blocked due to hardware fault!\n');
        return;
      }

      // 2. Fázis: Target Firmware égetése STK500 protokollal
      this.writeToLog('>> [2-STAGE VERIFICATION] Stage 2: Hardware verified, flashing target firmware via STK500...\n');
      await this.flashTargetFirmwareDirectly();
    },

    async flashTargetFirmwareDirectly() {
      if (!this.isConnected || !this.port) {
        this.flashMessage = t('msgPortError');
        this.isError = true;
        return;
      }
      if (!this.firmwareFile && !this.loadedFirmwareUrl) {
        this.flashMessage = t('msgSelectHexError');
        this.isError = true;
        return;
      }

      this.isFlashing = true;
      this.isFlashingDone = false;
      this.flashProgress = 0;
      this.flashMessage = t('badgeFlashing');
      this.isError = false;

      try {
        let hexText;
        if (this.firmwareFile) {
          hexText = await this.firmwareFile.text();
        } else if (this.loadedFirmwareUrl) {
          const response = await fetch(`http://127.0.0.1:8000${this.loadedFirmwareUrl}`);
          hexText = await response.text();
        }

        await this.pauseSerialReader();

        this.writeToLog('\n>> [STK500] Initializing Optiboot bootloader flasher...\n');

        const result = await flashFirmwareSTK500(this.port, hexText, {
          onProgress: (p) => {
            this.flashProgress = p.percent;
            if (p.phase === 'PROGRAMMING') {
              this.flashMessage = `${t('badgeFlashing')} (${p.current}/${p.total} pages - ${p.percent}%)`;
            }
          },
          onLog: (msg) => {
            this.writeToLog(msg + '\n');
          }
        });

        this.isFlashingDone = true;
        this.flashMessage = t('msgFlashSuccess');
        this.writeToLog('>> [FLASH SUCCESS] Target firmware active and running.\n');
      } catch (err) {
        console.error('Flashing error:', err);
        this.flashMessage = t('msgFlashError') + err.message;
        this.isError = true;
        this.writeToLog(`>> [FLASH ERROR] ${err.message}\n`);
      } finally {
        this.isFlashing = false;
        this.resumeSerialReader();
      }
    },

    // =========================================================================
    // Preset Management
    // =========================================================================
    handleFileChange(event) {
      this.firmwareFile = event.target.files[0];
      this.loadedFirmwareUrl = null;
      this.loadedPresetId = null;
    },

    clearLoadedFile() {
      this.loadedFirmwareUrl = null;
      this.firmwareFile = null;
      this.loadedPresetId = null;
      if (this.$refs.fileInput) this.$refs.fileInput.value = '';
    },

    getFilename(url) {
      if (!url) return '';
      return url.split('/').pop();
    },

    loadPresetToForm(preset) {
      this.presetName = preset.name;
      this.presetDescription = preset.description || '';
      this.loadedFirmwareUrl = preset.firmware_file;
      this.loadedPresetId = preset.id;
      this.firmwareFile = null;
      this.flashMessage = t('msgPresetLoaded', preset.name);
      this.isError = false;
    },

    async savePreset() {
      if (!this.firmwareFile) {
        this.flashMessage = t('msgFileRequired');
        this.isError = true;
        return;
      }
      if (!this.presetName) {
        this.flashMessage = t('msgNameRequired');
        this.isError = true;
        return;
      }

      this.isUploading = true;
      this.flashMessage = '';

      const formData = new FormData();
      formData.append('name', this.presetName);
      formData.append('description', this.presetDescription);
      formData.append('firmware_file', this.firmwareFile);

      const token = localStorage.getItem('user-token');
      try {
        await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Token ${token}`
          }
        });
        this.flashMessage = t('msgPresetSaved');
        this.isError = false;
        this.loadPresets();
      } catch (err) {
        this.flashMessage = t('msgPresetSaveError');
        this.isError = true;
      } finally {
        this.isUploading = false;
      }
    },

    async loadPresets() {
      const token = localStorage.getItem('user-token');
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/presets/', {
          headers: { Authorization: `Token ${token}` }
        });
        this.presets = response.data;
      } catch (err) {
        console.error('Presets loading error:', err);
      }
    },

    logout() {
      if (this.isConnected) {
        this.disconnectSerial();
      }
      localStorage.removeItem('user-token');
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
/* =========================================================================
   Layout & Container Styles
   ========================================================================= */
.dashboard-container {
  width: 100%;
  max-width: 1320px;
  margin: 0 auto;
  padding: 10px 20px 40px 20px;
  box-sizing: border-box;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 20px;
  align-items: start;
}

.main-column, .side-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Glassmorphism Cards */
.glass-card {
  background: rgba(17, 24, 39, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 22px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
}

/* =========================================================================
   Header & Workflow Stepper
   ========================================================================= */
.header-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

h2 {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 700;
  color: #f3f4f6;
  letter-spacing: -0.3px;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 0.88rem;
  color: #94a3b8;
}

.port-connection-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.linux-hint {
  font-size: 0.72rem;
  color: #64748b;
  line-height: 1.2;
}

.port-connection-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #1e293b;
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid #334155;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #64748b;
  transition: all 0.3s ease;
}
.status-indicator.online {
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
}
.status-indicator.offline {
  background: #ef4444;
}

.status-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
}

.btn-port {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-port:hover {
  background: #2563eb;
}
.btn-port.connected {
  background: #dc2626;
}
.btn-port.connected:hover {
  background: #b91c1c;
}

/* Stepper Bar */
.stepper-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #0f172a;
  padding: 12px 20px;
  border-radius: 10px;
  border: 1px solid #1e293b;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  opacity: 0.5;
  transition: all 0.3s ease;
}
.step-item.active { opacity: 1; }
.step-item.current .step-circle {
  background: #3b82f6;
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.6);
}
.step-item.done .step-circle {
  background: #10b981;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
}
.step-item.failed .step-circle {
  background: #ef4444;
}

.step-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #334155;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 800;
}

.step-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #e2e8f0;
}

.step-divider {
  flex-grow: 1;
  height: 2px;
  background: #334155;
  margin: 0 15px;
  transition: all 0.3s ease;
}
.step-divider.filled {
  background: #10b981;
}

/* =========================================================================
   STAGE 1: Diagnostic HUD Styles
   ========================================================================= */
.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 10px;
}

h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #f1f5f9;
}

.badge {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.badge-idle { background: #334155; color: #94a3b8; }
.badge-running { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
.badge-success { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
.badge-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }

.diag-action-bar {
  display: flex;
  gap: 8px;
}

.btn-sub {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s ease;
}
.btn-diag { background: #0284c7; color: white; }
.btn-diag:hover:not(:disabled) { background: #0369a1; }
.btn-fault { background: #475569; color: #f1f5f9; }
.btn-fault:hover:not(:disabled) { background: #334155; }
.btn-sub:disabled { opacity: 0.5; cursor: not-allowed; }

/* Telemetry Gauges */
.telemetry-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.telemetry-box {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 10px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.telemetry-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 4px;
}

.telemetry-val {
  font-size: 1.18rem;
  font-weight: 800;
  color: #f8fafc;
  font-family: monospace;
}

.telemetry-sub {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 4px;
}

.text-emerald { color: #34d399; }
.text-amber { color: #fbbf24; }
.text-rose { color: #f87171; }
.text-cyan { color: #38bdf8; }
.text-violet { color: #a78bfa; }

.progress-bar-bg {
  width: 100%;
  height: 4px;
  background: #1e293b;
  border-radius: 2px;
  margin-top: 6px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: #10b981;
  transition: width 0.3s ease;
}

/* Pin Matrix */
.pin-matrix-container {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 10px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.matrix-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #cbd5e1;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.pin-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.group-tag {
  font-size: 0.72rem;
  color: #64748b;
  font-weight: 600;
}

.pins-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.pin-badge {
  padding: 4px 8px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 48px;
  font-family: monospace;
  transition: all 0.2s ease;
}
.pin-num { font-size: 0.75rem; font-weight: 700; }
.pin-state { font-size: 0.65rem; }

.pin-idle { background: #1e293b; color: #64748b; }
.pin-testing { background: #172554; color: #60a5fa; border: 1px solid #3b82f6; }
.pin-pass { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
.pin-fail { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }

/* Alert Banner */
.diag-banner {
  margin-top: 15px;
  padding: 12px 16px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.pass-banner { background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981; color: #34d399; }
.fail-banner { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #f87171; }
.banner-icon { display: flex; align-items: center; justify-content: center; }
.banner-status-svg { width: 22px; height: 22px; }
.banner-text strong { display: block; font-size: 0.92rem; margin-bottom: 2px; }
.banner-text p { margin: 0; font-size: 0.8rem; opacity: 0.9; }

/* =========================================================================
   STAGE 2: Flash Form & Flashing Controls
   ========================================================================= */
.flash-card {
  display: flex;
  flex-direction: column;
}

.flash-form-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #cbd5e1;
}

.form-row-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.text-input {
  background: #0f172a;
  border: 1px solid #334155;
  padding: 10px 12px;
  border-radius: 8px;
  color: white;
  font-size: 0.88rem;
}
.text-input:focus { outline: none; border-color: #3b82f6; }

.file-input-hidden { display: none; }

.file-upload-dropzone {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px;
  background: #0f172a;
  border: 2px dashed #334155;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.88rem;
  color: #94a3b8;
  transition: all 0.2s ease;
}
.file-upload-dropzone:hover {
  border-color: #3b82f6;
  color: #e2e8f0;
  background: #172554;
}

.upload-icon-svg {
  width: 24px;
  height: 24px;
  color: #94a3b8;
}

.loaded-firmware-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1e293b;
  border: 1px solid #3b82f6;
  padding: 10px 14px;
  border-radius: 8px;
}
.file-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.88rem;
  color: #f1f5f9;
}
.file-icon-svg {
  width: 20px;
  height: 20px;
  color: #60a5fa;
}
.file-name { color: #94a3b8; font-size: 0.82rem; }

.btn-text-clear {
  background: transparent;
  border: none;
  color: #f87171;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-text-clear:hover { text-decoration: underline; }

/* Flashing Progress Bar */
.flashing-progress-box {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.flashing-progress-bar-bg {
  width: 100%;
  height: 6px;
  background: #1e293b;
  border-radius: 3px;
  overflow: hidden;
}
.flashing-progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  transition: width 0.2s ease;
}
.flashing-progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.76rem;
  color: #94a3b8;
  font-weight: 600;
}

/* Master Action Buttons */
.master-action-row {
  display: grid;
  grid-template-columns: 2fr 1.2fr 1fr;
  gap: 12px;
}

.btn-master {
  padding: 12px 16px;
  border-radius: 10px;
  border: none;
  font-size: 0.92rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.btn-master:hover:not(:disabled) {
  transform: translateY(-1px);
}
.btn-master:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-primary-two-stage {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}
.btn-primary-two-stage:hover:not(:disabled) {
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45);
}

.btn-direct-flash {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.25);
}
.btn-save-preset {
  background: #334155;
  color: #e2e8f0;
}
.btn-save-preset:hover:not(:disabled) { background: #475569; }

.feedback-msg {
  margin: 14px 0 0 0;
  font-size: 0.88rem;
  font-weight: 600;
}
.msg-success { color: #34d399; }
.msg-error { color: #f87171; }

/* =========================================================================
   Serial Monitor Console
   ========================================================================= */
.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.monitor-title-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #64748b;
}
.live-dot.live-active {
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.monitor-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-icon {
  background: #1e293b;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.78rem;
  cursor: pointer;
}
.btn-icon:hover { background: #334155; }

.autoscroll-toggle {
  font-size: 0.78rem;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.console-wrapper {
  background: #000;
  border: 1px solid #1e293b;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 10px;
}

.monitor-console {
  width: 100%;
  height: 160px;
  background: #000;
  color: #34d399;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.82rem;
  line-height: 1.45;
  border: none;
  padding: 12px;
  resize: none;
  box-sizing: border-box;
}
.monitor-console:focus { outline: none; }

.command-bar {
  display: flex;
  gap: 8px;
}

.command-input {
  flex-grow: 1;
  padding: 8px 12px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  color: #f1f5f9;
  font-family: monospace;
  font-size: 0.82rem;
}
.command-input:focus { outline: none; border-color: #3b82f6; }

.btn-send-cmd {
  background: #2563eb;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-send-cmd:disabled { opacity: 0.5; cursor: not-allowed; }

/* =========================================================================
   Right Column (Presets & Profile)
   ========================================================================= */
.user-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 38px;
  height: 38px;
  background: #1e293b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.user-svg {
  width: 20px;
  height: 20px;
  color: #94a3b8;
}

.user-info h4 {
  margin: 0;
  font-size: 0.95rem;
  color: #f1f5f9;
}

.user-status-pill {
  font-size: 0.72rem;
  color: #34d399;
  background: rgba(16, 185, 129, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
}

.btn-logout {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-logout:hover {
  background: #dc2626;
  color: white;
}

/* Presets List */
.presets-card {
  display: flex;
  flex-direction: column;
}

.preset-count-badge {
  background: #334155;
  color: #94a3b8;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.presets-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 420px;
  overflow-y: auto;
  padding-right: 4px;
}
.presets-list::-webkit-scrollbar { width: 5px; }
.presets-list::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }

.preset-item-card {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all 0.2s ease;
}
.preset-item-card:hover {
  border-color: #3b82f6;
  background: #172554;
}
.preset-item-card.active-preset {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.08);
}

.preset-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.preset-title {
  color: #f1f5f9;
  font-size: 0.88rem;
}
.preset-date {
  font-size: 0.72rem;
  color: #64748b;
}

.preset-desc {
  margin: 0;
  font-size: 0.78rem;
  color: #94a3b8;
  line-height: 1.35;
}

.preset-footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 4px;
}

.firmware-tag {
  font-size: 0.7rem;
  color: #a855f7;
  background: rgba(168, 85, 247, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.btn-load-preset {
  background: #334155;
  color: #e2e8f0;
  border: none;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-load-preset:hover { background: #475569; }

.empty-presets-state {
  text-align: center;
  padding: 30px 10px;
  color: #64748b;
}
.empty-icon {
  margin-bottom: 8px;
  display: flex;
  justify-content: center;
}
.empty-svg {
  width: 38px;
  height: 38px;
  color: #475569;
}
.empty-presets-state p { margin: 0; font-size: 0.88rem; color: #94a3b8; }
.empty-sub { font-size: 0.76rem; display: block; margin-top: 4px; }

/* Guide Card */
.guide-card h4 {
  margin: 0 0 10px 0;
  font-size: 0.88rem;
  color: #e2e8f0;
}
.guide-list {
  margin: 0;
  padding-left: 18px;
  font-size: 0.78rem;
  color: #94a3b8;
  line-height: 1.5;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.guide-list strong { color: #cbd5e1; }

/* =========================================================================
   Responsive Breakpoints
   ========================================================================= */
@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .telemetry-grid {
    grid-template-columns: 1fr 1fr;
  }
  .master-action-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .telemetry-grid {
    grid-template-columns: 1fr;
  }
  .form-row-2col {
    grid-template-columns: 1fr;
  }
  .stepper-bar {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  .step-divider { display: none; }
  .port-connection-wrapper { align-items: flex-start; }
}
</style>
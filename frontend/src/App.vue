<template>
  <div id="app">
    <header class="app-topbar">
      <div class="topbar-container">

        <!-- Brand Logo & Title -->
        <div class="logo-group">
          <div class="brand-icon-box">
            <svg class="brand-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
          </div>
          <div class="brand-text-block">
            <div class="brand-title-row">
              <h1 class="brand-title">{{ t('appTitle') }}</h1>
              <span class="version-tag">v2.0 • 2-Stage Diag</span>
            </div>
            <span class="brand-sub">{{ t('appSubtitle') }}</span>
          </div>
        </div>

        <!-- Sleek Language Switcher -->
        <div class="lang-switcher-container">
          <div class="lang-pill">
            <button
              type="button"
              class="lang-btn"
              :class="{ active: i18nState.currentLang === 'hu' }"
              @click="setLanguage('hu')"
            >
              <span class="lang-code">HU</span>
              <span class="lang-name">Magyar</span>
            </button>

            <button
              type="button"
              class="lang-btn"
              :class="{ active: i18nState.currentLang === 'en' }"
              @click="setLanguage('en')"
            >
              <span class="lang-code">EN</span>
              <span class="lang-name">English</span>
            </button>
          </div>
        </div>

      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script>
import { i18nState, setLanguage, t } from './i18n';

export default {
  setup() {
    return {
      i18nState,
      setLanguage,
      t
    };
  }
};
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  min-height: 100%;
}

body {
  background: #0b0f19;
  color: #f8fafc;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

#app {
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}

/* =========================================================================
   Top Bar Styles
   ========================================================================= */
.app-topbar {
  width: 100%;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}

.topbar-container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

/* Logo & Brand text */
.logo-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #10b981, #0284c7);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
  flex-shrink: 0;
}

.brand-svg {
  width: 22px;
  height: 22px;
  color: #ffffff;
  fill: #ffffff;
}

.brand-text-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -0.4px;
}

.version-tag {
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.brand-sub {
  font-size: 0.78rem;
  color: #94a3b8;
}

/* Language Switcher Pill */
.lang-switcher-container {
  display: flex;
  align-items: center;
}

.lang-pill {
  display: flex;
  align-items: center;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 3px;
  gap: 2px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

.lang-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 6px 14px;
  border-radius: 7px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.lang-code {
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.lang-name {
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 0.85;
}

.lang-btn:hover {
  color: #e2e8f0;
}

.lang-btn.active {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.4);
}

.lang-btn.active .lang-name {
  opacity: 1;
}

/* App Main */
.app-main {
  flex-grow: 1;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

@media (max-width: 768px) {
  .topbar-container {
    padding: 10px 16px;
  }
  .brand-sub {
    display: none;
  }
  .version-tag {
    display: none;
  }
  .lang-name {
    display: none;
  }
  .lang-btn {
    padding: 6px 10px;
  }
}
</style>
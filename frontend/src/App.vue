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
            </div>
            <span class="brand-sub">{{ t('appSubtitle') }}</span>
          </div>
        </div>

        <!-- Theme & Language Switcher -->
        <div class="lang-switcher-container">
          <!-- Theme Toggle Pill -->
          <button
            type="button"
            class="theme-toggle-btn"
            @click="toggleTheme"
            :title="t('themeToggleTitle')"
          >
            <!-- Sun Icon (when in Light Mode) -->
            <svg v-if="theme === 'light'" class="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            <!-- Moon Icon (when in Dark Mode) -->
            <svg v-else class="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
            <span class="theme-label">{{ theme === 'light' ? t('themeLight') : t('themeDark') }}</span>
          </button>

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
import { ref, onMounted } from 'vue';
import { i18nState, setLanguage, t } from './i18n';

export default {
  setup() {
    const theme = ref(localStorage.getItem('app-theme') || 'dark');

    const applyTheme = (val) => {
      document.documentElement.setAttribute('data-theme', val);
      localStorage.setItem('app-theme', val);
    };

    const toggleTheme = () => {
      theme.value = theme.value === 'dark' ? 'light' : 'dark';
      applyTheme(theme.value);
    };

    onMounted(() => {
      applyTheme(theme.value);
    });

    return {
      i18nState,
      setLanguage,
      t,
      theme,
      toggleTheme
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
  background: var(--bg-page);
  color: var(--text-primary);
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
  background: var(--bg-topbar);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-card);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-topbar);
  transition: background-color 0.2s ease, border-color 0.2s ease;
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
  padding: 0;
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.4px;
}

.brand-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
}

/* Theme & Language Switcher */
.lang-switcher-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-surface);
  border: 1px solid var(--border-control);
  color: var(--text-secondary);
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-inset);
}

.theme-toggle-btn:hover {
  border-color: #3b82f6;
  color: var(--text-primary);
}

.theme-icon {
  width: 16px;
  height: 16px;
  color: #f59e0b;
}

:root:not([data-theme="light"]) .theme-icon {
  color: #38bdf8;
}

.lang-pill {
  display: flex;
  align-items: center;
  background: var(--bg-surface);
  border: 1px solid var(--border-control);
  border-radius: 10px;
  padding: 3px;
  gap: 2px;
  box-shadow: var(--shadow-inset);
}

.lang-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
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
  color: var(--text-primary);
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
  .lang-name,
  .theme-label {
    display: none;
  }
  .lang-btn {
    padding: 6px 10px;
  }
}
</style>

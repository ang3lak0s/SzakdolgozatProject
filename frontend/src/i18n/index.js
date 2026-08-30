import { reactive } from 'vue';
import { translations } from './translations';

const savedLang = localStorage.getItem('app-lang') || 'hu';

export const i18nState = reactive({
  currentLang: savedLang === 'en' ? 'en' : 'hu'
});

export function setLanguage(lang) {
  if (translations[lang]) {
    i18nState.currentLang = lang;
    localStorage.setItem('app-lang', lang);
  }
}

export function t(key, ...args) {
  const lang = i18nState.currentLang;
  const dict = translations[lang] || translations.hu;
  const val = dict[key];

  if (typeof val === 'function') {
    return val(...args);
  }
  if (val !== undefined) {
    return val;
  }
  // Fallback to Hungarian or key
  const fallback = translations.hu[key];
  if (typeof fallback === 'function') {
    return fallback(...args);
  }
  return fallback !== undefined ? fallback : key;
}

export default {
  state: i18nState,
  setLanguage,
  t
};

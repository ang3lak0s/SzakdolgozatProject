<template>
  <div class="login-container">
    <div class="card glass-card">
      <h2>{{ t('loginTitle') }}</h2>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <input v-model="username" type="text" :placeholder="t('usernamePlaceholder')" required>
        </div>

        <div class="input-group">
          <input v-model="password" type="password" :placeholder="t('passwordPlaceholder')" required>
        </div>

        <button type="submit" :disabled="isLoading">
          {{ isLoading ? '...' : t('loginBtn') }}
        </button>
      </form>

      <p
        v-if="message"
        :class="{
          success: isSuccess,
          error: !isSuccess
        }"
      >
        {{ message }}
      </p>

      <button class="link-btn" @click="$router.push('/register')">
        {{ t('noAccountLink') }}
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { t } from '../i18n';

export default {
  data() {
    return {
      username: '',
      password: '',
      message: '',
      isSuccess: false,
      isLoading: false
    };
  },
  methods: {
    t,
    async handleLogin() {
      this.isLoading = true;
      this.message = '';
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/login/', {
          username: this.username,
          password: this.password
        });

        const token = response.data.token;
        localStorage.setItem('user-token', token);

        this.isSuccess = true;
        this.message = t('loginSuccess');

        setTimeout(() => {
          this.$router.push('/dashboard');
        }, 500);
      } catch (error) {
        this.isSuccess = false;
        this.message = t('loginFailed');
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  box-sizing: border-box;
}

.glass-card {
  background: rgba(17, 24, 39, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 34px;
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
  text-align: center;
}

h2 {
  margin: 0 0 25px 0;
  color: #f1f5f9;
  font-size: 1.5rem;
  font-weight: 700;
}

form {
  width: 100%;
}

.input-group {
  margin-bottom: 16px;
}

input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #fff;
  font-size: 0.92rem;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

input::placeholder {
  color: #64748b;
}

input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}

button[type="submit"] {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
}

button[type="submit"]:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(16, 185, 129, 0.45);
}

button[type="submit"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.link-btn {
  background: transparent;
  border: none;
  box-shadow: none;
  margin-top: 18px;
  color: #60a5fa;
  font-size: 0.88rem;
  cursor: pointer;
}

.link-btn:hover {
  text-decoration: underline;
}

p {
  margin-top: 15px;
  font-size: 0.88rem;
  font-weight: 600;
}

.success {
  color: #34d399;
}

.error {
  color: #f87171;
}
</style>
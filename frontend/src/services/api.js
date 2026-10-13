import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Projects
  async getProjects() {
    const res = await apiClient.get('/projects');
    return res.data;
  },

  async getProject(id) {
    const res = await apiClient.get(`/projects/${id}`);
    return res.data;
  },

  async createProject(data) {
    const res = await apiClient.post('/projects', data);
    return res.data;
  },

  async updateProject(id, data) {
    const res = await apiClient.put(`/projects/${id}`, data);
    return res.data;
  },

  async deleteProject(id) {
    const res = await apiClient.delete(`/projects/${id}`);
    return res.data;
  },

  // Generation
  async startGeneration(projectId) {
    const res = await apiClient.post(`/projects/${projectId}/generate`);
    return res.data;
  },

  async getGenerationStatus(projectId) {
    const res = await apiClient.get(`/projects/${projectId}/status`);
    return res.data;
  },

  async regenerateProject(projectId) {
    const res = await apiClient.post(`/projects/${projectId}/regenerate`);
    return res.data;
  },

  async regenerateScene(projectId, sceneId) {
    const res = await apiClient.post(`/projects/${projectId}/scenes/${sceneId}/regenerate`);
    return res.data;
  },

  // Settings
  async getSettings() {
    const res = await apiClient.get('/settings');
    return res.data;
  },

  async updateSettings(data) {
    const res = await apiClient.post('/settings', data);
    return res.data;
  },

  // Media URLs
  getVideoUrl(projectId, version = null) {
    const v = version || Date.now();
    return `http://localhost:8000/api/projects/${projectId}/video?v=${v}`;
  },

  getThumbnailUrl(projectId, version = null) {
    const v = version || Date.now();
    return `http://localhost:8000/api/projects/${projectId}/thumbnail?v=${v}`;
  },

  getSceneVideoUrl(projectId, sceneId, version = null) {
    const v = version || Date.now();
    return `http://localhost:8000/api/projects/${projectId}/scenes/${sceneId}/video?v=${v}`;
  },

  getSceneThumbnailUrl(projectId, sceneId, version = null) {
    const v = version || Date.now();
    return `http://localhost:8000/api/projects/${projectId}/scenes/${sceneId}/thumbnail?v=${v}`;
  },

  // Real-time WebSocket connection
  connectWebSocket(onMessage, onOpen, onClose) {
    const wsUrl = `ws://localhost:8000/api/ws/status`;
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('[WS] Connected to AI Content Studio status stream');
      if (onOpen) onOpen();
    };

    socket.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (onMessage) onMessage(parsed);
      } catch (err) {
        console.error('[WS] Error parsing message:', err);
      }
    };

    socket.onclose = () => {
      console.log('[WS] Disconnected');
      if (onClose) onClose();
    };

    socket.onerror = (err) => {
      console.warn('[WS] Error:', err);
    };

    return socket;
  }
};

export default api;

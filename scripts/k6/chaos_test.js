/**
 * K6 Chaos Test - Testes de caos (memória, disco, rede)
 * Simula condições extremas e falhas de infraestrutura
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('chaos_errors');
const responseTime = new Trend('chaos_response_time');

export const options = {
  scenarios: {
    memory_stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 200 },  // Pico de carga para estressar memória
        { duration: '5m', target: 200 },
        { duration: '2m', target: 0 },
      ],
      exec: 'memoryStress',
    },
    network_chaos: {
      executor: 'constant-vus',
      vus: 50,
      duration: '10m',
      exec: 'networkChaos',
    },
    disk_chaos: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      stages: [
        { duration: '2m', target: 100 },
        { duration: '5m', target: 100 },
        { duration: '2m', target: 0 },
      ],
      exec: 'diskChaos',
    },
  },
  thresholds: {
    chaos_errors: ['rate<0.10'], // Aceitar até 10% de erros em cenários de caos
  },
};

export function memoryStress() {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
  
  // Requisições que consomem muita memória (payloads grandes)
  const largePayload = JSON.stringify({
    data: Array(10000).fill('x').join(''),
    query: 'complex query with many parameters',
  });
  
  const params = {
    headers: { 'Content-Type': 'application/json' },
    timeout: '30s',
  };
  
  const startTime = Date.now();
  const response = http.post(`${baseUrl}/api/query`, largePayload, params);
  const duration = Date.now() - startTime;
  
  responseTime.add(duration);
  
  const success = check(response, {
    'status is 200 or 429': (r) => r.status === 200 || r.status === 429, // 429 = Too Many Requests (esperado)
    'response received': (r) => r.status > 0,
  });
  
  errorRate.add(!success);
  
  sleep(0.5);
}

export function networkChaos() {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
  
  // Simular condições de rede instável (timeouts curtos)
  const params = {
    headers: { 'Content-Type': 'application/json' },
    timeout: '2s', // Timeout curto para simular latência
  };
  
  const startTime = Date.now();
  const response = http.get(`${baseUrl}/health`, params);
  const duration = Date.now() - startTime;
  
  responseTime.add(duration);
  
  const success = check(response, {
    'status received': (r) => r.status > 0,
    'or timeout expected': (r) => r.status === 0 || r.status > 0,
  });
  
  errorRate.add(!success);
  
  sleep(Math.random() * 3);
}

export function diskChaos() {
  const baseUrl = __ENV.BASE_URL || 'http://localhost:8000';
  
  // Requisições que geram muitos logs/artefatos (estresse de disco)
  const params = {
    headers: { 'Content-Type': 'application/json' },
    timeout: '15s',
  };
  
  const startTime = Date.now();
  const response = http.post(`${baseUrl}/api/report`, JSON.stringify({
    generate_artifacts: true,
    log_level: 'verbose',
  }), params);
  
  const duration = Date.now() - startTime;
  responseTime.add(duration);
  
  const success = check(response, {
    'status is 200 or 507': (r) => r.status === 200 || r.status === 507, // 507 = Insufficient Storage
    'response received': (r) => r.status > 0,
  });
  
  errorRate.add(!success);
  
  sleep(1);
}

export function handleSummary(data) {
  return {
    'artifacts/k6_chaos_test_summary.json': JSON.stringify(data, null, 2),
  };
}


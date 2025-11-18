/**
 * K6 Load Test - Testes de carga sequencial e paralela
 * Simula múltiplos usuários fazendo requisições simultâneas
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// Métricas customizadas
const errorRate = new Rate("errors");
const responseTime = new Trend("response_time");
const requestCount = new Counter("requests");

export const options = {
  stages: [
    { duration: "5m", target: 10 }, // Ramp-up: 10 usuários em 5min
    { duration: "10m", target: 50 }, // Load: 50 usuários por 10min
    { duration: "5m", target: 100 }, // Stress: 100 usuários por 5min
    { duration: "10m", target: 50 }, // Ramp-down: voltar a 50
    { duration: "5m", target: 0 }, // Recovery: 0 usuários
  ],
  thresholds: {
    http_req_duration: ["p(95)<2000"], // 95% das requisições < 2s
    http_req_failed: ["rate<0.05"], // Taxa de erro < 5%
    errors: ["rate<0.05"],
  },
};

export default function () {
  const baseUrl = __ENV.BASE_URL || "http://localhost:8000";

  // Simular diferentes tipos de requisições
  const endpoints = [
    "/health",
    "/api/query",
    "/api/validate",
    "/api/gatekeeper",
  ];

  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  const url = `${baseUrl}${endpoint}`;

  const params = {
    headers: {
      "Content-Type": "application/json",
      "User-Agent": "k6-load-test",
    },
    timeout: "10s",
  };

  const startTime = Date.now();
  const response = http.get(url, params);
  const duration = Date.now() - startTime;

  requestCount.add(1);
  responseTime.add(duration);

  const success = check(response, {
    "status is 200": (r) => r.status === 200,
    "response time < 2s": (r) => r.timings.duration < 2000,
    "has response body": (r) => r.body.length > 0,
  });

  errorRate.add(!success);

  sleep(Math.random() * 2 + 1); // Espera aleatória entre 1-3s
}

export function handleSummary(data) {
  return {
    "artifacts/k6_load_test_summary.json": JSON.stringify(data, null, 2),
  };
}

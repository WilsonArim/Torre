import http from 'k6/http';
import { sleep } from 'k6';
export let options = { vus: 60, duration: '45m' };
export default function () {
  http.get(`${__ENV.TARGET_URL}/healthcheck`);
  sleep(1);
}

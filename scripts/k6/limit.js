import http from 'k6/http';
import { sleep } from 'k6';
export let options = { vus: 180, duration: '15m' };
export default function () {
  http.get(`${__ENV.TARGET_URL}/heavy-task`);
  sleep(1);
}

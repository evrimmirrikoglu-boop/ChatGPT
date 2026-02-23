const serverUrlInput = document.getElementById('serverUrl');
const tokenInput = document.getElementById('token');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');
const statusEl = document.getElementById('status');
const pad = document.getElementById('pad');
const sensitivityInput = document.getElementById('sensitivity');
const sensValue = document.getElementById('sensValue');
const invertScrollInput = document.getElementById('invertScroll');

const wsProtocol = location.protocol === 'https:' ? 'wss' : 'ws';
serverUrlInput.value = `${wsProtocol}://${location.hostname}:8766`;

let socket = null;
let connected = false;

let lastOneFinger = null;
let lastTwoFingerY = null;
let lastTwoFingerX = null;
let moveDx = 0;
let moveDy = 0;
let rafScheduled = false;
let touchStartTime = 0;
let touchStartFingerCount = 0;
let movedSinceTouchStart = false;
let lastTapTime = 0;

function setStatus(text, ok = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle('ok', ok);
}

function send(type, payload = {}, { allowBeforeAuth = false } = {}) {
  if ((!connected && !allowBeforeAuth) || socket?.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({ type, ...payload }));
}

function flushMove() {
  rafScheduled = false;
  if (!moveDx && !moveDy) return;
  send('move', { dx: moveDx, dy: moveDy });
  moveDx = 0;
  moveDy = 0;
}

function queueMove(dx, dy) {
  moveDx += dx;
  moveDy += dy;
  if (!rafScheduled) {
    rafScheduled = true;
    requestAnimationFrame(flushMove);
  }
}

connectBtn.addEventListener('click', () => {
  const serverUrl = serverUrlInput.value.trim();
  const token = tokenInput.value.trim();
  if (!serverUrl || !token) {
    setStatus('Sunucu ve token gerekli');
    return;
  }

  socket = new WebSocket(serverUrl);

  socket.addEventListener('open', () => {
    send('auth', { token }, { allowBeforeAuth: true });
    setStatus('Kimlik doğrulama...');
  });

  socket.addEventListener('message', (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === 'auth_ok') {
        connected = true;
        setStatus('Bağlandı', true);
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
      } else if (msg.type === 'auth_fail') {
        setStatus('Token hatalı');
      }
    } catch {
      setStatus('Mesaj çözümlenemedi');
    }
  });

  socket.addEventListener('close', () => {
    connected = false;
    setStatus('Bağlantı kapandı');
    connectBtn.disabled = false;
    disconnectBtn.disabled = true;
  });

  socket.addEventListener('error', () => {
    setStatus('Bağlantı hatası');
  });
});

disconnectBtn.addEventListener('click', () => {
  socket?.close();
});

sensitivityInput.addEventListener('input', () => {
  sensValue.textContent = Number(sensitivityInput.value).toFixed(2);
});

pad.addEventListener('touchstart', (event) => {
  event.preventDefault();
  pad.classList.add('active');
  touchStartTime = performance.now();
  touchStartFingerCount = event.touches.length;
  movedSinceTouchStart = false;

  if (event.touches.length === 1) {
    const t = event.touches[0];
    lastOneFinger = { x: t.clientX, y: t.clientY };
  }

  if (event.touches.length === 2) {
    const y = (event.touches[0].clientY + event.touches[1].clientY) / 2;
    const x = (event.touches[0].clientX + event.touches[1].clientX) / 2;
    lastTwoFingerY = y;
    lastTwoFingerX = x;
  }
}, { passive: false });

pad.addEventListener('touchmove', (event) => {
  event.preventDefault();
  const sensitivity = Number(sensitivityInput.value);

  if (event.touches.length === 1 && lastOneFinger) {
    const t = event.touches[0];
    const dx = (t.clientX - lastOneFinger.x) * sensitivity;
    const dy = (t.clientY - lastOneFinger.y) * sensitivity;
    if (Math.abs(dx) + Math.abs(dy) > 0.2) {
      movedSinceTouchStart = true;
      queueMove(dx, dy);
    }
    lastOneFinger = { x: t.clientX, y: t.clientY };
  }

  if (event.touches.length === 2 && lastTwoFingerY !== null && lastTwoFingerX !== null) {
    const y = (event.touches[0].clientY + event.touches[1].clientY) / 2;
    const x = (event.touches[0].clientX + event.touches[1].clientX) / 2;
    const invert = invertScrollInput.checked ? -1 : 1;
    const dy = (y - lastTwoFingerY) * 1.2 * invert;
    const dx = (x - lastTwoFingerX) * 1.2 * invert;

    if (Math.abs(dy) + Math.abs(dx) > 0.2) {
      movedSinceTouchStart = true;
      send('scroll', { dx, dy });
    }

    lastTwoFingerY = y;
    lastTwoFingerX = x;
  }
}, { passive: false });

pad.addEventListener('touchend', (event) => {
  event.preventDefault();
  if (event.touches.length === 0) {
    pad.classList.remove('active');
    lastOneFinger = null;
    lastTwoFingerY = null;
    lastTwoFingerX = null;

    const elapsed = performance.now() - touchStartTime;
    const quickTap = elapsed < 220 && !movedSinceTouchStart;

    if (quickTap) {
      const now = performance.now();
      const isDouble = now - lastTapTime < 280 && touchStartFingerCount === 1;

      if (touchStartFingerCount === 2) {
        send('click', { button: 'right' });
      } else if (isDouble) {
        send('double_click');
        lastTapTime = 0;
      } else {
        send('click', { button: 'left' });
        lastTapTime = now;
      }
    }
  }
}, { passive: false });

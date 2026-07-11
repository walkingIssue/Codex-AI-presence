const canvas = document.querySelector("#presenceCanvas");
const context = canvas.getContext("2d");
const stateLabel = document.querySelector("#presenceState");
const demoButton = document.querySelector("#demoButton");

let canvasWidth = 0;
let canvasHeight = 0;
let speakingUntil = 0;

function resizeCanvas() {
  const bounds = canvas.getBoundingClientRect();
  const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
  const nextWidth = Math.max(1, Math.round(bounds.width * pixelRatio));
  const nextHeight = Math.max(1, Math.round(bounds.height * pixelRatio));

  if (nextWidth !== canvas.width || nextHeight !== canvas.height) {
    canvas.width = nextWidth;
    canvas.height = nextHeight;
    canvasWidth = bounds.width;
    canvasHeight = bounds.height;
  }
}

function drawOrb(milliseconds) {
  resizeCanvas();

  const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
  const width = canvasWidth || canvas.clientWidth;
  const height = canvasHeight || canvas.clientHeight;
  const time = milliseconds / 1000;
  const isSpeaking = performance.now() < speakingUntil;
  const energy = isSpeaking ? 1 : 0.15;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.245;

  context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  context.clearRect(0, 0, width, height);
  context.save();
  context.translate(centerX, centerY);

  const glow = context.createRadialGradient(0, 0, radius * .2, 0, 0, radius * 2.1);
  glow.addColorStop(0, isSpeaking ? "rgba(143, 244, 228, .19)" : "rgba(143, 244, 228, .08)");
  glow.addColorStop(.45, "rgba(91, 156, 178, .045)");
  glow.addColorStop(1, "rgba(0, 0, 0, 0)");
  context.fillStyle = glow;
  context.beginPath();
  context.arc(0, 0, radius * 2.1, 0, Math.PI * 2);
  context.fill();

  const strandCount = 112;
  const pointCount = 28;
  for (let strand = 0; strand < strandCount; strand += 1) {
    const angle = (strand / strandCount) * Math.PI * 2;
    const strandPhase = strand * .37;
    const hue = 164 + Math.sin(strand * .17) * 34;
    const alpha = .13 + (strand % 5) * .025 + energy * .18;
    context.beginPath();

    for (let point = 0; point <= pointCount; point += 1) {
      const progress = point / pointCount;
      const radialWave = Math.sin(time * (isSpeaking ? 5.2 : 1.15) + strandPhase + progress * 7) * (isSpeaking ? 11 : 3.2) * progress;
      const slowWave = Math.sin(time * .8 + strandPhase * .4 + progress * 3) * 3;
      const distance = radius * (.34 + progress * .72) + radialWave + slowWave;
      const x = Math.cos(angle + Math.sin(time * .18 + strandPhase) * .018) * distance;
      const y = Math.sin(angle + Math.sin(time * .18 + strandPhase) * .018) * distance;

      if (point === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    }

    context.strokeStyle = `hsla(${hue}, 82%, ${isSpeaking ? 76 : 68}%, ${alpha})`;
    context.lineWidth = strand % 9 === 0 ? 1.35 : .65;
    context.stroke();
  }

  context.strokeStyle = isSpeaking ? "rgba(143, 244, 228, .42)" : "rgba(143, 244, 228, .2)";
  context.lineWidth = 1;
  context.beginPath();
  context.arc(0, 0, radius * (.97 + Math.sin(time * 1.5) * .012), 0, Math.PI * 2);
  context.stroke();

  const core = context.createRadialGradient(0, 0, 0, 0, 0, radius * .32);
  core.addColorStop(0, isSpeaking ? "rgba(224, 255, 247, .8)" : "rgba(190, 255, 239, .32)");
  core.addColorStop(.28, isSpeaking ? "rgba(143, 244, 228, .28)" : "rgba(143, 244, 228, .12)");
  core.addColorStop(1, "rgba(143, 244, 228, 0)");
  context.fillStyle = core;
  context.beginPath();
  context.arc(0, 0, radius * .32, 0, Math.PI * 2);
  context.fill();

  context.restore();
  stateLabel.innerHTML = `<span></span> ${isSpeaking ? "PLAYBACK" : "IDLE"}`;
  requestAnimationFrame(drawOrb);
}

demoButton.addEventListener("click", () => {
  speakingUntil = performance.now() + 5200;
});

window.addEventListener("resize", resizeCanvas);
requestAnimationFrame(drawOrb);

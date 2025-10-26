import epgData from './data/epg-data.json';
import type { EPGData, Channel, Program } from './types/epg';

const data = epgData as EPGData;

function renderSchedules(channels: Channel[], programs: Record<string, Program[]>): string {
  return channels
    .map((channel) => `
      <div class="channel-card">
        <div class="channel-header">
          ${
            channel.icon
              ? `<img src="${channel.icon}" alt="${channel.name}" width="26px" class="channel-icon" />`
              : '<div class="channel-icon-placeholder">📺</div>'
          }
          <h3 class="channel-name">${channel.name}</h3>
        </div>
        <div class="channel-stats">
          <span class="stat">
            Nombre de programme: ${programs[channel.id].length}
          </span>
        </div>
      </div>
    `)
    .join('');
}

function initApp() {
  const app = document.querySelector<HTMLDivElement>('#app')!;

  app.innerHTML = `
    <div class="container">
      <header class="header">
        <h1>📺 Guide TV</h1>
        <p class="subtitle">
          ${data.channels.length} chaînes
        </p>
      </header>

      <div class="channels-grid">
        ${renderSchedules(data.channels, data.programs)}
      </div>
    </div>
  `;
}

initApp();

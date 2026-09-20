/*
 * OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
 * Copyright (C) 2026 David Lopes (https://github.com/davdlic)
 * Licensed under the GNU General Public License v3.0 - see LICENSE
 *
 * Valve colours, kept in sync with coordinator.py:
 *   closed -> grey | opening -> pulsing orange | open -> orange | fault -> red
 */

// LitElement comes from the Home Assistant frontend, not a CDN: the card must
// work with the internet down.
const LitElement =
  window.LitElement ||
  Object.getPrototypeOf(
    customElements.get("ha-panel-lovelace") || customElements.get("hui-view")
  );
const html = LitElement.prototype.html;
const css = LitElement.prototype.css;

const CARD_VERSION = "1.0.0";

const VALVE_COLORS = {
  closed: "var(--oh-valve-closed)",
  opening: "var(--oh-valve-opening)",
  open: "var(--oh-valve-open)",
  fault: "var(--oh-valve-fault)",
};

const LABELS = {
  en: {
    card_title: "Heating",
    card_description:
      "Hydronic zone control with valve status, global modes and air purge.",
    empty:
      "No zones configured yet. Add them in Settings -> Devices & services -> OpenHydronic -> Configure.",
    summer: "Summer",
    holiday: "Holiday",
    air_purge: "Air purge",
    purge_left: (min) => `Purge ${min} min`,
    min_cycle: (min) => `minimum cycle ${min} min`,
    metrics: (hours, cycles) => `${hours} h - ${cycles} cycles`,
    editor_title: "Title",
    editor_zones: "Zones (empty = auto-detect)",
    editor_show_global: "Show global controls",
    editor_show_metrics: "Show per-zone metrics",
    fault: {
      sensor_stale: "Sensor not updating",
      sensor_missing: "Sensor unavailable",
      relay_missing: "Relay unavailable",
    },
    master: {
      disabled: "Master disabled",
      off: "Master off",
      waiting: "Thermal delay...",
      on: "Circulator running",
      purging: "Purging heat...",
    },
    system: {
      normal: "Normal",
      summer: "Summer",
      holiday: "Holiday",
      air_purge: "Air purge",
      anti_seize: "Anti-seize",
    },
  },
  pt: {
    card_title: "Climatização",
    card_description:
      "Controlo de zonas hidráulicas com estado das válvulas, modos globais e purga de ar.",
    empty:
      "Sem zonas configuradas. Adicione-as em Definições -> Dispositivos e serviços -> OpenHydronic -> Configurar.",
    summer: "Verão",
    holiday: "Férias",
    air_purge: "Purga de ar",
    purge_left: (min) => `Purga ${min} min`,
    min_cycle: (min) => `ciclo mínimo ${min} min`,
    metrics: (hours, cycles) => `${hours} h - ${cycles} ciclos`,
    editor_title: "Título",
    editor_zones: "Zonas (vazio = deteção automática)",
    editor_show_global: "Mostrar controlos globais",
    editor_show_metrics: "Mostrar métricas por zona",
    fault: {
      sensor_stale: "Sensor sem atualização",
      sensor_missing: "Sensor indisponível",
      relay_missing: "Relé indisponível",
    },
    master: {
      disabled: "Master desativado",
      off: "Master desligado",
      waiting: "Delay térmico…",
      on: "Circulador ativo",
      purging: "Purga térmica…",
    },
    system: {
      normal: "Normal",
      summer: "Verão",
      holiday: "Férias",
      air_purge: "Purga de ar",
      anti_seize: "Anti-gripagem",
    },
  },
};

/** Labels for a Home Assistant language code, English as fallback. */
function labels(language) {
  return LABELS[String(language || "en").slice(0, 2)] || LABELS.en;
}

class OpenHydronicCard extends LitElement {
  static get properties() {
    return { hass: {}, _config: {} };
  }

  static getStubConfig(hass) {
    const zones = Object.keys(hass.states).filter(
      (id) =>
        id.startsWith("climate.") &&
        hass.states[id].attributes.valve_state !== undefined
    );
    return {
      type: "custom:openhydronic-card",
      title: labels(hass.language).card_title,
      zones,
    };
  }

  static getConfigElement() {
    return document.createElement("openhydronic-card-editor");
  }

  setConfig(config) {
    this._config = {
      title: "OpenHydronic",
      show_global: true,
      show_metrics: false,
      ...config,
    };
  }

  getCardSize() {
    return 2 + Math.ceil(this._zones().length / 2);
  }

  /** Labels in the Home Assistant language. */
  get _l() {
    return labels(this.hass && this.hass.language);
  }

  /** Zones from the config, or auto-detected from the climate entities. */
  _zones() {
    if (!this.hass) return [];
    const ids =
      this._config.zones && this._config.zones.length
        ? this._config.zones
        : Object.keys(this.hass.states).filter(
            (id) =>
              id.startsWith("climate.") &&
              this.hass.states[id].attributes.valve_state !== undefined
          );
    return ids.map((id) => this.hass.states[id]).filter(Boolean);
  }

  /** Find a companion entity (switch/sensor) created by the integration. */
  _findEntity(domain, suffix) {
    if (this._config[suffix]) return this.hass.states[this._config[suffix]];
    const id = Object.keys(this.hass.states).find(
      (e) => e.startsWith(`${domain}.`) && e.includes(suffix)
    );
    return id ? this.hass.states[id] : undefined;
  }

  render() {
    if (!this.hass || !this._config) return html``;

    const l = this._l;
    const zones = this._zones();
    const summer = this._findEntity("switch", "summer_mode");
    const holiday = this._findEntity("switch", "holiday_mode");
    const purge = this._findEntity("switch", "air_purge");
    const master = this._findEntity("sensor", "master_state");
    const systemMode = zones.length
      ? zones[0].attributes.system_mode
      : undefined;

    return html`
      <ha-card class="glass">
        <div class="header">
          <div class="title">
            <ha-icon icon="mdi:heating-coil"></ha-icon>
            <span>${this._config.title}</span>
          </div>
          <div class="status">
            ${master
              ? html`<span class="pill master ${master.state}">
                  ${l.master[master.state] || master.state}
                </span>`
              : ""}
            ${systemMode && systemMode !== "normal"
              ? html`<span class="pill mode">
                  ${l.system[systemMode] || systemMode}
                </span>`
              : ""}
          </div>
        </div>

        ${this._config.show_global
          ? html`<div class="globals">
              ${this._globalButton(summer, "mdi:weather-sunny", l.summer)}
              ${this._globalButton(holiday, "mdi:bag-suitcase", l.holiday)}
              ${this._globalButton(purge, "mdi:air-filter", this._purgeLabel(purge))}
            </div>`
          : ""}

        <div class="zones">
          ${zones.length
            ? zones.map((zone) => this._renderZone(zone))
            : html`<div class="empty">${l.empty}</div>`}
        </div>
      </ha-card>
    `;
  }

  _purgeLabel(purge) {
    const l = this._l;
    if (!purge || purge.state !== "on") return l.air_purge;
    const remaining = purge.attributes.remaining_seconds || 0;
    return l.purge_left(Math.ceil(remaining / 60));
  }

  _globalButton(entity, icon, label) {
    if (!entity) return "";
    const active = entity.state === "on";
    return html`
      <button
        class="global ${active ? "active" : ""}"
        @click=${() => this._toggle(entity.entity_id)}
        title=${label}
      >
        <ha-icon icon=${icon}></ha-icon>
        <span>${label}</span>
      </button>
    `;
  }

  _renderZone(zone) {
    const l = this._l;
    const a = zone.attributes;
    const valve = a.valve_state || "closed";
    const fault = a.fault;
    const off = zone.state === "off";
    const current =
      a.current_temperature !== undefined && a.current_temperature !== null
        ? Number(a.current_temperature).toFixed(1)
        : "--";
    const target =
      a.temperature !== undefined && a.temperature !== null
        ? Number(a.temperature).toFixed(1)
        : "--";
    const locked = a.locked_until > 0;

    return html`
      <div class="zone ${off ? "disabled" : ""} ${a.is_bypass ? "bypass" : ""}">
        <div
          class="valve ${valve}"
          @click=${() => this._moreInfo(zone.entity_id)}
          title=${l.fault[fault] || valve}
        >
          ${this._valveIcon(valve)}
        </div>

        <div class="info" @click=${() => this._moreInfo(zone.entity_id)}>
          <div class="name">
            ${a.friendly_name || zone.entity_id}
            ${a.is_bypass ? html`<span class="tag">bypass</span>` : ""}
          </div>
          <div class="temps">
            <span class="current">${current}<small>°C</small></span>
            <span class="sep">→</span>
            <span class="target">${target}<small>°C</small></span>
          </div>
          <div class="sub">
            ${fault
              ? html`<span class="fault">${l.fault[fault] || fault}</span>`
              : locked
                ? html`<span class="lock">
                    <ha-icon icon="mdi:lock-clock"></ha-icon>
                    ${l.min_cycle(Math.ceil(a.locked_until / 60))}
                  </span>`
                : html`<span class="preset">${a.preset_mode || ""}</span>`}
            ${this._config.show_metrics
              ? html`<span class="metrics">
                  ${l.metrics(a.runtime_hours ?? 0, a.cycles ?? 0)}
                </span>`
              : ""}
          </div>
        </div>

        ${a.is_bypass
          ? ""
          : html`<div class="controls">
              <button @click=${() => this._nudge(zone, +0.5)}>
                <ha-icon icon="mdi:plus"></ha-icon>
              </button>
              <button @click=${() => this._nudge(zone, -0.5)}>
                <ha-icon icon="mdi:minus"></ha-icon>
              </button>
            </div>`}
      </div>
    `;
  }

  _valveIcon(valve) {
    const color = VALVE_COLORS[valve] || VALVE_COLORS.closed;
    return html`
      <svg viewBox="0 0 48 48" aria-hidden="true">
        <circle cx="24" cy="24" r="21" class="halo" fill=${color} />
        <path
          d="M24 6v9m0 18v9M6 24h9m18 0h9"
          stroke=${color}
          stroke-width="3"
          stroke-linecap="round"
          fill="none"
          opacity="0.55"
        />
        <circle cx="24" cy="24" r="10" fill=${color} />
        <path
          d="M19 24h10M24 19v10"
          stroke="rgba(255,255,255,0.9)"
          stroke-width="2.4"
          stroke-linecap="round"
        />
      </svg>
    `;
  }

  // -- actions -------------------------------------------------------
  _toggle(entityId) {
    this.hass.callService("switch", "toggle", { entity_id: entityId });
  }

  _nudge(zone, delta) {
    const base = Number(zone.attributes.temperature ?? 20);
    this.hass.callService("climate", "set_temperature", {
      entity_id: zone.entity_id,
      temperature: Math.round((base + delta) * 2) / 2,
    });
  }

  _moreInfo(entityId) {
    this.dispatchEvent(
      new CustomEvent("hass-more-info", {
        detail: { entityId },
        bubbles: true,
        composed: true,
      })
    );
  }

  static get styles() {
    return css`
      :host {
        --oh-valve-closed: #8a8f98;
        --oh-valve-opening: #ffa726;
        --oh-valve-open: #fb8c00;
        --oh-valve-fault: #e53935;
        --oh-glass-bg: rgba(255, 255, 255, 0.12);
        --oh-glass-border: rgba(255, 255, 255, 0.22);
        --oh-text: var(--primary-text-color);
      }

      ha-card.glass {
        padding: 16px;
        border-radius: 22px;
        background: linear-gradient(
          145deg,
          rgba(255, 255, 255, 0.14),
          rgba(255, 255, 255, 0.04)
        );
        backdrop-filter: blur(18px) saturate(140%);
        -webkit-backdrop-filter: blur(18px) saturate(140%);
        border: 1px solid var(--oh-glass-border);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
        color: var(--oh-text);
      }

      .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 14px;
      }
      .title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.25rem;
        font-weight: 600;
      }
      .status {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
      }
      .pill {
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 999px;
        background: var(--oh-glass-bg);
        border: 1px solid var(--oh-glass-border);
        white-space: nowrap;
      }
      .pill.master.on,
      .pill.master.purging {
        color: var(--oh-valve-open);
        border-color: var(--oh-valve-open);
      }
      .pill.master.waiting {
        color: var(--oh-valve-opening);
        border-color: var(--oh-valve-opening);
        animation: pulse 1.6s ease-in-out infinite;
      }

      .globals {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 8px;
        margin-bottom: 16px;
      }
      button.global {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 10px 8px;
        border-radius: 14px;
        border: 1px solid var(--oh-glass-border);
        background: var(--oh-glass-bg);
        color: inherit;
        font: inherit;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s ease;
      }
      button.global:hover {
        transform: translateY(-1px);
      }
      button.global.active {
        background: rgba(251, 140, 0, 0.25);
        border-color: var(--oh-valve-open);
        color: var(--oh-valve-open);
      }

      .zones {
        display: grid;
        gap: 10px;
      }
      .zone {
        display: grid;
        grid-template-columns: 52px 1fr auto;
        align-items: center;
        gap: 12px;
        padding: 10px 12px;
        border-radius: 16px;
        background: var(--oh-glass-bg);
        border: 1px solid var(--oh-glass-border);
      }
      .zone.disabled {
        opacity: 0.55;
      }
      .zone.bypass {
        border-style: dashed;
      }

      .valve {
        width: 48px;
        height: 48px;
        cursor: pointer;
      }
      .valve svg {
        width: 100%;
        height: 100%;
      }
      .valve .halo {
        opacity: 0.12;
      }
      .valve.opening svg {
        animation: pulse 1.2s ease-in-out infinite;
      }
      .valve.open .halo {
        opacity: 0.22;
      }

      .info {
        cursor: pointer;
        min-width: 0;
      }
      .name {
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .tag {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 1px 6px;
        border-radius: 6px;
        background: var(--oh-glass-bg);
        border: 1px solid var(--oh-glass-border);
      }
      .temps {
        display: flex;
        align-items: baseline;
        gap: 6px;
        font-size: 1.15rem;
      }
      .temps small {
        font-size: 0.7rem;
        opacity: 0.7;
      }
      .temps .sep {
        opacity: 0.5;
      }
      .temps .target {
        color: var(--oh-valve-open);
      }
      .sub {
        display: flex;
        gap: 10px;
        font-size: 0.75rem;
        opacity: 0.8;
        text-transform: capitalize;
      }
      .sub .fault {
        color: var(--oh-valve-fault);
        text-transform: none;
      }
      .sub .lock {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        text-transform: none;
      }
      .sub ha-icon {
        --mdc-icon-size: 14px;
      }

      .controls {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      .controls button {
        width: 34px;
        height: 28px;
        border-radius: 9px;
        border: 1px solid var(--oh-glass-border);
        background: var(--oh-glass-bg);
        color: inherit;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .controls ha-icon {
        --mdc-icon-size: 18px;
      }

      .empty {
        padding: 18px;
        text-align: center;
        font-size: 0.85rem;
        opacity: 0.75;
      }

      @keyframes pulse {
        0%,
        100% {
          opacity: 1;
        }
        50% {
          opacity: 0.35;
        }
      }

      @media (prefers-reduced-motion: reduce) {
        .valve.opening svg,
        .pill.master.waiting {
          animation: none;
        }
      }
    `;
  }
}

/** Minimal visual editor so the card is configurable from the UI. */
class OpenHydronicCardEditor extends LitElement {
  static get properties() {
    return { hass: {}, _config: {} };
  }

  setConfig(config) {
    this._config = config;
  }

  get _schema() {
    return [
      { name: "title", selector: { text: {} } },
      {
        name: "zones",
        selector: { entity: { domain: "climate", multiple: true } },
      },
      { name: "show_global", selector: { boolean: {} } },
      { name: "show_metrics", selector: { boolean: {} } },
    ];
  }

  render() {
    if (!this.hass || !this._config) return html``;
    return html`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._schema}
        .computeLabel=${(s) => {
          const l = labels(this.hass && this.hass.language);
          return (
            {
              title: l.editor_title,
              zones: l.editor_zones,
              show_global: l.editor_show_global,
              show_metrics: l.editor_show_metrics,
            }[s.name] || s.name
          );
        }}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `;
  }

  _valueChanged(ev) {
    const event = new CustomEvent("config-changed", {
      detail: { config: ev.detail.value },
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);
  }
}

customElements.define("openhydronic-card", OpenHydronicCard);
customElements.define("openhydronic-card-editor", OpenHydronicCardEditor);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "openhydronic-card",
  name: "OpenHydronic Card",
  description: labels(navigator.language).card_description,
  preview: true,
  documentationURL: "https://github.com/davdlic/OpenHydronic-HA",
});

console.info(
  `%c OPENHYDRONIC-CARD %c ${CARD_VERSION} `,
  "color:#fff;background:#fb8c00;font-weight:700;border-radius:4px 0 0 4px",
  "color:#fb8c00;background:#222;border-radius:0 4px 4px 0"
);

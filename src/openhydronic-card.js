/*
 * OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
 * Copyright (C) 2026 David Lopes (https://github.com/davdlic)
 * Licensed under the GNU General Public License v3.0 - see LICENSE
 *
 * Valve colours, kept in sync with coordinator.py:
 *   closed -> grey | opening -> pulsing orange | open -> orange | fault -> red
 */

// Lit is bundled, not fetched: the card works with the internet down. It is not taken
// from the Home Assistant frontend either, because Home Assistant imports this file
// at page start, before its own elements exist.
import { LitElement, html, css } from "lit";

const CARD_VERSION = "1.2.3";

// Material Design Icons paths, inlined so the card works offline.
const ICON_FIRE = "M17.66 11.2C17.43 10.9 17.15 10.64 16.89 10.38C16.22 9.78 15.46 9.35 14.82 8.72C13.33 7.26 13 4.85 13.95 3C13 3.23 12.17 3.75 11.46 4.32C8.87 6.4 7.85 10.07 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C6.87 12.33 6.69 10.28 7.45 8.64C5.78 10 4.87 12.3 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C18.86 17.66 19.5 15 18.56 12.72L18.43 12.46C18.22 12 17.66 11.2 17.66 11.2M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.78 14.43 12.46 13.77 12.33 13C12.21 12.26 12.23 11.63 12.5 10.94C12.69 11.32 12.89 11.7 13.13 12C13.9 13 15.11 13.44 15.37 14.8C15.41 14.94 15.43 15.08 15.43 15.23C15.46 16.05 15.1 16.95 14.5 17.5H14.5Z";
const ICON_FIRE_OFF = "M22.11 21.46L2.39 1.73L1.11 3L7.09 9C5.66 10.36 4.88 12.47 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C17.1 19.26 17.15 19.18 17.22 19.11L20.84 22.73L22.11 21.46M8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C7 12.47 6.74 10.69 7.26 9.15L8.58 10.47C8.58 11.4 8.73 12.33 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.66 15 12.66 14.76 12.64 14.53L15 16.88C14.85 17.11 14.69 17.33 14.5 17.5M18.92 15.72L9.65 6.46C10.12 5.65 10.72 4.92 11.46 4.32C12.17 3.75 13 3.23 13.95 3C13 4.85 13.33 7.26 14.82 8.72C15.46 9.35 16.22 9.78 16.89 10.38C17.15 10.64 17.43 10.9 17.66 11.2C17.66 11.2 18.22 12 18.43 12.46L18.56 12.72C18.96 13.69 19.06 14.72 18.92 15.72Z";
const ICON_ALERT = "M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16";

const PRESETS = ["comfort", "eco", "away"];

// A tap shows at once; the board value replaces it when Home Assistant confirms or this runs out.
const PENDING_MS = 4000;

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
    air_purge: "Purge",
    now: "Now",
    lower: "Lower the setpoint",
    raise: "Raise the setpoint",
    presets: { comfort: "Comfort", eco: "Eco", away: "Away" },
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
    fix: {
      sensor_stale:
        "The sensor has stopped reporting. Check it, or pick another in Configure -> Edit zone.",
      sensor_missing:
        "The sensor is unavailable. Check it, or pick another in Configure -> Edit zone.",
      relay_missing:
        "The relay is unavailable. Check the board, or pick another relay in Configure -> Edit zone.",
    },
    master: {
      disabled: "Pump not managed",
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
    air_purge: "Purga",
    now: "Agora",
    lower: "Baixar a temperatura",
    raise: "Subir a temperatura",
    presets: { comfort: "Conforto", eco: "Eco", away: "Ausente" },
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
    fix: {
      sensor_stale:
        "O sensor deixou de comunicar. Verifique-o, ou escolha outro em Configurar -> Edit zone.",
      sensor_missing:
        "O sensor está indisponível. Verifique-o, ou escolha outro em Configurar -> Edit zone.",
      relay_missing:
        "O relé está indisponível. Verifique a placa, ou escolha outro relé em Configurar -> Edit zone.",
    },
    master: {
      disabled: "Bomba não gerida",
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
    return { hass: {}, _config: {}, _pending: { state: true } };
  }

  constructor() {
    super();
    this._pending = {};
  }

  /** Drop what the board already shows, so a later change from elsewhere is not hidden. */
  willUpdate(changed) {
    if (!changed.has("hass") || !this.hass) return;
    const ids = Object.keys(this._pending);
    if (!ids.length) return;
    const next = {};
    for (const id of ids) {
      const p = this._pending[id];
      const s = this.hass.states[id];
      const done =
        !s ||
        Date.now() > p.until ||
        ((p.temperature === undefined || s.attributes.temperature === p.temperature) &&
          (p.preset === undefined || s.attributes.preset_mode === p.preset));
      if (!done) next[id] = p;
    }
    if (Object.keys(next).length !== ids.length) this._pending = next;
  }

  /** Setpoint and preset to show: the tap still in flight, else the board's. */
  _view(zone) {
    const a = zone.attributes;
    const p = this._pending[zone.entity_id];
    const live = p && Date.now() <= p.until;
    return {
      temperature: live && p.temperature !== undefined ? p.temperature : a.temperature,
      preset: live && p.preset !== undefined ? p.preset : a.preset_mode,
    };
  }

  _remember(zone, change) {
    const id = zone.entity_id;
    this._pending = {
      ...this._pending,
      [id]: { ...this._pending[id], ...change, until: Date.now() + PENDING_MS },
    };
    setTimeout(() => this.requestUpdate(), PENDING_MS + 50);
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
    return 3 + this._zones().length * 3;
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
    // Not managing the pump is a choice, so say so only while a zone is asking for heat.
    const showMaster =
      master && (master.state !== "disabled" || zones.some((z) => z.attributes.demand));
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
            ${showMaster
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
    const view = this._view(zone);
    const target =
      view.temperature !== undefined && view.temperature !== null
        ? Number(view.temperature).toFixed(1)
        : "--";
    const locked = a.locked_until > 0;
    const open = () => this._moreInfo(zone.entity_id);

    return html`
      <div class="zone ${off ? "disabled" : ""} ${a.is_bypass ? "bypass" : ""}">
        <div class="top">
          <div class="valve ${valve}" @click=${open} title=${l.fault[fault] || valve}>
            ${this._valveIcon(valve)}
          </div>
          <div class="name" @click=${open}>
            <span class="label">${a.friendly_name || zone.entity_id}</span>
            ${a.is_bypass ? html`<span class="tag">bypass</span>` : ""}
          </div>
          ${fault
            ? html`<span class="notice fault">${l.fault[fault] || fault}</span>`
            : locked
              ? html`<span class="notice">
                  <ha-icon icon="mdi:lock-clock"></ha-icon>
                  ${l.min_cycle(Math.ceil(a.locked_until / 60))}
                </span>`
              : ""}
        </div>

        ${fault && l.fix[fault]
          ? html`<div class="hint">
              ${l.fix[fault]}
              <code>
                ${fault === "relay_missing" ? a.relay_entity : a.sensor_entity}
              </code>
            </div>`
          : ""}

        ${a.is_bypass
          ? ""
          : html`
              <div class="mid">
                <div class="now" @click=${open}>
                  <small>${l.now}</small>
                  <b>${current}<small>°C</small></b>
                </div>
                <div class="stepper">
                  <button
                    aria-label=${l.lower}
                    @click=${() => this._nudge(zone, -0.5)}
                  >
                    <ha-icon icon="mdi:minus"></ha-icon>
                  </button>
                  <div class="set">${target}<small>°C</small></div>
                  <button
                    aria-label=${l.raise}
                    @click=${() => this._nudge(zone, +0.5)}
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
                  </button>
                </div>
              </div>
              <div class="presets">
                ${PRESETS.map(
                  (key) => html`
                    <button
                      class=${view.preset === key ? "on" : ""}
                      aria-pressed=${view.preset === key ? "true" : "false"}
                      @click=${() => this._preset(zone, key)}
                    >
                      ${l.presets[key]}
                    </button>
                  `
                )}
              </div>
            `}
        ${this._config.show_metrics
          ? html`<div class="metrics">
              ${l.metrics(a.runtime_hours ?? 0, a.cycles ?? 0)}
            </div>`
          : ""}
      </div>
    `;
  }

  _valveIcon(valve) {
    const color = VALVE_COLORS[valve] || VALVE_COLORS.closed;
    const closed = valve === "closed";
    const glyph =
      valve === "fault" ? ICON_ALERT : closed ? ICON_FIRE_OFF : ICON_FIRE;
    return html`
      <svg viewBox="0 0 48 48" aria-hidden="true">
        <circle cx="24" cy="24" r="21" class="halo" fill=${color} />
        <circle
          cx="24"
          cy="24"
          r="17"
          fill=${closed ? "none" : color}
          stroke=${color}
          stroke-width="2.5"
        />
        <g transform="translate(10 10) scale(1.1667)">
          <path
            d=${glyph}
            fill=${closed ? color : "rgba(255,255,255,0.95)"}
          />
        </g>
      </svg>
    `;
  }

  // -- actions -------------------------------------------------------
  _toggle(entityId) {
    this.hass.callService("switch", "toggle", { entity_id: entityId });
  }

  _nudge(zone, delta) {
    const a = zone.attributes;
    const base = Number(this._view(zone).temperature ?? 20);
    const lo = Number(a.min_temp ?? 5);
    const hi = Number(a.max_temp ?? 30);
    const temperature = Math.min(hi, Math.max(lo, Math.round((base + delta) * 2) / 2));
    // A manual setpoint leaves the presets, which is what the board will report.
    this._remember(zone, { temperature, preset: "none" });
    this.hass.callService("climate", "set_temperature", {
      entity_id: zone.entity_id,
      temperature,
    });
  }

  _preset(zone, preset) {
    // The preset's own setpoint is not known here, so the board's value is shown for it.
    this._remember(zone, { preset, temperature: undefined });
    this.hass.callService("climate", "set_preset_mode", {
      entity_id: zone.entity_id,
      preset_mode: preset,
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
        grid-template-columns: repeat(auto-fit, minmax(92px, 1fr));
        gap: 8px;
        margin-bottom: 16px;
      }
      button.global {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 10px 6px;
        border-radius: 14px;
        border: 1px solid var(--oh-glass-border);
        background: var(--oh-glass-bg);
        color: inherit;
        font: inherit;
        font-size: 0.85rem;
        min-width: 0;
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
        grid-template-columns: minmax(0, 1fr);
        gap: 10px;
      }
      .zone {
        padding: 14px;
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
      .zone button {
        font: inherit;
        color: inherit;
        cursor: pointer;
        touch-action: manipulation;
        -webkit-tap-highlight-color: transparent;
        border: 1px solid var(--oh-glass-border);
        background: var(--oh-glass-bg);
      }

      .top {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .valve {
        flex: none;
        width: 44px;
        height: 44px;
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
      .name {
        flex: 1;
        min-width: 0;
        font-weight: 600;
        font-size: 1.05rem;
        display: flex;
        align-items: center;
        gap: 6px;
        overflow: hidden;
        cursor: pointer;
      }
      .name .label {
        min-width: 0;
        overflow: hidden;
        overflow-wrap: anywhere;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        line-clamp: 2;
      }
      .hint {
        margin-top: 8px;
        font-size: 0.78rem;
        line-height: 1.35;
        opacity: 0.85;
      }
      .hint code {
        display: block;
        margin-top: 2px;
        font-size: 0.72rem;
        opacity: 0.7;
        overflow-wrap: anywhere;
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
      .notice {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        flex: none;
        max-width: 55%;
        font-size: 0.72rem;
        font-weight: 500;
        padding: 3px 9px;
        border-radius: 999px;
        background: var(--oh-glass-bg);
        border: 1px solid var(--oh-glass-border);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .notice.fault {
        color: #ff6b66;
        border-color: rgba(229, 57, 53, 0.55);
        background: rgba(229, 57, 53, 0.14);
      }
      .notice ha-icon {
        --mdc-icon-size: 14px;
      }

      .mid {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        margin-top: 12px;
      }
      .now {
        display: flex;
        flex-direction: column;
        line-height: 1.15;
        cursor: pointer;
      }
      .now small {
        font-size: 0.7rem;
        opacity: 0.7;
      }
      .now b {
        font-size: 1.35rem;
        font-weight: 500;
      }
      .now b small {
        font-size: 0.75rem;
        font-weight: 400;
      }
      .stepper {
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .stepper .set {
        min-width: 84px;
        text-align: center;
        font-size: 1.55rem;
        font-weight: 600;
        color: var(--oh-valve-open);
      }
      .stepper .set small {
        font-size: 0.75rem;
        font-weight: 400;
      }
      .stepper button {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        display: grid;
        place-items: center;
      }
      .stepper ha-icon {
        --mdc-icon-size: 28px;
      }

      .presets {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 12px;
      }
      .presets button {
        height: 46px;
        border-radius: 14px;
        font-size: 0.92rem;
        min-width: 0;
      }
      .presets button.on {
        color: var(--oh-valve-open);
        border-color: var(--oh-valve-open);
        background: rgba(251, 140, 0, 0.22);
        font-weight: 600;
      }
      .metrics {
        margin-top: 10px;
        font-size: 0.72rem;
        opacity: 0.7;
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

/*! OpenHydronic-HA - Copyright (C) 2026 David Lopes - GPL-3.0-or-later - https://github.com/davdlic/OpenHydronic-HA */
var d=window.LitElement||Object.getPrototypeOf(customElements.get("ha-panel-lovelace")||customElements.get("hui-view")),a=d.prototype.html,f=d.prototype.css,b="1.0.0",h={closed:"var(--oh-valve-closed)",opening:"var(--oh-valve-opening)",open:"var(--oh-valve-open)",fault:"var(--oh-valve-fault)"},m={en:{card_title:"Heating",card_description:"Hydronic zone control with valve status, global modes and air purge.",empty:"No zones configured yet. Add them in Settings -> Devices & services -> OpenHydronic -> Configure.",summer:"Summer",holiday:"Holiday",air_purge:"Air purge",purge_left:i=>`Purge ${i} min`,min_cycle:i=>`minimum cycle ${i} min`,metrics:(i,e)=>`${i} h - ${e} cycles`,editor_title:"Title",editor_zones:"Zones (empty = auto-detect)",editor_show_global:"Show global controls",editor_show_metrics:"Show per-zone metrics",fault:{sensor_stale:"Sensor not updating",sensor_missing:"Sensor unavailable",relay_missing:"Relay unavailable"},master:{disabled:"Master disabled",off:"Master off",waiting:"Thermal delay...",on:"Circulator running",purging:"Purging heat..."},system:{normal:"Normal",summer:"Summer",holiday:"Holiday",air_purge:"Air purge",anti_seize:"Anti-seize"}},pt:{card_title:"Climatiza\xE7\xE3o",card_description:"Controlo de zonas hidr\xE1ulicas com estado das v\xE1lvulas, modos globais e purga de ar.",empty:"Sem zonas configuradas. Adicione-as em Defini\xE7\xF5es -> Dispositivos e servi\xE7os -> OpenHydronic -> Configurar.",summer:"Ver\xE3o",holiday:"F\xE9rias",air_purge:"Purga de ar",purge_left:i=>`Purga ${i} min`,min_cycle:i=>`ciclo m\xEDnimo ${i} min`,metrics:(i,e)=>`${i} h - ${e} ciclos`,editor_title:"T\xEDtulo",editor_zones:"Zonas (vazio = dete\xE7\xE3o autom\xE1tica)",editor_show_global:"Mostrar controlos globais",editor_show_metrics:"Mostrar m\xE9tricas por zona",fault:{sensor_stale:"Sensor sem atualiza\xE7\xE3o",sensor_missing:"Sensor indispon\xEDvel",relay_missing:"Rel\xE9 indispon\xEDvel"},master:{disabled:"Master desativado",off:"Master desligado",waiting:"Delay t\xE9rmico\u2026",on:"Circulador ativo",purging:"Purga t\xE9rmica\u2026"},system:{normal:"Normal",summer:"Ver\xE3o",holiday:"F\xE9rias",air_purge:"Purga de ar",anti_seize:"Anti-gripagem"}}};function c(i){return m[String(i||"en").slice(0,2)]||m.en}var u=class extends d{static get properties(){return{hass:{},_config:{}}}static getStubConfig(e){let t=Object.keys(e.states).filter(s=>s.startsWith("climate.")&&e.states[s].attributes.valve_state!==void 0);return{type:"custom:openhydronic-card",title:c(e.language).card_title,zones:t}}static getConfigElement(){return document.createElement("openhydronic-card-editor")}setConfig(e){this._config={title:"OpenHydronic",show_global:!0,show_metrics:!1,...e}}getCardSize(){return 2+Math.ceil(this._zones().length/2)}get _l(){return c(this.hass&&this.hass.language)}_zones(){return this.hass?(this._config.zones&&this._config.zones.length?this._config.zones:Object.keys(this.hass.states).filter(t=>t.startsWith("climate.")&&this.hass.states[t].attributes.valve_state!==void 0)).map(t=>this.hass.states[t]).filter(Boolean):[]}_findEntity(e,t){if(this._config[t])return this.hass.states[this._config[t]];let s=Object.keys(this.hass.states).find(o=>o.startsWith(`${e}.`)&&o.includes(t));return s?this.hass.states[s]:void 0}render(){if(!this.hass||!this._config)return a``;let e=this._l,t=this._zones(),s=this._findEntity("switch","summer_mode"),o=this._findEntity("switch","holiday_mode"),r=this._findEntity("switch","air_purge"),n=this._findEntity("sensor","master_state"),l=t.length?t[0].attributes.system_mode:void 0;return a`
      <ha-card class="glass">
        <div class="header">
          <div class="title">
            <ha-icon icon="mdi:heating-coil"></ha-icon>
            <span>${this._config.title}</span>
          </div>
          <div class="status">
            ${n?a`<span class="pill master ${n.state}">
                  ${e.master[n.state]||n.state}
                </span>`:""}
            ${l&&l!=="normal"?a`<span class="pill mode">
                  ${e.system[l]||l}
                </span>`:""}
          </div>
        </div>

        ${this._config.show_global?a`<div class="globals">
              ${this._globalButton(s,"mdi:weather-sunny",e.summer)}
              ${this._globalButton(o,"mdi:bag-suitcase",e.holiday)}
              ${this._globalButton(r,"mdi:air-filter",this._purgeLabel(r))}
            </div>`:""}

        <div class="zones">
          ${t.length?t.map(p=>this._renderZone(p)):a`<div class="empty">${e.empty}</div>`}
        </div>
      </ha-card>
    `}_purgeLabel(e){let t=this._l;if(!e||e.state!=="on")return t.air_purge;let s=e.attributes.remaining_seconds||0;return t.purge_left(Math.ceil(s/60))}_globalButton(e,t,s){if(!e)return"";let o=e.state==="on";return a`
      <button
        class="global ${o?"active":""}"
        @click=${()=>this._toggle(e.entity_id)}
        title=${s}
      >
        <ha-icon icon=${t}></ha-icon>
        <span>${s}</span>
      </button>
    `}_renderZone(e){let t=this._l,s=e.attributes,o=s.valve_state||"closed",r=s.fault,n=e.state==="off",l=s.current_temperature!==void 0&&s.current_temperature!==null?Number(s.current_temperature).toFixed(1):"--",p=s.temperature!==void 0&&s.temperature!==null?Number(s.temperature).toFixed(1):"--",v=s.locked_until>0;return a`
      <div class="zone ${n?"disabled":""} ${s.is_bypass?"bypass":""}">
        <div
          class="valve ${o}"
          @click=${()=>this._moreInfo(e.entity_id)}
          title=${t.fault[r]||o}
        >
          ${this._valveIcon(o)}
        </div>

        <div class="info" @click=${()=>this._moreInfo(e.entity_id)}>
          <div class="name">
            ${s.friendly_name||e.entity_id}
            ${s.is_bypass?a`<span class="tag">bypass</span>`:""}
          </div>
          <div class="temps">
            <span class="current">${l}<small>°C</small></span>
            <span class="sep">→</span>
            <span class="target">${p}<small>°C</small></span>
          </div>
          <div class="sub">
            ${r?a`<span class="fault">${t.fault[r]||r}</span>`:v?a`<span class="lock">
                    <ha-icon icon="mdi:lock-clock"></ha-icon>
                    ${t.min_cycle(Math.ceil(s.locked_until/60))}
                  </span>`:a`<span class="preset">${s.preset_mode||""}</span>`}
            ${this._config.show_metrics?a`<span class="metrics">
                  ${t.metrics(s.runtime_hours??0,s.cycles??0)}
                </span>`:""}
          </div>
        </div>

        ${s.is_bypass?"":a`<div class="controls">
              <button @click=${()=>this._nudge(e,.5)}>
                <ha-icon icon="mdi:plus"></ha-icon>
              </button>
              <button @click=${()=>this._nudge(e,-.5)}>
                <ha-icon icon="mdi:minus"></ha-icon>
              </button>
            </div>`}
      </div>
    `}_valveIcon(e){let t=h[e]||h.closed;return a`
      <svg viewBox="0 0 48 48" aria-hidden="true">
        <circle cx="24" cy="24" r="21" class="halo" fill=${t} />
        <path
          d="M24 6v9m0 18v9M6 24h9m18 0h9"
          stroke=${t}
          stroke-width="3"
          stroke-linecap="round"
          fill="none"
          opacity="0.55"
        />
        <circle cx="24" cy="24" r="10" fill=${t} />
        <path
          d="M19 24h10M24 19v10"
          stroke="rgba(255,255,255,0.9)"
          stroke-width="2.4"
          stroke-linecap="round"
        />
      </svg>
    `}_toggle(e){this.hass.callService("switch","toggle",{entity_id:e})}_nudge(e,t){let s=Number(e.attributes.temperature??20);this.hass.callService("climate","set_temperature",{entity_id:e.entity_id,temperature:Math.round((s+t)*2)/2})}_moreInfo(e){this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:e},bubbles:!0,composed:!0}))}static get styles(){return f`
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
    `}},g=class extends d{static get properties(){return{hass:{},_config:{}}}setConfig(e){this._config=e}get _schema(){return[{name:"title",selector:{text:{}}},{name:"zones",selector:{entity:{domain:"climate",multiple:!0}}},{name:"show_global",selector:{boolean:{}}},{name:"show_metrics",selector:{boolean:{}}}]}render(){return!this.hass||!this._config?a``:a`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._schema}
        .computeLabel=${e=>{let t=c(this.hass&&this.hass.language);return{title:t.editor_title,zones:t.editor_zones,show_global:t.editor_show_global,show_metrics:t.editor_show_metrics}[e.name]||e.name}}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `}_valueChanged(e){let t=new CustomEvent("config-changed",{detail:{config:e.detail.value},bubbles:!0,composed:!0});this.dispatchEvent(t)}};customElements.define("openhydronic-card",u);customElements.define("openhydronic-card-editor",g);window.customCards=window.customCards||[];window.customCards.push({type:"openhydronic-card",name:"OpenHydronic Card",description:c(navigator.language).card_description,preview:!0,documentationURL:"https://github.com/davdlic/OpenHydronic-HA"});console.info(`%c OPENHYDRONIC-CARD %c ${b} `,"color:#fff;background:#fb8c00;font-weight:700;border-radius:4px 0 0 4px","color:#fb8c00;background:#222;border-radius:0 4px 4px 0");

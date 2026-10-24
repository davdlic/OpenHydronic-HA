/*! OpenHydronic-HA - Copyright (C) 2026 David Lopes - GPL-3.0-or-later - https://github.com/davdlic/OpenHydronic-HA */
var p=window.LitElement||Object.getPrototypeOf(customElements.get("ha-panel-lovelace")||customElements.get("hui-view")),i=p.prototype.html,_=p.prototype.css,y="1.2.1",x="M17.66 11.2C17.43 10.9 17.15 10.64 16.89 10.38C16.22 9.78 15.46 9.35 14.82 8.72C13.33 7.26 13 4.85 13.95 3C13 3.23 12.17 3.75 11.46 4.32C8.87 6.4 7.85 10.07 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C6.87 12.33 6.69 10.28 7.45 8.64C5.78 10 4.87 12.3 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C18.86 17.66 19.5 15 18.56 12.72L18.43 12.46C18.22 12 17.66 11.2 17.66 11.2M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.78 14.43 12.46 13.77 12.33 13C12.21 12.26 12.23 11.63 12.5 10.94C12.69 11.32 12.89 11.7 13.13 12C13.9 13 15.11 13.44 15.37 14.8C15.41 14.94 15.43 15.08 15.43 15.23C15.46 16.05 15.1 16.95 14.5 17.5H14.5Z",w="M22.11 21.46L2.39 1.73L1.11 3L7.09 9C5.66 10.36 4.88 12.47 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C17.1 19.26 17.15 19.18 17.22 19.11L20.84 22.73L22.11 21.46M8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C7 12.47 6.74 10.69 7.26 9.15L8.58 10.47C8.58 11.4 8.73 12.33 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.66 15 12.66 14.76 12.64 14.53L15 16.88C14.85 17.11 14.69 17.33 14.5 17.5M18.92 15.72L9.65 6.46C10.12 5.65 10.72 4.92 11.46 4.32C12.17 3.75 13 3.23 13.95 3C13 4.85 13.33 7.26 14.82 8.72C15.46 9.35 16.22 9.78 16.89 10.38C17.15 10.64 17.43 10.9 17.66 11.2C17.66 11.2 18.22 12 18.43 12.46L18.56 12.72C18.96 13.69 19.06 14.72 18.92 15.72Z",C="M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",$=["comfort","eco","away"],v={closed:"var(--oh-valve-closed)",opening:"var(--oh-valve-opening)",open:"var(--oh-valve-open)",fault:"var(--oh-valve-fault)"},f={en:{card_title:"Heating",card_description:"Hydronic zone control with valve status, global modes and air purge.",empty:"No zones configured yet. Add them in Settings -> Devices & services -> OpenHydronic -> Configure.",summer:"Summer",holiday:"Holiday",air_purge:"Purge",now:"Now",lower:"Lower the setpoint",raise:"Raise the setpoint",presets:{comfort:"Comfort",eco:"Eco",away:"Away"},purge_left:o=>`Purge ${o} min`,min_cycle:o=>`minimum cycle ${o} min`,metrics:(o,e)=>`${o} h - ${e} cycles`,editor_title:"Title",editor_zones:"Zones (empty = auto-detect)",editor_show_global:"Show global controls",editor_show_metrics:"Show per-zone metrics",fault:{sensor_stale:"Sensor not updating",sensor_missing:"Sensor unavailable",relay_missing:"Relay unavailable"},master:{disabled:"Master disabled",off:"Master off",waiting:"Thermal delay...",on:"Circulator running",purging:"Purging heat..."},system:{normal:"Normal",summer:"Summer",holiday:"Holiday",air_purge:"Air purge",anti_seize:"Anti-seize"}},pt:{card_title:"Climatiza\xE7\xE3o",card_description:"Controlo de zonas hidr\xE1ulicas com estado das v\xE1lvulas, modos globais e purga de ar.",empty:"Sem zonas configuradas. Adicione-as em Defini\xE7\xF5es -> Dispositivos e servi\xE7os -> OpenHydronic -> Configurar.",summer:"Ver\xE3o",holiday:"F\xE9rias",air_purge:"Purga",now:"Agora",lower:"Baixar a temperatura",raise:"Subir a temperatura",presets:{comfort:"Conforto",eco:"Eco",away:"Ausente"},purge_left:o=>`Purga ${o} min`,min_cycle:o=>`ciclo m\xEDnimo ${o} min`,metrics:(o,e)=>`${o} h - ${e} ciclos`,editor_title:"T\xEDtulo",editor_zones:"Zonas (vazio = dete\xE7\xE3o autom\xE1tica)",editor_show_global:"Mostrar controlos globais",editor_show_metrics:"Mostrar m\xE9tricas por zona",fault:{sensor_stale:"Sensor sem atualiza\xE7\xE3o",sensor_missing:"Sensor indispon\xEDvel",relay_missing:"Rel\xE9 indispon\xEDvel"},master:{disabled:"Master desativado",off:"Master desligado",waiting:"Delay t\xE9rmico\u2026",on:"Circulador ativo",purging:"Purga t\xE9rmica\u2026"},system:{normal:"Normal",summer:"Ver\xE3o",holiday:"F\xE9rias",air_purge:"Purga de ar",anti_seize:"Anti-gripagem"}}};function d(o){return f[String(o||"en").slice(0,2)]||f.en}var m=class extends p{static get properties(){return{hass:{},_config:{}}}static getStubConfig(e){let t=Object.keys(e.states).filter(s=>s.startsWith("climate.")&&e.states[s].attributes.valve_state!==void 0);return{type:"custom:openhydronic-card",title:d(e.language).card_title,zones:t}}static getConfigElement(){return document.createElement("openhydronic-card-editor")}setConfig(e){this._config={title:"OpenHydronic",show_global:!0,show_metrics:!1,...e}}getCardSize(){return 3+this._zones().length*3}get _l(){return d(this.hass&&this.hass.language)}_zones(){return this.hass?(this._config.zones&&this._config.zones.length?this._config.zones:Object.keys(this.hass.states).filter(t=>t.startsWith("climate.")&&this.hass.states[t].attributes.valve_state!==void 0)).map(t=>this.hass.states[t]).filter(Boolean):[]}_findEntity(e,t){if(this._config[t])return this.hass.states[this._config[t]];let s=Object.keys(this.hass.states).find(a=>a.startsWith(`${e}.`)&&a.includes(t));return s?this.hass.states[s]:void 0}render(){if(!this.hass||!this._config)return i``;let e=this._l,t=this._zones(),s=this._findEntity("switch","summer_mode"),a=this._findEntity("switch","holiday_mode"),r=this._findEntity("switch","air_purge"),n=this._findEntity("sensor","master_state"),l=t.length?t[0].attributes.system_mode:void 0;return i`
      <ha-card class="glass">
        <div class="header">
          <div class="title">
            <ha-icon icon="mdi:heating-coil"></ha-icon>
            <span>${this._config.title}</span>
          </div>
          <div class="status">
            ${n?i`<span class="pill master ${n.state}">
                  ${e.master[n.state]||n.state}
                </span>`:""}
            ${l&&l!=="normal"?i`<span class="pill mode">
                  ${e.system[l]||l}
                </span>`:""}
          </div>
        </div>

        ${this._config.show_global?i`<div class="globals">
              ${this._globalButton(s,"mdi:weather-sunny",e.summer)}
              ${this._globalButton(a,"mdi:bag-suitcase",e.holiday)}
              ${this._globalButton(r,"mdi:air-filter",this._purgeLabel(r))}
            </div>`:""}

        <div class="zones">
          ${t.length?t.map(g=>this._renderZone(g)):i`<div class="empty">${e.empty}</div>`}
        </div>
      </ha-card>
    `}_purgeLabel(e){let t=this._l;if(!e||e.state!=="on")return t.air_purge;let s=e.attributes.remaining_seconds||0;return t.purge_left(Math.ceil(s/60))}_globalButton(e,t,s){if(!e)return"";let a=e.state==="on";return i`
      <button
        class="global ${a?"active":""}"
        @click=${()=>this._toggle(e.entity_id)}
        title=${s}
      >
        <ha-icon icon=${t}></ha-icon>
        <span>${s}</span>
      </button>
    `}_renderZone(e){let t=this._l,s=e.attributes,a=s.valve_state||"closed",r=s.fault,n=e.state==="off",l=s.current_temperature!==void 0&&s.current_temperature!==null?Number(s.current_temperature).toFixed(1):"--",g=s.temperature!==void 0&&s.temperature!==null?Number(s.temperature).toFixed(1):"--",b=s.locked_until>0,h=()=>this._moreInfo(e.entity_id);return i`
      <div class="zone ${n?"disabled":""} ${s.is_bypass?"bypass":""}">
        <div class="top">
          <div class="valve ${a}" @click=${h} title=${t.fault[r]||a}>
            ${this._valveIcon(a)}
          </div>
          <div class="name" @click=${h}>
            ${s.friendly_name||e.entity_id}
            ${s.is_bypass?i`<span class="tag">bypass</span>`:""}
          </div>
          ${r?i`<span class="notice fault">${t.fault[r]||r}</span>`:b?i`<span class="notice">
                  <ha-icon icon="mdi:lock-clock"></ha-icon>
                  ${t.min_cycle(Math.ceil(s.locked_until/60))}
                </span>`:""}
        </div>

        ${s.is_bypass?"":i`
              <div class="mid">
                <div class="now" @click=${h}>
                  <small>${t.now}</small>
                  <b>${l}<small>°C</small></b>
                </div>
                <div class="stepper">
                  <button
                    aria-label=${t.lower}
                    @click=${()=>this._nudge(e,-.5)}
                  >
                    <ha-icon icon="mdi:minus"></ha-icon>
                  </button>
                  <div class="set">${g}<small>°C</small></div>
                  <button
                    aria-label=${t.raise}
                    @click=${()=>this._nudge(e,.5)}
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
                  </button>
                </div>
              </div>
              <div class="presets">
                ${$.map(c=>i`
                    <button
                      class=${s.preset_mode===c?"on":""}
                      aria-pressed=${s.preset_mode===c?"true":"false"}
                      @click=${()=>this._preset(e,c)}
                    >
                      ${t.presets[c]}
                    </button>
                  `)}
              </div>
            `}
        ${this._config.show_metrics?i`<div class="metrics">
              ${t.metrics(s.runtime_hours??0,s.cycles??0)}
            </div>`:""}
      </div>
    `}_valveIcon(e){let t=v[e]||v.closed,s=e==="closed";return i`
      <svg viewBox="0 0 48 48" aria-hidden="true">
        <circle cx="24" cy="24" r="21" class="halo" fill=${t} />
        <circle
          cx="24"
          cy="24"
          r="17"
          fill=${s?"none":t}
          stroke=${t}
          stroke-width="2.5"
        />
        <g transform="translate(10 10) scale(1.1667)">
          <path
            d=${e==="fault"?C:s?w:x}
            fill=${s?t:"rgba(255,255,255,0.95)"}
          />
        </g>
      </svg>
    `}_toggle(e){this.hass.callService("switch","toggle",{entity_id:e})}_nudge(e,t){let s=Number(e.attributes.temperature??20);this.hass.callService("climate","set_temperature",{entity_id:e.entity_id,temperature:Math.round((s+t)*2)/2})}_preset(e,t){this.hass.callService("climate","set_preset_mode",{entity_id:e.entity_id,preset_mode:t})}_moreInfo(e){this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:e},bubbles:!0,composed:!0}))}static get styles(){return _`
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
        text-overflow: ellipsis;
        white-space: nowrap;
        cursor: pointer;
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
    `}},u=class extends p{static get properties(){return{hass:{},_config:{}}}setConfig(e){this._config=e}get _schema(){return[{name:"title",selector:{text:{}}},{name:"zones",selector:{entity:{domain:"climate",multiple:!0}}},{name:"show_global",selector:{boolean:{}}},{name:"show_metrics",selector:{boolean:{}}}]}render(){return!this.hass||!this._config?i``:i`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._schema}
        .computeLabel=${e=>{let t=d(this.hass&&this.hass.language);return{title:t.editor_title,zones:t.editor_zones,show_global:t.editor_show_global,show_metrics:t.editor_show_metrics}[e.name]||e.name}}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `}_valueChanged(e){let t=new CustomEvent("config-changed",{detail:{config:e.detail.value},bubbles:!0,composed:!0});this.dispatchEvent(t)}};customElements.define("openhydronic-card",m);customElements.define("openhydronic-card-editor",u);window.customCards=window.customCards||[];window.customCards.push({type:"openhydronic-card",name:"OpenHydronic Card",description:d(navigator.language).card_description,preview:!0,documentationURL:"https://github.com/davdlic/OpenHydronic-HA"});console.info(`%c OPENHYDRONIC-CARD %c ${y} `,"color:#fff;background:#fb8c00;font-weight:700;border-radius:4px 0 0 4px","color:#fb8c00;background:#222;border-radius:0 4px 4px 0");

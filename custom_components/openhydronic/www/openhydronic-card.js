/*! OpenHydronic-HA - Copyright (C) 2026 David Lopes - GPL-3.0-or-later - https://github.com/davdlic/OpenHydronic-HA */
var N=globalThis,H=N.ShadowRoot&&(N.ShadyCSS===void 0||N.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,T=Symbol(),ee=new WeakMap,C=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==T)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(H&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=ee.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&ee.set(t,e))}return e}toString(){return this.cssText}},te=o=>new C(typeof o=="string"?o:o+"",void 0,T),D=(o,...e)=>{let t=o.length===1?o[0]:e.reduce((s,i,r)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+o[r+1],o[0]);return new C(t,o,T)},se=(o,e)=>{if(H)o.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),i=N.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=t.cssText,o.appendChild(s)}},I=H?o=>o:o=>o instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return te(t)})(o):o;var{is:ye,defineProperty:we,getOwnPropertyDescriptor:xe,getOwnPropertyNames:Ae,getOwnPropertySymbols:Ce,getPrototypeOf:Ee}=Object,R=globalThis,ie=R.trustedTypes,Se=ie?ie.emptyScript:"",Pe=R.reactiveElementPolyfillSupport,E=(o,e)=>o,j={toAttribute(o,e){switch(e){case Boolean:o=o?Se:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,e){let t=o;switch(e){case Boolean:t=o!==null;break;case Number:t=o===null?null:Number(o);break;case Object:case Array:try{t=JSON.parse(o)}catch{t=null}}return t}},re=(o,e)=>!ye(o,e),oe={attribute:!0,type:String,converter:j,reflect:!1,useDefault:!1,hasChanged:re};Symbol.metadata??=Symbol("metadata"),R.litPropertyMetadata??=new WeakMap;var g=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=oe){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(e,s,t);i!==void 0&&we(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){let{get:i,set:r}=xe(this.prototype,e)??{get(){return this[t]},set(n){this[t]=n}};return{get:i,set(n){let c=i?.call(this);r?.call(this,n),this.requestUpdate(e,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??oe}static _$Ei(){if(this.hasOwnProperty(E("elementProperties")))return;let e=Ee(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(E("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(E("properties"))){let t=this.properties,s=[...Ae(t),...Ce(t)];for(let i of s)this.createProperty(i,t[i])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,i]of t)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let i=this._$Eu(t,s);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let i of s)t.unshift(I(i))}else e!==void 0&&t.push(I(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return se(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(i!==void 0&&s.reflect===!0){let r=(s.converter?.toAttribute!==void 0?s.converter:j).toAttribute(t,s.type);this._$Em=e,r==null?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(e,t){let s=this.constructor,i=s._$Eh.get(e);if(i!==void 0&&this._$Em!==i){let r=s.getPropertyOptions(i),n=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:j;this._$Em=i;let c=n.fromAttribute(t,r.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(e,t,s,i=!1,r){if(e!==void 0){let n=this.constructor;if(i===!1&&(r=this[e]),s??=n.getPropertyOptions(e),!((s.hasChanged??re)(r,t)||s.useDefault&&s.reflect&&r===this._$Ej?.get(e)&&!this.hasAttribute(n._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:r},n){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,n??t??this[e]),r!==!0||n!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,r]of this._$Ep)this[i]=r;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,r]of s){let{wrapped:n}=r,c=this[i];n!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,r,c)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};g.elementStyles=[],g.shadowRootOptions={mode:"open"},g[E("elementProperties")]=new Map,g[E("finalized")]=new Map,Pe?.({ReactiveElement:g}),(R.reactiveElementVersions??=[]).push("2.1.2");var K=globalThis,ne=o=>o,U=K.trustedTypes,ae=U?U.createPolicy("lit-html",{createHTML:o=>o}):void 0,ue="$lit$",v=`lit$${Math.random().toFixed(9).slice(2)}$`,me="?"+v,ke=`<${me}>`,y=document,P=()=>y.createComment(""),k=o=>o===null||typeof o!="object"&&typeof o!="function",J=Array.isArray,ze=o=>J(o)||typeof o?.[Symbol.iterator]=="function",B=`[ 	
\f\r]`,S=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,le=/-->/g,ce=/>/g,$=RegExp(`>|${B}(?:([^\\s"'>=/]+)(${B}*=${B}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),he=/'/g,de=/"/g,ge=/^(?:script|style|textarea|title)$/i,Y=o=>(e,...t)=>({_$litType$:o,strings:e,values:t}),d=Y(1),Ve=Y(2),qe=Y(3),w=Symbol.for("lit-noChange"),u=Symbol.for("lit-nothing"),pe=new WeakMap,b=y.createTreeWalker(y,129);function _e(o,e){if(!J(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return ae!==void 0?ae.createHTML(e):e}var Me=(o,e)=>{let t=o.length-1,s=[],i,r=e===2?"<svg>":e===3?"<math>":"",n=S;for(let c=0;c<t;c++){let a=o[c],h,p,l=-1,m=0;for(;m<a.length&&(n.lastIndex=m,p=n.exec(a),p!==null);)m=n.lastIndex,n===S?p[1]==="!--"?n=le:p[1]!==void 0?n=ce:p[2]!==void 0?(ge.test(p[2])&&(i=RegExp("</"+p[2],"g")),n=$):p[3]!==void 0&&(n=$):n===$?p[0]===">"?(n=i??S,l=-1):p[1]===void 0?l=-2:(l=n.lastIndex-p[2].length,h=p[1],n=p[3]===void 0?$:p[3]==='"'?de:he):n===de||n===he?n=$:n===le||n===ce?n=S:(n=$,i=void 0);let f=n===$&&o[c+1].startsWith("/>")?" ":"";r+=n===S?a+ke:l>=0?(s.push(h),a.slice(0,l)+ue+a.slice(l)+v+f):a+v+(l===-2?c:f)}return[_e(o,r+(o[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},z=class o{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let r=0,n=0,c=e.length-1,a=this.parts,[h,p]=Me(e,t);if(this.el=o.createElement(h,s),b.currentNode=this.el.content,t===2||t===3){let l=this.el.content.firstChild;l.replaceWith(...l.childNodes)}for(;(i=b.nextNode())!==null&&a.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let l of i.getAttributeNames())if(l.endsWith(ue)){let m=p[n++],f=i.getAttribute(l).split(v),O=/([.?@])?(.*)/.exec(m);a.push({type:1,index:r,name:O[2],strings:f,ctor:O[1]==="."?q:O[1]==="?"?W:O[1]==="@"?F:A}),i.removeAttribute(l)}else l.startsWith(v)&&(a.push({type:6,index:r}),i.removeAttribute(l));if(ge.test(i.tagName)){let l=i.textContent.split(v),m=l.length-1;if(m>0){i.textContent=U?U.emptyScript:"";for(let f=0;f<m;f++)i.append(l[f],P()),b.nextNode(),a.push({type:2,index:++r});i.append(l[m],P())}}}else if(i.nodeType===8)if(i.data===me)a.push({type:2,index:r});else{let l=-1;for(;(l=i.data.indexOf(v,l+1))!==-1;)a.push({type:7,index:r}),l+=v.length-1}r++}}static createElement(e,t){let s=y.createElement("template");return s.innerHTML=e,s}};function x(o,e,t=o,s){if(e===w)return e;let i=s!==void 0?t._$Co?.[s]:t._$Cl,r=k(e)?void 0:e._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),r===void 0?i=void 0:(i=new r(o),i._$AT(o,t,s)),s!==void 0?(t._$Co??=[])[s]=i:t._$Cl=i),i!==void 0&&(e=x(o,i._$AS(o,e.values),i,s)),e}var V=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??y).importNode(t,!0);b.currentNode=i;let r=b.nextNode(),n=0,c=0,a=s[0];for(;a!==void 0;){if(n===a.index){let h;a.type===2?h=new M(r,r.nextSibling,this,e):a.type===1?h=new a.ctor(r,a.name,a.strings,this,e):a.type===6&&(h=new Z(r,this,e)),this._$AV.push(h),a=s[++c]}n!==a?.index&&(r=b.nextNode(),n++)}return b.currentNode=y,i}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},M=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=u,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=x(this,e,t),k(e)?e===u||e==null||e===""?(this._$AH!==u&&this._$AR(),this._$AH=u):e!==this._$AH&&e!==w&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):ze(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==u&&k(this._$AH)?this._$AA.nextSibling.data=e:this.T(y.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,i=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=z.createElement(_e(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{let r=new V(i,this),n=r.u(this.options);r.p(t),this.T(n),this._$AH=r}}_$AC(e){let t=pe.get(e.strings);return t===void 0&&pe.set(e.strings,t=new z(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,i=0;for(let r of e)i===t.length?t.push(s=new o(this.O(P()),this.O(P()),this,this.options)):s=t[i],s._$AI(r),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=ne(e).nextSibling;ne(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},A=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,r){this.type=1,this._$AH=u,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=r,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=u}_$AI(e,t=this,s,i){let r=this.strings,n=!1;if(r===void 0)e=x(this,e,t,0),n=!k(e)||e!==this._$AH&&e!==w,n&&(this._$AH=e);else{let c=e,a,h;for(e=r[0],a=0;a<r.length-1;a++)h=x(this,c[s+a],t,a),h===w&&(h=this._$AH[a]),n||=!k(h)||h!==this._$AH[a],h===u?e=u:e!==u&&(e+=(h??"")+r[a+1]),this._$AH[a]=h}n&&!i&&this.j(e)}j(e){e===u?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},q=class extends A{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===u?void 0:e}},W=class extends A{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==u)}},F=class extends A{constructor(e,t,s,i,r){super(e,t,s,i,r),this.type=5}_$AI(e,t=this){if((e=x(this,e,t,0)??u)===w)return;let s=this._$AH,i=e===u&&s!==u||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,r=e!==u&&(s===u||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},Z=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){x(this,e)}};var Oe=K.litHtmlPolyfillSupport;Oe?.(z,M),(K.litHtmlVersions??=[]).push("3.3.3");var fe=(o,e,t)=>{let s=t?.renderBefore??e,i=s._$litPart$;if(i===void 0){let r=t?.renderBefore??null;s._$litPart$=i=new M(e.insertBefore(P(),r),r,void 0,t??{})}return i._$AI(o),i};var G=globalThis,_=class extends g{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=fe(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return w}};_._$litElement$=!0,_.finalized=!0,G.litElementHydrateSupport?.({LitElement:_});var Ne=G.litElementPolyfillSupport;Ne?.({LitElement:_});(G.litElementVersions??=[]).push("4.2.2");var He="1.2.3",Re="M17.66 11.2C17.43 10.9 17.15 10.64 16.89 10.38C16.22 9.78 15.46 9.35 14.82 8.72C13.33 7.26 13 4.85 13.95 3C13 3.23 12.17 3.75 11.46 4.32C8.87 6.4 7.85 10.07 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C6.87 12.33 6.69 10.28 7.45 8.64C5.78 10 4.87 12.3 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C18.86 17.66 19.5 15 18.56 12.72L18.43 12.46C18.22 12 17.66 11.2 17.66 11.2M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.78 14.43 12.46 13.77 12.33 13C12.21 12.26 12.23 11.63 12.5 10.94C12.69 11.32 12.89 11.7 13.13 12C13.9 13 15.11 13.44 15.37 14.8C15.41 14.94 15.43 15.08 15.43 15.23C15.46 16.05 15.1 16.95 14.5 17.5H14.5Z",Ue="M22.11 21.46L2.39 1.73L1.11 3L7.09 9C5.66 10.36 4.88 12.47 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C17.1 19.26 17.15 19.18 17.22 19.11L20.84 22.73L22.11 21.46M8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C7 12.47 6.74 10.69 7.26 9.15L8.58 10.47C8.58 11.4 8.73 12.33 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.66 15 12.66 14.76 12.64 14.53L15 16.88C14.85 17.11 14.69 17.33 14.5 17.5M18.92 15.72L9.65 6.46C10.12 5.65 10.72 4.92 11.46 4.32C12.17 3.75 13 3.23 13.95 3C13 4.85 13.33 7.26 14.82 8.72C15.46 9.35 16.22 9.78 16.89 10.38C17.15 10.64 17.43 10.9 17.66 11.2C17.66 11.2 18.22 12 18.43 12.46L18.56 12.72C18.96 13.69 19.06 14.72 18.92 15.72Z",Le="M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",Te=["comfort","eco","away"],ve=4e3,$e={closed:"var(--oh-valve-closed)",opening:"var(--oh-valve-opening)",open:"var(--oh-valve-open)",fault:"var(--oh-valve-fault)"},be={en:{card_title:"Heating",card_description:"Hydronic zone control with valve status, global modes and air purge.",empty:"No zones configured yet. Add them in Settings -> Devices & services -> OpenHydronic -> Configure.",summer:"Summer",holiday:"Holiday",air_purge:"Purge",now:"Now",lower:"Lower the setpoint",raise:"Raise the setpoint",presets:{comfort:"Comfort",eco:"Eco",away:"Away"},purge_left:o=>`Purge ${o} min`,min_cycle:o=>`minimum cycle ${o} min`,metrics:(o,e)=>`${o} h - ${e} cycles`,editor_title:"Title",editor_zones:"Zones (empty = auto-detect)",editor_show_global:"Show global controls",editor_show_metrics:"Show per-zone metrics",fault:{sensor_stale:"Sensor not updating",sensor_missing:"Sensor unavailable",relay_missing:"Relay unavailable"},fix:{sensor_stale:"The sensor has stopped reporting. Check it, or pick another in Configure -> Edit zone.",sensor_missing:"The sensor is unavailable. Check it, or pick another in Configure -> Edit zone.",relay_missing:"The relay is unavailable. Check the board, or pick another relay in Configure -> Edit zone."},master:{disabled:"Pump not managed",off:"Master off",waiting:"Thermal delay...",on:"Circulator running",purging:"Purging heat..."},system:{normal:"Normal",summer:"Summer",holiday:"Holiday",air_purge:"Air purge",anti_seize:"Anti-seize"}},pt:{card_title:"Climatiza\xE7\xE3o",card_description:"Controlo de zonas hidr\xE1ulicas com estado das v\xE1lvulas, modos globais e purga de ar.",empty:"Sem zonas configuradas. Adicione-as em Defini\xE7\xF5es -> Dispositivos e servi\xE7os -> OpenHydronic -> Configurar.",summer:"Ver\xE3o",holiday:"F\xE9rias",air_purge:"Purga",now:"Agora",lower:"Baixar a temperatura",raise:"Subir a temperatura",presets:{comfort:"Conforto",eco:"Eco",away:"Ausente"},purge_left:o=>`Purga ${o} min`,min_cycle:o=>`ciclo m\xEDnimo ${o} min`,metrics:(o,e)=>`${o} h - ${e} ciclos`,editor_title:"T\xEDtulo",editor_zones:"Zonas (vazio = dete\xE7\xE3o autom\xE1tica)",editor_show_global:"Mostrar controlos globais",editor_show_metrics:"Mostrar m\xE9tricas por zona",fault:{sensor_stale:"Sensor sem atualiza\xE7\xE3o",sensor_missing:"Sensor indispon\xEDvel",relay_missing:"Rel\xE9 indispon\xEDvel"},fix:{sensor_stale:"O sensor deixou de comunicar. Verifique-o, ou escolha outro em Configurar -> Edit zone.",sensor_missing:"O sensor est\xE1 indispon\xEDvel. Verifique-o, ou escolha outro em Configurar -> Edit zone.",relay_missing:"O rel\xE9 est\xE1 indispon\xEDvel. Verifique a placa, ou escolha outro rel\xE9 em Configurar -> Edit zone."},master:{disabled:"Bomba n\xE3o gerida",off:"Master desligado",waiting:"Delay t\xE9rmico\u2026",on:"Circulador ativo",purging:"Purga t\xE9rmica\u2026"},system:{normal:"Normal",summer:"Ver\xE3o",holiday:"F\xE9rias",air_purge:"Purga de ar",anti_seize:"Anti-gripagem"}}};function L(o){return be[String(o||"en").slice(0,2)]||be.en}var Q=class extends _{static get properties(){return{hass:{},_config:{},_pending:{state:!0}}}constructor(){super(),this._pending={}}willUpdate(e){if(!e.has("hass")||!this.hass)return;let t=Object.keys(this._pending);if(!t.length)return;let s={};for(let i of t){let r=this._pending[i],n=this.hass.states[i];!n||Date.now()>r.until||(r.temperature===void 0||n.attributes.temperature===r.temperature)&&(r.preset===void 0||n.attributes.preset_mode===r.preset)||(s[i]=r)}Object.keys(s).length!==t.length&&(this._pending=s)}_view(e){let t=e.attributes,s=this._pending[e.entity_id],i=s&&Date.now()<=s.until;return{temperature:i&&s.temperature!==void 0?s.temperature:t.temperature,preset:i&&s.preset!==void 0?s.preset:t.preset_mode}}_remember(e,t){let s=e.entity_id;this._pending={...this._pending,[s]:{...this._pending[s],...t,until:Date.now()+ve}},setTimeout(()=>this.requestUpdate(),ve+50)}static getStubConfig(e){let t=Object.keys(e.states).filter(s=>s.startsWith("climate.")&&e.states[s].attributes.valve_state!==void 0);return{type:"custom:openhydronic-card",title:L(e.language).card_title,zones:t}}static getConfigElement(){return document.createElement("openhydronic-card-editor")}setConfig(e){this._config={title:"OpenHydronic",show_global:!0,show_metrics:!1,...e}}getCardSize(){return 3+this._zones().length*3}get _l(){return L(this.hass&&this.hass.language)}_zones(){return this.hass?(this._config.zones&&this._config.zones.length?this._config.zones:Object.keys(this.hass.states).filter(t=>t.startsWith("climate.")&&this.hass.states[t].attributes.valve_state!==void 0)).map(t=>this.hass.states[t]).filter(Boolean):[]}_findEntity(e,t){if(this._config[t])return this.hass.states[this._config[t]];let s=Object.keys(this.hass.states).find(i=>i.startsWith(`${e}.`)&&i.includes(t));return s?this.hass.states[s]:void 0}render(){if(!this.hass||!this._config)return d``;let e=this._l,t=this._zones(),s=this._findEntity("switch","summer_mode"),i=this._findEntity("switch","holiday_mode"),r=this._findEntity("switch","air_purge"),n=this._findEntity("sensor","master_state"),c=n&&(n.state!=="disabled"||t.some(h=>h.attributes.demand)),a=t.length?t[0].attributes.system_mode:void 0;return d`
      <ha-card class="glass">
        <div class="header">
          <div class="title">
            <ha-icon icon="mdi:heating-coil"></ha-icon>
            <span>${this._config.title}</span>
          </div>
          <div class="status">
            ${c?d`<span class="pill master ${n.state}">
                  ${e.master[n.state]||n.state}
                </span>`:""}
            ${a&&a!=="normal"?d`<span class="pill mode">
                  ${e.system[a]||a}
                </span>`:""}
          </div>
        </div>

        ${this._config.show_global?d`<div class="globals">
              ${this._globalButton(s,"mdi:weather-sunny",e.summer)}
              ${this._globalButton(i,"mdi:bag-suitcase",e.holiday)}
              ${this._globalButton(r,"mdi:air-filter",this._purgeLabel(r))}
            </div>`:""}

        <div class="zones">
          ${t.length?t.map(h=>this._renderZone(h)):d`<div class="empty">${e.empty}</div>`}
        </div>
      </ha-card>
    `}_purgeLabel(e){let t=this._l;if(!e||e.state!=="on")return t.air_purge;let s=e.attributes.remaining_seconds||0;return t.purge_left(Math.ceil(s/60))}_globalButton(e,t,s){if(!e)return"";let i=e.state==="on";return d`
      <button
        class="global ${i?"active":""}"
        @click=${()=>this._toggle(e.entity_id)}
        title=${s}
      >
        <ha-icon icon=${t}></ha-icon>
        <span>${s}</span>
      </button>
    `}_renderZone(e){let t=this._l,s=e.attributes,i=s.valve_state||"closed",r=s.fault,n=e.state==="off",c=s.current_temperature!==void 0&&s.current_temperature!==null?Number(s.current_temperature).toFixed(1):"--",a=this._view(e),h=a.temperature!==void 0&&a.temperature!==null?Number(a.temperature).toFixed(1):"--",p=s.locked_until>0,l=()=>this._moreInfo(e.entity_id);return d`
      <div class="zone ${n?"disabled":""} ${s.is_bypass?"bypass":""}">
        <div class="top">
          <div class="valve ${i}" @click=${l} title=${t.fault[r]||i}>
            ${this._valveIcon(i)}
          </div>
          <div class="name" @click=${l}>
            <span class="label">${s.friendly_name||e.entity_id}</span>
            ${s.is_bypass?d`<span class="tag">bypass</span>`:""}
          </div>
          ${r?d`<span class="notice fault">${t.fault[r]||r}</span>`:p?d`<span class="notice">
                  <ha-icon icon="mdi:lock-clock"></ha-icon>
                  ${t.min_cycle(Math.ceil(s.locked_until/60))}
                </span>`:""}
        </div>

        ${r&&t.fix[r]?d`<div class="hint">
              ${t.fix[r]}
              <code>
                ${r==="relay_missing"?s.relay_entity:s.sensor_entity}
              </code>
            </div>`:""}

        ${s.is_bypass?"":d`
              <div class="mid">
                <div class="now" @click=${l}>
                  <small>${t.now}</small>
                  <b>${c}<small>°C</small></b>
                </div>
                <div class="stepper">
                  <button
                    aria-label=${t.lower}
                    @click=${()=>this._nudge(e,-.5)}
                  >
                    <ha-icon icon="mdi:minus"></ha-icon>
                  </button>
                  <div class="set">${h}<small>°C</small></div>
                  <button
                    aria-label=${t.raise}
                    @click=${()=>this._nudge(e,.5)}
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
                  </button>
                </div>
              </div>
              <div class="presets">
                ${Te.map(m=>d`
                    <button
                      class=${a.preset===m?"on":""}
                      aria-pressed=${a.preset===m?"true":"false"}
                      @click=${()=>this._preset(e,m)}
                    >
                      ${t.presets[m]}
                    </button>
                  `)}
              </div>
            `}
        ${this._config.show_metrics?d`<div class="metrics">
              ${t.metrics(s.runtime_hours??0,s.cycles??0)}
            </div>`:""}
      </div>
    `}_valveIcon(e){let t=$e[e]||$e.closed,s=e==="closed";return d`
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
            d=${e==="fault"?Le:s?Ue:Re}
            fill=${s?t:"rgba(255,255,255,0.95)"}
          />
        </g>
      </svg>
    `}_toggle(e){this.hass.callService("switch","toggle",{entity_id:e})}_nudge(e,t){let s=e.attributes,i=Number(this._view(e).temperature??20),r=Number(s.min_temp??5),n=Number(s.max_temp??30),c=Math.min(n,Math.max(r,Math.round((i+t)*2)/2));this._remember(e,{temperature:c,preset:"none"}),this.hass.callService("climate","set_temperature",{entity_id:e.entity_id,temperature:c})}_preset(e,t){this._remember(e,{preset:t,temperature:void 0}),this.hass.callService("climate","set_preset_mode",{entity_id:e.entity_id,preset_mode:t})}_moreInfo(e){this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:e},bubbles:!0,composed:!0}))}static get styles(){return D`
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
    `}},X=class extends _{static get properties(){return{hass:{},_config:{}}}setConfig(e){this._config=e}get _schema(){return[{name:"title",selector:{text:{}}},{name:"zones",selector:{entity:{domain:"climate",multiple:!0}}},{name:"show_global",selector:{boolean:{}}},{name:"show_metrics",selector:{boolean:{}}}]}render(){return!this.hass||!this._config?d``:d`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._schema}
        .computeLabel=${e=>{let t=L(this.hass&&this.hass.language);return{title:t.editor_title,zones:t.editor_zones,show_global:t.editor_show_global,show_metrics:t.editor_show_metrics}[e.name]||e.name}}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `}_valueChanged(e){let t=new CustomEvent("config-changed",{detail:{config:e.detail.value},bubbles:!0,composed:!0});this.dispatchEvent(t)}};customElements.define("openhydronic-card",Q);customElements.define("openhydronic-card-editor",X);window.customCards=window.customCards||[];window.customCards.push({type:"openhydronic-card",name:"OpenHydronic Card",description:L(navigator.language).card_description,preview:!0,documentationURL:"https://github.com/davdlic/OpenHydronic-HA"});console.info(`%c OPENHYDRONIC-CARD %c ${He} `,"color:#fff;background:#fb8c00;font-weight:700;border-radius:4px 0 0 4px","color:#fb8c00;background:#222;border-radius:0 4px 4px 0");
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/lit-html.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/

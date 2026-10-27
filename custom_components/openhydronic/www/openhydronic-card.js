/*! OpenHydronic-HA - Copyright (C) 2026 David Lopes - GPL-3.0-or-later - https://github.com/davdlic/OpenHydronic-HA */
var H=globalThis,N=H.ShadowRoot&&(H.ShadyCSS===void 0||H.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,T=Symbol(),tt=new WeakMap,C=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==T)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(N&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=tt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&tt.set(e,t))}return t}toString(){return this.cssText}},et=o=>new C(typeof o=="string"?o:o+"",void 0,T),D=(o,...t)=>{let e=o.length===1?o[0]:t.reduce((s,i,r)=>s+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+o[r+1],o[0]);return new C(e,o,T)},st=(o,t)=>{if(N)o.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=H.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,o.appendChild(s)}},I=N?o=>o:o=>o instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return et(e)})(o):o;var{is:bt,defineProperty:yt,getOwnPropertyDescriptor:At,getOwnPropertyNames:wt,getOwnPropertySymbols:xt,getPrototypeOf:Ct}=Object,R=globalThis,it=R.trustedTypes,St=it?it.emptyScript:"",Et=R.reactiveElementPolyfillSupport,S=(o,t)=>o,B={toAttribute(o,t){switch(t){case Boolean:o=o?St:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,t){let e=o;switch(t){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},rt=(o,t)=>!bt(o,t),ot={attribute:!0,type:String,converter:B,reflect:!1,useDefault:!1,hasChanged:rt};Symbol.metadata??=Symbol("metadata"),R.litPropertyMetadata??=new WeakMap;var g=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=ot){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&yt(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:r}=At(this.prototype,t)??{get(){return this[e]},set(n){this[e]=n}};return{get:i,set(n){let c=i?.call(this);r?.call(this,n),this.requestUpdate(t,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??ot}static _$Ei(){if(this.hasOwnProperty(S("elementProperties")))return;let t=Ct(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(S("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(S("properties"))){let e=this.properties,s=[...wt(e),...xt(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(I(i))}else t!==void 0&&e.push(I(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return st(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let r=(s.converter?.toAttribute!==void 0?s.converter:B).toAttribute(e,s.type);this._$Em=t,r==null?this.removeAttribute(i):this.setAttribute(i,r),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let r=s.getPropertyOptions(i),n=typeof r.converter=="function"?{fromAttribute:r.converter}:r.converter?.fromAttribute!==void 0?r.converter:B;this._$Em=i;let c=n.fromAttribute(e,r.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(t,e,s,i=!1,r){if(t!==void 0){let n=this.constructor;if(i===!1&&(r=this[t]),s??=n.getPropertyOptions(t),!((s.hasChanged??rt)(r,e)||s.useDefault&&s.reflect&&r===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:r},n){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??e??this[t]),r!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,r]of this._$Ep)this[i]=r;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,r]of s){let{wrapped:n}=r,c=this[i];n!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,r,c)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};g.elementStyles=[],g.shadowRootOptions={mode:"open"},g[S("elementProperties")]=new Map,g[S("finalized")]=new Map,Et?.({ReactiveElement:g}),(R.reactiveElementVersions??=[]).push("2.1.2");var K=globalThis,nt=o=>o,U=K.trustedTypes,at=U?U.createPolicy("lit-html",{createHTML:o=>o}):void 0,ut="$lit$",$=`lit$${Math.random().toFixed(9).slice(2)}$`,mt="?"+$,Pt=`<${mt}>`,y=document,P=()=>y.createComment(""),z=o=>o===null||typeof o!="object"&&typeof o!="function",J=Array.isArray,zt=o=>J(o)||typeof o?.[Symbol.iterator]=="function",j=`[ 	
\f\r]`,E=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,lt=/-->/g,ct=/>/g,v=RegExp(`>|${j}(?:([^\\s"'>=/]+)(${j}*=${j}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ht=/'/g,dt=/"/g,gt=/^(?:script|style|textarea|title)$/i,Y=o=>(t,...e)=>({_$litType$:o,strings:t,values:e}),u=Y(1),jt=Y(2),Vt=Y(3),A=Symbol.for("lit-noChange"),p=Symbol.for("lit-nothing"),pt=new WeakMap,b=y.createTreeWalker(y,129);function _t(o,t){if(!J(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return at!==void 0?at.createHTML(t):t}var Mt=(o,t)=>{let e=o.length-1,s=[],i,r=t===2?"<svg>":t===3?"<math>":"",n=E;for(let c=0;c<e;c++){let a=o[c],h,d,l=-1,m=0;for(;m<a.length&&(n.lastIndex=m,d=n.exec(a),d!==null);)m=n.lastIndex,n===E?d[1]==="!--"?n=lt:d[1]!==void 0?n=ct:d[2]!==void 0?(gt.test(d[2])&&(i=RegExp("</"+d[2],"g")),n=v):d[3]!==void 0&&(n=v):n===v?d[0]===">"?(n=i??E,l=-1):d[1]===void 0?l=-2:(l=n.lastIndex-d[2].length,h=d[1],n=d[3]===void 0?v:d[3]==='"'?dt:ht):n===dt||n===ht?n=v:n===lt||n===ct?n=E:(n=v,i=void 0);let f=n===v&&o[c+1].startsWith("/>")?" ":"";r+=n===E?a+Pt:l>=0?(s.push(h),a.slice(0,l)+ut+a.slice(l)+$+f):a+$+(l===-2?c:f)}return[_t(o,r+(o[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},M=class o{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let r=0,n=0,c=t.length-1,a=this.parts,[h,d]=Mt(t,e);if(this.el=o.createElement(h,s),b.currentNode=this.el.content,e===2||e===3){let l=this.el.content.firstChild;l.replaceWith(...l.childNodes)}for(;(i=b.nextNode())!==null&&a.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let l of i.getAttributeNames())if(l.endsWith(ut)){let m=d[n++],f=i.getAttribute(l).split($),k=/([.?@])?(.*)/.exec(m);a.push({type:1,index:r,name:k[2],strings:f,ctor:k[1]==="."?W:k[1]==="?"?F:k[1]==="@"?q:x}),i.removeAttribute(l)}else l.startsWith($)&&(a.push({type:6,index:r}),i.removeAttribute(l));if(gt.test(i.tagName)){let l=i.textContent.split($),m=l.length-1;if(m>0){i.textContent=U?U.emptyScript:"";for(let f=0;f<m;f++)i.append(l[f],P()),b.nextNode(),a.push({type:2,index:++r});i.append(l[m],P())}}}else if(i.nodeType===8)if(i.data===mt)a.push({type:2,index:r});else{let l=-1;for(;(l=i.data.indexOf($,l+1))!==-1;)a.push({type:7,index:r}),l+=$.length-1}r++}}static createElement(t,e){let s=y.createElement("template");return s.innerHTML=t,s}};function w(o,t,e=o,s){if(t===A)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,r=z(t)?void 0:t._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),r===void 0?i=void 0:(i=new r(o),i._$AT(o,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=w(o,i._$AS(o,t.values),i,s)),t}var V=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??y).importNode(e,!0);b.currentNode=i;let r=b.nextNode(),n=0,c=0,a=s[0];for(;a!==void 0;){if(n===a.index){let h;a.type===2?h=new O(r,r.nextSibling,this,t):a.type===1?h=new a.ctor(r,a.name,a.strings,this,t):a.type===6&&(h=new Z(r,this,t)),this._$AV.push(h),a=s[++c]}n!==a?.index&&(r=b.nextNode(),n++)}return b.currentNode=y,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},O=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=p,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=w(this,t,e),z(t)?t===p||t==null||t===""?(this._$AH!==p&&this._$AR(),this._$AH=p):t!==this._$AH&&t!==A&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):zt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==p&&z(this._$AH)?this._$AA.nextSibling.data=t:this.T(y.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=M.createElement(_t(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let r=new V(i,this),n=r.u(this.options);r.p(e),this.T(n),this._$AH=r}}_$AC(t){let e=pt.get(t.strings);return e===void 0&&pt.set(t.strings,e=new M(t)),e}k(t){J(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let r of t)i===e.length?e.push(s=new o(this.O(P()),this.O(P()),this,this.options)):s=e[i],s._$AI(r),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=nt(t).nextSibling;nt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},x=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,r){this.type=1,this._$AH=p,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=r,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=p}_$AI(t,e=this,s,i){let r=this.strings,n=!1;if(r===void 0)t=w(this,t,e,0),n=!z(t)||t!==this._$AH&&t!==A,n&&(this._$AH=t);else{let c=t,a,h;for(t=r[0],a=0;a<r.length-1;a++)h=w(this,c[s+a],e,a),h===A&&(h=this._$AH[a]),n||=!z(h)||h!==this._$AH[a],h===p?t=p:t!==p&&(t+=(h??"")+r[a+1]),this._$AH[a]=h}n&&!i&&this.j(t)}j(t){t===p?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},W=class extends x{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===p?void 0:t}},F=class extends x{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==p)}},q=class extends x{constructor(t,e,s,i,r){super(t,e,s,i,r),this.type=5}_$AI(t,e=this){if((t=w(this,t,e,0)??p)===A)return;let s=this._$AH,i=t===p&&s!==p||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,r=t!==p&&(s===p||i);i&&this.element.removeEventListener(this.name,this,s),r&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},Z=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){w(this,t)}};var Ot=K.litHtmlPolyfillSupport;Ot?.(M,O),(K.litHtmlVersions??=[]).push("3.3.3");var ft=(o,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let r=e?.renderBefore??null;s._$litPart$=i=new O(t.insertBefore(P(),r),r,void 0,e??{})}return i._$AI(o),i};var G=globalThis,_=class extends g{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=ft(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return A}};_._$litElement$=!0,_.finalized=!0,G.litElementHydrateSupport?.({LitElement:_});var kt=G.litElementPolyfillSupport;kt?.({LitElement:_});(G.litElementVersions??=[]).push("4.2.2");var Ht="1.2.2",Nt="M17.66 11.2C17.43 10.9 17.15 10.64 16.89 10.38C16.22 9.78 15.46 9.35 14.82 8.72C13.33 7.26 13 4.85 13.95 3C13 3.23 12.17 3.75 11.46 4.32C8.87 6.4 7.85 10.07 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C6.87 12.33 6.69 10.28 7.45 8.64C5.78 10 4.87 12.3 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C18.86 17.66 19.5 15 18.56 12.72L18.43 12.46C18.22 12 17.66 11.2 17.66 11.2M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.78 14.43 12.46 13.77 12.33 13C12.21 12.26 12.23 11.63 12.5 10.94C12.69 11.32 12.89 11.7 13.13 12C13.9 13 15.11 13.44 15.37 14.8C15.41 14.94 15.43 15.08 15.43 15.23C15.46 16.05 15.1 16.95 14.5 17.5H14.5Z",Rt="M22.11 21.46L2.39 1.73L1.11 3L7.09 9C5.66 10.36 4.88 12.47 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C17.1 19.26 17.15 19.18 17.22 19.11L20.84 22.73L22.11 21.46M8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C7 12.47 6.74 10.69 7.26 9.15L8.58 10.47C8.58 11.4 8.73 12.33 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.66 15 12.66 14.76 12.64 14.53L15 16.88C14.85 17.11 14.69 17.33 14.5 17.5M18.92 15.72L9.65 6.46C10.12 5.65 10.72 4.92 11.46 4.32C12.17 3.75 13 3.23 13.95 3C13 4.85 13.33 7.26 14.82 8.72C15.46 9.35 16.22 9.78 16.89 10.38C17.15 10.64 17.43 10.9 17.66 11.2C17.66 11.2 18.22 12 18.43 12.46L18.56 12.72C18.96 13.69 19.06 14.72 18.92 15.72Z",Ut="M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",Lt=["comfort","eco","away"],$t={closed:"var(--oh-valve-closed)",opening:"var(--oh-valve-opening)",open:"var(--oh-valve-open)",fault:"var(--oh-valve-fault)"},vt={en:{card_title:"Heating",card_description:"Hydronic zone control with valve status, global modes and air purge.",empty:"No zones configured yet. Add them in Settings -> Devices & services -> OpenHydronic -> Configure.",summer:"Summer",holiday:"Holiday",air_purge:"Purge",now:"Now",lower:"Lower the setpoint",raise:"Raise the setpoint",presets:{comfort:"Comfort",eco:"Eco",away:"Away"},purge_left:o=>`Purge ${o} min`,min_cycle:o=>`minimum cycle ${o} min`,metrics:(o,t)=>`${o} h - ${t} cycles`,editor_title:"Title",editor_zones:"Zones (empty = auto-detect)",editor_show_global:"Show global controls",editor_show_metrics:"Show per-zone metrics",fault:{sensor_stale:"Sensor not updating",sensor_missing:"Sensor unavailable",relay_missing:"Relay unavailable"},master:{disabled:"Master disabled",off:"Master off",waiting:"Thermal delay...",on:"Circulator running",purging:"Purging heat..."},system:{normal:"Normal",summer:"Summer",holiday:"Holiday",air_purge:"Air purge",anti_seize:"Anti-seize"}},pt:{card_title:"Climatiza\xE7\xE3o",card_description:"Controlo de zonas hidr\xE1ulicas com estado das v\xE1lvulas, modos globais e purga de ar.",empty:"Sem zonas configuradas. Adicione-as em Defini\xE7\xF5es -> Dispositivos e servi\xE7os -> OpenHydronic -> Configurar.",summer:"Ver\xE3o",holiday:"F\xE9rias",air_purge:"Purga",now:"Agora",lower:"Baixar a temperatura",raise:"Subir a temperatura",presets:{comfort:"Conforto",eco:"Eco",away:"Ausente"},purge_left:o=>`Purga ${o} min`,min_cycle:o=>`ciclo m\xEDnimo ${o} min`,metrics:(o,t)=>`${o} h - ${t} ciclos`,editor_title:"T\xEDtulo",editor_zones:"Zonas (vazio = dete\xE7\xE3o autom\xE1tica)",editor_show_global:"Mostrar controlos globais",editor_show_metrics:"Mostrar m\xE9tricas por zona",fault:{sensor_stale:"Sensor sem atualiza\xE7\xE3o",sensor_missing:"Sensor indispon\xEDvel",relay_missing:"Rel\xE9 indispon\xEDvel"},master:{disabled:"Master desativado",off:"Master desligado",waiting:"Delay t\xE9rmico\u2026",on:"Circulador ativo",purging:"Purga t\xE9rmica\u2026"},system:{normal:"Normal",summer:"Ver\xE3o",holiday:"F\xE9rias",air_purge:"Purga de ar",anti_seize:"Anti-gripagem"}}};function L(o){return vt[String(o||"en").slice(0,2)]||vt.en}var Q=class extends _{static get properties(){return{hass:{},_config:{}}}static getStubConfig(t){let e=Object.keys(t.states).filter(s=>s.startsWith("climate.")&&t.states[s].attributes.valve_state!==void 0);return{type:"custom:openhydronic-card",title:L(t.language).card_title,zones:e}}static getConfigElement(){return document.createElement("openhydronic-card-editor")}setConfig(t){this._config={title:"OpenHydronic",show_global:!0,show_metrics:!1,...t}}getCardSize(){return 3+this._zones().length*3}get _l(){return L(this.hass&&this.hass.language)}_zones(){return this.hass?(this._config.zones&&this._config.zones.length?this._config.zones:Object.keys(this.hass.states).filter(e=>e.startsWith("climate.")&&this.hass.states[e].attributes.valve_state!==void 0)).map(e=>this.hass.states[e]).filter(Boolean):[]}_findEntity(t,e){if(this._config[e])return this.hass.states[this._config[e]];let s=Object.keys(this.hass.states).find(i=>i.startsWith(`${t}.`)&&i.includes(e));return s?this.hass.states[s]:void 0}render(){if(!this.hass||!this._config)return u``;let t=this._l,e=this._zones(),s=this._findEntity("switch","summer_mode"),i=this._findEntity("switch","holiday_mode"),r=this._findEntity("switch","air_purge"),n=this._findEntity("sensor","master_state"),c=e.length?e[0].attributes.system_mode:void 0;return u`
      <ha-card class="glass">
        <div class="header">
          <div class="title">
            <ha-icon icon="mdi:heating-coil"></ha-icon>
            <span>${this._config.title}</span>
          </div>
          <div class="status">
            ${n?u`<span class="pill master ${n.state}">
                  ${t.master[n.state]||n.state}
                </span>`:""}
            ${c&&c!=="normal"?u`<span class="pill mode">
                  ${t.system[c]||c}
                </span>`:""}
          </div>
        </div>

        ${this._config.show_global?u`<div class="globals">
              ${this._globalButton(s,"mdi:weather-sunny",t.summer)}
              ${this._globalButton(i,"mdi:bag-suitcase",t.holiday)}
              ${this._globalButton(r,"mdi:air-filter",this._purgeLabel(r))}
            </div>`:""}

        <div class="zones">
          ${e.length?e.map(a=>this._renderZone(a)):u`<div class="empty">${t.empty}</div>`}
        </div>
      </ha-card>
    `}_purgeLabel(t){let e=this._l;if(!t||t.state!=="on")return e.air_purge;let s=t.attributes.remaining_seconds||0;return e.purge_left(Math.ceil(s/60))}_globalButton(t,e,s){if(!t)return"";let i=t.state==="on";return u`
      <button
        class="global ${i?"active":""}"
        @click=${()=>this._toggle(t.entity_id)}
        title=${s}
      >
        <ha-icon icon=${e}></ha-icon>
        <span>${s}</span>
      </button>
    `}_renderZone(t){let e=this._l,s=t.attributes,i=s.valve_state||"closed",r=s.fault,n=t.state==="off",c=s.current_temperature!==void 0&&s.current_temperature!==null?Number(s.current_temperature).toFixed(1):"--",a=s.temperature!==void 0&&s.temperature!==null?Number(s.temperature).toFixed(1):"--",h=s.locked_until>0,d=()=>this._moreInfo(t.entity_id);return u`
      <div class="zone ${n?"disabled":""} ${s.is_bypass?"bypass":""}">
        <div class="top">
          <div class="valve ${i}" @click=${d} title=${e.fault[r]||i}>
            ${this._valveIcon(i)}
          </div>
          <div class="name" @click=${d}>
            ${s.friendly_name||t.entity_id}
            ${s.is_bypass?u`<span class="tag">bypass</span>`:""}
          </div>
          ${r?u`<span class="notice fault">${e.fault[r]||r}</span>`:h?u`<span class="notice">
                  <ha-icon icon="mdi:lock-clock"></ha-icon>
                  ${e.min_cycle(Math.ceil(s.locked_until/60))}
                </span>`:""}
        </div>

        ${s.is_bypass?"":u`
              <div class="mid">
                <div class="now" @click=${d}>
                  <small>${e.now}</small>
                  <b>${c}<small>°C</small></b>
                </div>
                <div class="stepper">
                  <button
                    aria-label=${e.lower}
                    @click=${()=>this._nudge(t,-.5)}
                  >
                    <ha-icon icon="mdi:minus"></ha-icon>
                  </button>
                  <div class="set">${a}<small>°C</small></div>
                  <button
                    aria-label=${e.raise}
                    @click=${()=>this._nudge(t,.5)}
                  >
                    <ha-icon icon="mdi:plus"></ha-icon>
                  </button>
                </div>
              </div>
              <div class="presets">
                ${Lt.map(l=>u`
                    <button
                      class=${s.preset_mode===l?"on":""}
                      aria-pressed=${s.preset_mode===l?"true":"false"}
                      @click=${()=>this._preset(t,l)}
                    >
                      ${e.presets[l]}
                    </button>
                  `)}
              </div>
            `}
        ${this._config.show_metrics?u`<div class="metrics">
              ${e.metrics(s.runtime_hours??0,s.cycles??0)}
            </div>`:""}
      </div>
    `}_valveIcon(t){let e=$t[t]||$t.closed,s=t==="closed";return u`
      <svg viewBox="0 0 48 48" aria-hidden="true">
        <circle cx="24" cy="24" r="21" class="halo" fill=${e} />
        <circle
          cx="24"
          cy="24"
          r="17"
          fill=${s?"none":e}
          stroke=${e}
          stroke-width="2.5"
        />
        <g transform="translate(10 10) scale(1.1667)">
          <path
            d=${t==="fault"?Ut:s?Rt:Nt}
            fill=${s?e:"rgba(255,255,255,0.95)"}
          />
        </g>
      </svg>
    `}_toggle(t){this.hass.callService("switch","toggle",{entity_id:t})}_nudge(t,e){let s=Number(t.attributes.temperature??20);this.hass.callService("climate","set_temperature",{entity_id:t.entity_id,temperature:Math.round((s+e)*2)/2})}_preset(t,e){this.hass.callService("climate","set_preset_mode",{entity_id:t.entity_id,preset_mode:e})}_moreInfo(t){this.dispatchEvent(new CustomEvent("hass-more-info",{detail:{entityId:t},bubbles:!0,composed:!0}))}static get styles(){return D`
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
    `}},X=class extends _{static get properties(){return{hass:{},_config:{}}}setConfig(t){this._config=t}get _schema(){return[{name:"title",selector:{text:{}}},{name:"zones",selector:{entity:{domain:"climate",multiple:!0}}},{name:"show_global",selector:{boolean:{}}},{name:"show_metrics",selector:{boolean:{}}}]}render(){return!this.hass||!this._config?u``:u`
      <ha-form
        .hass=${this.hass}
        .data=${this._config}
        .schema=${this._schema}
        .computeLabel=${t=>{let e=L(this.hass&&this.hass.language);return{title:e.editor_title,zones:e.editor_zones,show_global:e.editor_show_global,show_metrics:e.editor_show_metrics}[t.name]||t.name}}
        @value-changed=${this._valueChanged}
      ></ha-form>
    `}_valueChanged(t){let e=new CustomEvent("config-changed",{detail:{config:t.detail.value},bubbles:!0,composed:!0});this.dispatchEvent(e)}};customElements.define("openhydronic-card",Q);customElements.define("openhydronic-card-editor",X);window.customCards=window.customCards||[];window.customCards.push({type:"openhydronic-card",name:"OpenHydronic Card",description:L(navigator.language).card_description,preview:!0,documentationURL:"https://github.com/davdlic/OpenHydronic-HA"});console.info(`%c OPENHYDRONIC-CARD %c ${Ht} `,"color:#fff;background:#fb8c00;font-weight:700;border-radius:4px 0 0 4px","color:#fb8c00;background:#222;border-radius:0 4px 4px 0");
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

/* ================= sauvegarde : ce téléphone + GitHub ================= */
const GH = {owner:"yoeldahan", repo:"plan-dcg", branch:"data"};
const GH_RAW = "https://raw.githubusercontent.com/"+GH.owner+"/"+GH.repo+"/"+GH.branch+"/";
const GH_API = "https://api.github.com/repos/"+GH.owner+"/"+GH.repo+"/contents/";
const LS = {
  get(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } },
  set(k,v){ try{ localStorage.setItem(k,v); }catch(e){} },
  del(k){ try{ localStorage.removeItem(k); }catch(e){} }
};
const USER_COLS = new Set(["done","progress","skips","extras","scores","bilans"]);
function ghToken(){ return (LS.get("dcg-gh-token")||"").trim(); }
function localDocs(){
  const o = {};
  try{ for (let i=0;i<localStorage.length;i++){ const k = localStorage.key(i); if (k && k.startsWith("dcg2-")){ try{ o[k.slice(5)] = JSON.parse(localStorage.getItem(k)); }catch(e){} } } }catch(e){}
  return o;
}
function b64enc(s){ const b = new TextEncoder().encode(s); let bin = ""; for (let i=0;i<b.length;i+=0x8000) bin += String.fromCharCode.apply(null, b.subarray(i,i+0x8000)); return btoa(bin); }
function b64dec(s){ const bin = atob(String(s).replace(/\s/g,"")); const b = new Uint8Array(bin.length); for (let i=0;i<bin.length;i++) b[i] = bin.charCodeAt(i); return new TextDecoder().decode(b); }
function ghHeaders(json){ const h = {Authorization:"Bearer "+ghToken(), Accept:"application/vnd.github+json"}; if (json) h["Content-Type"] = "application/json"; return h; }
async function ghGet(path){
  const r = await fetch(GH_API+path+"?ref="+GH.branch, {headers:ghHeaders(), cache:"no-store"});
  if (!r.ok) return {status:r.status};
  const j = await r.json(); return {status:200, sha:j.sha, text: j.content ? b64dec(j.content) : ""};
}
function ghPut(path, text, sha){
  const body = {message:"Progression · "+new Date().toLocaleString("fr-FR"), content:b64enc(text), branch:GH.branch};
  if (sha) body.sha = sha;
  return fetch(GH_API+path, {method:"PUT", headers:ghHeaders(true), body:JSON.stringify(body)});
}
let ghSha = null, ghTimer = null, ghBusy = false, ghAgain = false, ghState = "off";
function syncLine(){
  if (!ghToken()) return "Tes coches sont gardées sur ce téléphone. Relie-les à ton coach dans Méthode.";
  if (ghState === "ok") return "Sauvegardé · ton coach voit ta progression.";
  if (ghState === "auth") return "Clé GitHub refusée : reconnecte-la dans Méthode.";
  if (ghState === "offline") return "Hors ligne : tes coches sont gardées ici, envoi dès que possible.";
  return "Sauvegarde…";
}
function ghQueue(delay){ if (!ghToken()) return; clearTimeout(ghTimer); ghTimer = setTimeout(()=>{ ghTimer = null; ghPush(); }, delay==null ? 6000 : delay); }
async function ghPush(){
  if (!ghToken()) return;
  if (ghBusy){ ghAgain = true; return; }
  ghBusy = true; ghState = "busy"; setSync(syncLine());
  try{
    const text = JSON.stringify({updatedAt:new Date().toISOString(), userAt:LS.get("dcg-user-at")||"", docs:localDocs()});
    if (ghSha === null){ const g = await ghGet("state.json"); if (g.status === 401 || g.status === 403) throw {auth:true}; ghSha = g.sha || ""; }
    let r = await ghPut("state.json", text, ghSha);
    if (r.status === 409 || r.status === 422){ const g = await ghGet("state.json"); ghSha = g.sha || ""; r = await ghPut("state.json", text, ghSha); }
    if (r.ok){ const j = await r.json(); ghSha = j.content && j.content.sha || null; ghState = "ok"; }
    else if (r.status === 401 || r.status === 403 || r.status === 404) ghState = "auth";
    else ghState = "offline";
  }catch(e){ ghState = e && e.auth ? "auth" : "offline"; }
  ghBusy = false; setSync(syncLine());
  if (ghAgain){ ghAgain = false; ghQueue(1500); }
}
function persist(path, data){
  LS.set("dcg2-"+path, JSON.stringify(data));
  if (USER_COLS.has(path.split("/")[0])) LS.set("dcg-user-at", new Date().toISOString());
  ghQueue();
  return Promise.resolve();
}
function remove(path){
  LS.del("dcg2-"+path);
  if (USER_COLS.has(path.split("/")[0])) LS.set("dcg-user-at", new Date().toISOString());
  ghQueue();
}
function loadLocal(){
  done = {}; progress = {}; skips = {}; extras = {}; scores = {}; bilans = {}; history = {};
  const o = localDocs();
  for (const path in o){
    const [col, id] = path.split("/"); const val = o[path];
    if (col==="done") done[id] = Object.assign({}, val.items||{});
    else if (col==="progress") progress[id] = val; else if (col==="skips") skips[id] = val; else if (col==="extras") extras[id] = val;
    else if (col==="scores") scores[id] = val; else if (col==="bilans") bilans[id] = val; else if (col==="history") history[id] = val;
  }
  migrateLegacy(progress);
}
async function loadCoach(){
  try{
    const r = await fetch(GH_RAW+"coach.json?t="+Date.now(), {cache:"no-store"});
    if (r.ok){ const c = await r.json(); overrides = c.overrides || {}; meta = c.meta || null; LS.set("dcg-coach", JSON.stringify(c)); refresh(); }
  }catch(e){}
}
async function loadRemote(){
  let remote = null;
  try{
    if (ghToken()){
      const g = await ghGet("state.json");
      if (g.status === 200){ ghSha = g.sha; remote = JSON.parse(g.text||"null"); }
      else if (g.status === 401 || g.status === 403){ ghState = "auth"; }
    } else {
      const r = await fetch(GH_RAW+"state.json?t="+Date.now(), {cache:"no-store"});
      if (r.ok) remote = await r.json();
    }
  }catch(e){ if (ghToken()) ghState = "offline"; }
  const lu = LS.get("dcg-user-at") || "";
  if (remote && remote.docs && (remote.userAt||"") > lu){
    for (const k of Object.keys(localDocs())) LS.del("dcg2-"+k);
    for (const p in remote.docs) LS.set("dcg2-"+p, JSON.stringify(remote.docs[p]));
    LS.set("dcg-user-at", remote.userAt || "");
    loadLocal(); lastHist = ""; lastComp = "";
    if (ghToken()) ghState = "ok";
  } else if (ghToken() && ghState !== "auth" && (!remote || lu > (remote.userAt||""))) ghQueue(1200);
  else if (ghToken() && ghState !== "auth" && ghState !== "offline") ghState = "ok";
  setSync(syncLine()); refresh();
}
function setSync(t){ document.getElementById("sync").textContent = t; }
(function(){
  try{ const c = JSON.parse(LS.get("dcg-coach")||"null"); if (c){ overrides = c.overrides || {}; meta = c.meta || null; } }catch(e){}
  loadLocal(); loaded = true; setSync(syncLine()); refresh();
  loadCoach(); loadRemote();
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "hidden"){ if (ghTimer){ clearTimeout(ghTimer); ghTimer = null; ghPush(); } }
    else { loadCoach(); }
  });
  window.addEventListener("online", () => { if (ghToken()) ghQueue(800); });
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(()=>{});
})();
/* ---- relier à GitHub ---- */
function openGitHub(){ sheetState = {type:"github"}; renderSheet(); openSheet(); }
function renderGitHub(sh){
  const has = !!ghToken();
  sh.append(h("div",{class:"grab"}));
  const inp = h("input",{type:"password",id:"gh-token",autocomplete:"off",autocapitalize:"off",spellcheck:"false",placeholder:"github_pat_…"});
  const body = h("div",{class:"body"},
    h("h2",{style:"font-size:1.25rem;margin-top:8px"}, has ? "Ton appli est reliée à ton coach" : "Relier l'appli à ton coach"),
    h("p",{class:"muted",style:"margin:0"}, "Avec une clé GitHub, tes coches sont sauvegardées dans ton dépôt plan-dcg. Je les lis le dimanche et le mardi pour ton planning et ton bilan. Sans clé, elles restent seulement sur ce téléphone."),
    h("ol",{class:"steps"},
      h("li",null,"Sur github.com, ouvre ton profil, puis Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token."),
      h("li",null,"Nom : plan-dcg. Expiration : Custom, choisis le 1er juillet 2027."),
      h("li",null,"Repository access : Only select repositories → plan-dcg."),
      h("li",null,"Permissions → Repository permissions → Contents : Read and write."),
      h("li",null,"Generate token, copie la clé (elle commence par github_pat_) et colle-la ici.")),
    h("div",{class:"field"}, h("label",{for:"gh-token"}, has ? "Remplacer la clé" : "Ta clé GitHub"), inp));
  sh.append(body);
  const foot = h("div",{class:"foot"});
  if (has) foot.append(h("button",{class:"btn soft",onclick:()=>{ LS.del("dcg-gh-token"); ghState = "off"; ghSha = null; setSync(syncLine()); closeSheet(); refresh(); toast("Clé retirée de ce téléphone."); }},"Déconnecter"));
  else foot.append(h("button",{class:"btn soft",onclick:closeSheet},"Plus tard"));
  foot.append(h("button",{class:"btn primary",onclick:async e=>{
    const v = inp.value.trim(); if (!v){ toast("Colle ta clé d'abord."); return; }
    const btn = e.currentTarget; btn.disabled = true; btn.textContent = "Vérification…";
    try{
      const r = await fetch(GH_API+"state.json?ref="+GH.branch, {headers:{Authorization:"Bearer "+v, Accept:"application/vnd.github+json"}, cache:"no-store"});
      if (r.status === 200 || r.status === 404){
        LS.set("dcg-gh-token", v); ghSha = null; ghState = "busy"; closeSheet(); refresh(); toast("C'est relié ! Ton coach voit ta progression."); ghPush();
      } else { btn.disabled = false; btn.textContent = "Enregistrer"; toast("Clé refusée : vérifie le dépôt plan-dcg et « Contents : Read and write »."); }
    }catch(err){ btn.disabled = false; btn.textContent = "Enregistrer"; toast("Pas de connexion. Réessaie dans un instant."); }
  }}, "Enregistrer"));
  sh.append(foot);
}

// AquaPredict Industrial Twin - Frontend App
// Vanilla JS + Chart.js + Leaflet.js

const API = 'http://127.0.0.1:8000/api/v1';
const H   = {'X-API-Key':'AQUA_SECURE_KEY_2026','Content-Type':'application/json'};

let lang='ar', theme='dark', autoRef=true, refTmr=null, user='', map=null, charts={};

// ── Translations ────────────────────────────────
const T = {
  ar:{
    appName:'AquaPredict',sub:'منصة الذكاء الصناعي للتحلية',ent:'النسخة المؤسسية - التوأم الرقمي',
    usr:'اسم المستخدم',pw:'كلمة المرور',lbtn:'تسجيل الدخول',lerr:'❌ بيانات الدخول غير صحيحة',
    online:'النظام متصل',welcome:'مرحباً',chpw:'تغيير كلمة المرور',npw:'كلمة المرور الجديدة',
    cpw:'تأكيد كلمة المرور',upd:'تحديث',cancel:'إلغاء',logout:'تسجيل الخروج',
    scen:'🎯 محرك السيناريوهات',sN:'الوضع الطبيعي الآمن',sF:'ترسبات الأغشية',
    sC:'تكهف المضخة',sA:'خطر الطحالب',sCy:'هجوم سيبراني',
    sens:'🎛️ لوحة الحساسات',pr:'الضغط',sal:'الملوحة',tmp:'درجة الحرارة',
    fl:'معدل التدفق',ph:'الحموضة',tb:'التعكر',vb:'الاهتزاز',pw2:'الطاقة',
    adv:'🧪 معاملات متقدمة',ma:'عمر الغشاء',genRpt:'📊 إنشاء تقرير PDF',
    autoR:'تحديث تلقائي',
    t1:'🎛️ غرفة التحكم',t2:'⚡ الكفاءة',t3:'🤖 AI Core',t4:'🚨 السيبراني',t5:'📜 التقارير',
    rs:'مستوى الخطورة',cf:'معامل الثقة',rl:'العمر المتبقي',mh:'صحة الأغشية',
    diag:'🧠 التشخيص التلقائي',rec:'📌 التوصية',hist:'📈 سجل الحساسات',
    sec:'استهلاك الطاقة (SEC)',ro:'نموذج RO الفيزيائي',foul:'نظام مكافحة الترسبات',
    fore:'التنبؤ للستة أشهر',
    ai1:'🧠 محرك الذكاء التفسيري',ai2:'🔬 وحدة الطحالب والتلوث',ai3:'⚡ محسّن أسعار الطاقة',
    tickets:'🎫 تذاكر الصيانة التنبؤية',cyberSim:'🔒 محاكاة الأمن السيبراني',
    atk:'🚨 محاكاة هجوم حقن بيانات',safe:'🟢 محاكاة حركة آمنة PLC',
    fwLogs:'📋 سجلات جدار الحماية',
    histLogs:'📋 السجلات التشغيلية التاريخية',exportT:'📜 تصدير البيانات',exportB:'📥 تجهيز وتحميل (CSV)',
    nodata:'لا توجد بيانات',err:'خطأ في الاتصال',
    pwok:'✅ تم تحديث كلمة المرور',pwmm:'⚠️ كلمات المرور غير متطابقة',
    pwsh:'⚠️ كلمة المرور قصيرة جداً',rptok:'✅ تم إنشاء التقرير',csvok:'✅ الملف جاهز للتحميل',
    ec:'استهلاك الطاقة',ef:'حالة الكفاءة',pm:'ملوحة النواتج',rc:'نسبة الاسترداد',
    sr:'معدل رفض الأملاح',sk:'الطاقة النوعية',fi:'مؤشر الترسبات',
    pi:'مؤشر انتشار البقعة',dm:'جرعة المعالجة (mg/L)',er:'مستوى الخطر البيئي',
    cr:'نسبة توفير التكاليف',oh:'ساعات التشغيل المثلى',ap:'متوسط سعر الكهرباء',
    epc:'سعر الكهرباء (EGP/kWh)',hr:'الساعة',mapT:'🗺️ التوأم الرقمي - محطة الغردقة',
    pressure:'الضغط (bar)',vibration:'الاهتزاز (mm/s)',turbidity:'التعكر (NTU)',
  },
  en:{
    appName:'AquaPredict',sub:'Industrial Water Intelligence Platform',ent:'Enterprise Edition - Digital Twin',
    usr:'Username',pw:'Password',lbtn:'Login',lerr:'❌ Invalid username or password',
    online:'System Online',welcome:'Welcome',chpw:'Change Password',npw:'New Password',
    cpw:'Confirm Password',upd:'Update',cancel:'Cancel',logout:'Logout',
    scen:'🎯 Scenario Engine',sN:'Normal Operation',sF:'Membrane Fouling',
    sC:'Pump Cavitation',sA:'Algal Bloom Risk',sCy:'Cyber Attack Simulation',
    sens:'🎛️ Sensor Controls',pr:'Pressure',sal:'Salinity',tmp:'Temperature',
    fl:'Flow Rate',ph:'pH Level',tb:'Turbidity',vb:'Vibration',pw2:'Power',
    adv:'🧪 Advanced Parameters',ma:'Membrane Age',genRpt:'📊 Generate PDF Report',
    autoR:'Auto Refresh',
    t1:'🎛️ SCADA Control',t2:'⚡ Efficiency',t3:'🤖 AI Core',t4:'🚨 Cyber',t5:'📜 Reports',
    rs:'Risk Score',cf:'Confidence',rl:'Remaining Life',mh:'Membrane Health',
    diag:'🧠 AI Diagnosis',rec:'📌 Recommendation',hist:'📈 Sensor History',
    sec:'Specific Energy Consumption (SEC)',ro:'Physics-Informed RO Model',foul:'Adaptive Fouling Mitigation',
    fore:'6-Month Predictive Forecast',
    ai1:'🧠 Explainable AI Decision Engine',ai2:'🔬 AI Plume & Dosing Engine',ai3:'⚡ Energy Market Optimizer',
    tickets:'🎫 AI Maintenance Tickets',cyberSim:'🔒 SCADA Cyber Simulation',
    atk:'🚨 Simulate Data Injection Attack',safe:'🟢 Simulate Safe PLC Traffic',
    fwLogs:'📋 SCADA Firewall Logs',
    histLogs:'📋 Operational Historical Store',exportT:'📜 Dataset Export',exportB:'📥 Prepare & Download CSV',
    nodata:'No data available',err:'Connection error',
    pwok:'✅ Password updated successfully',pwmm:'⚠️ Passwords do not match',
    pwsh:'⚠️ Password too short (min 4 chars)',rptok:'✅ Report generated',csvok:'✅ File ready for download',
    ec:'Energy Consumption',ef:'Efficiency Status',pm:'Permeate TDS',rc:'Recovery Rate',
    sr:'Salt Rejection',sk:'Specific Energy',fi:'Fouling Index',
    pi:'Plume Spread Index',dm:'Chemical Dosing (mg/L)',er:'Environmental Risk',
    cr:'Cost Reduction',oh:'Optimal Operating Hours',ap:'Avg. Electricity Price',
    epc:'Electricity Price (EGP/kWh)',hr:'Hour',mapT:'🗺️ Digital Twin - Hurghada Station',
    pressure:'Pressure (bar)',vibration:'Vibration (mm/s)',turbidity:'Turbidity (NTU)',
  }
};
const t = k => T[lang][k] || k;

// ── Lang & Theme ────────────────────────────────
function toggleLang(){
  lang = lang==='ar'?'en':'ar';
  const h=document.documentElement;
  h.lang=lang; h.dir=lang==='ar'?'rtl':'ltr';
  const b = document.getElementById('langBtn');
  if(b) b.textContent = lang==='ar'?'EN':'عربي';
  const b2 = document.getElementById('langBtnL');
  if(b2) b2.textContent = lang==='ar'?'English':'عربي';
  translate();
  // Re-render current tab with new language
  const dash = document.getElementById('dash');
  if(dash && !dash.classList.contains('hid')){
    loadTab(curTab);
  }
}
function toggleTheme(){
  theme=theme==='dark'?'light':'dark';
  document.documentElement.setAttribute('data-theme',theme);
  setTimeout(() => loadTab(curTab), 50);
  const icon=theme==='dark'?'🌙':'☀️';
  ['themeBtn','themeBtnL'].forEach(id=>{const e=document.getElementById(id);if(e)e.textContent=icon;});
}
function translate(){
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const k=el.getAttribute('data-i18n');
    if(T[lang][k]) el.textContent=T[lang][k];
  });
}

// ── Auth ────────────────────────────────────────
async function doLogin(){
  const un=document.getElementById('un').value.trim();
  const pw=document.getElementById('pw').value;
  const btn=document.getElementById('lbtn');
  const err=document.getElementById('lerr');
  if(!un||!pw)return;
  btn.disabled=true;
  btn.innerHTML='<span class="spin"></span>';
  err.classList.add('hid');
  try{
    const r=await fetch(`${API}/login`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:un,password:pw})});
    if(r.ok){
      const d=await r.json();
      user=d.username;
      showDash();
    } else {
      err.textContent=t('lerr');
      err.classList.remove('hid');
    }
  }catch(e){
    err.textContent=t('err')+': '+e.message;
    err.classList.remove('hid');
  } finally {
    btn.disabled=false;
    btn.innerHTML=`<span data-i18n="lbtn">${t('lbtn')}</span> <span>→</span>`;
  }
}
function doLogout(){
  document.getElementById('dash').classList.add('hid');
  document.getElementById('loginScreen').classList.remove('hid');
  stopRef();
  document.getElementById('uMenu').classList.add('hid');
}
function showDash(){
  document.getElementById('loginScreen').classList.add('hid');
  document.getElementById('dash').classList.remove('hid');
  const i=document.getElementById('uInitial');
  if(i) i.textContent=user.charAt(0).toUpperCase();
  const n=document.getElementById('uName');
  if(n) n.textContent=user;
  initMap();
  loadTab('scada');
  startRef();
}

// ── Clock ───────────────────────────────────────
function tickClock(){
  const e=document.getElementById('clk');
  if(e) e.textContent=new Date().toLocaleTimeString(lang==='ar'?'ar-EG':'en-US');
}

// ── Sidebar ─────────────────────────────────────
function toggleSidebar(){
  document.getElementById('sdb').classList.toggle('col');
  document.querySelector('.mc').classList.toggle('full');
}

// ── User menu ───────────────────────────────────
function toggleUM(){document.getElementById('uMenu').classList.toggle('hid')}
document.addEventListener('click',e=>{
  const ua=document.querySelector('.ua');
  const um=document.getElementById('uMenu');
  if(um&&!um.contains(e.target)&&ua&&!ua.contains(e.target)) um.classList.add('hid');
});

// ── Modal ───────────────────────────────────────
function showChPw(){
  document.getElementById('uMenu').classList.add('hid');
  document.getElementById('chPwModal').classList.remove('hid');
}
function closeModal(id){document.getElementById(id).classList.add('hid')}
async function submitChPw(){
  const np=document.getElementById('npw').value;
  const cp=document.getElementById('cpw').value;
  if(np!==cp){alert(t('pwmm'));return;}
  if(np.length<4){alert(t('pwsh'));return;}
  try{
    const r=await fetch(`${API}/change-password`,{method:'POST',headers:H,body:JSON.stringify({username:user,new_password:np})});
    if(r.ok){alert(t('pwok'));closeModal('chPwModal');}
  }catch(e){console.error(e);}
}

// ── Sliders & Payload ────────────────────────────
function payload(){
  const g=id=>parseFloat(document.getElementById(id)?.value||0);
  return {Pressure:g('pressure'),Salinity:g('salinity'),Temperature:g('temperature'),
          Flow_Rate:g('flowRate'),pH:g('ph'),Turbidity:g('turbidity'),Vibration:g('vibration')};
}
function desalPayload(){
  const p=payload();
  return {feed_tds_mgL:p.Salinity,feed_pressure_bar:p.Pressure,feed_temp_C:p.Temperature,
          feed_flow_m3h:p.Flow_Rate,membrane_age_months:parseFloat(document.getElementById('memAge')?.value||6)};
}

function updSlider(id){
  const el=document.getElementById(id);
  const vEl=document.getElementById(id+'V');
  if(el&&vEl) vEl.textContent=el.value;
  if(el){
    const mn=parseFloat(el.min),mx=parseFloat(el.max),v=parseFloat(el.value);
    const pct=((v-mn)/(mx-mn))*100;
    el.style.setProperty('--pct',pct+'%');
  }
}
function initSliders(){
  ['pressure','salinity','temperature','flowRate','ph','turbidity','vibration','power','memAge'].forEach(updSlider);
}

// ── Scenarios ────────────────────────────────────
const SCEN={
  normal:  {pressure:65,salinity:35000,temperature:25,flowRate:100,ph:7.5,turbidity:1.2,vibration:1.8,power:45},
  fouling: {pressure:86,salinity:36000,temperature:26,flowRate:95, ph:7.6,turbidity:3.4,vibration:2.3,power:52},
  cav:     {pressure:95,salinity:35000,temperature:25,flowRate:90, ph:7.5,turbidity:1.8,vibration:5.4,power:60},
  algae:   {pressure:70,salinity:35000,temperature:31,flowRate:95, ph:8.1,turbidity:4.8,vibration:2.1,power:48},
  cyber:   {pressure:110,salinity:40000,temperature:28,flowRate:110,ph:7.0,turbidity:6.2,vibration:4.0,power:70},
};
function applyScenario(){
  const s=SCEN[document.getElementById('scenSel')?.value];
  if(!s)return;
  Object.entries(s).forEach(([k,v])=>{const e=document.getElementById(k);if(e){e.value=v;updSlider(k);}});
  refreshAll();
}

// ── Tabs ─────────────────────────────────────────
let curTab='scada';
function showTab(name,btn){
  // Hide ALL tabs (add hid, remove act)
  document.querySelectorAll('.tc').forEach(e=>{
    e.classList.remove('act');
    e.classList.add('hid');
  });
  document.querySelectorAll('.tbb').forEach(e=>e.classList.remove('act'));
  // Show ONLY the target tab (remove hid, add act)
  const target = document.getElementById('tc-'+name);
  if(target){
    target.classList.remove('hid');
    target.classList.add('act');
  }
  btn?.classList.add('act');
  curTab=name;
  loadTab(name);
}
function loadTab(n){
  ({scada:loadScada,efficiency:loadEff,aicore:loadAI,cyber:loadCyber,reports:loadReports}[n]||loadScada)();
}

// ── API helpers ──────────────────────────────────
async function aPost(ep,body){const r=await fetch(API+ep,{method:'POST',headers:H,body:JSON.stringify(body)});return r.json();}
async function aGet(ep){const r=await fetch(API+ep,{headers:H});return r.json();}

// ── Map ──────────────────────────────────────────
function initMap(){
  if(map){map.remove();map=null;}
  const el=document.getElementById('stMap');
  if(!el||typeof L==='undefined')return;
  map=L.map('stMap').setView([27.2579,33.8116],11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap'}).addTo(map);
  const mk=L.marker([27.2579,33.8116],{
    icon:L.divIcon({html:'<div style="font-size:30px;filter:drop-shadow(0 0 10px #00d4ff)">💧</div>',className:'',iconSize:[36,36],iconAnchor:[18,36]})
  }).addTo(map);
  mk.bindPopup('<b>محطة تحلية الغردقة</b><br>Hurghada Desalination Station<br><small style="color:#00d4ff">نموذج محاكاة / Simulation Model</small>');
  L.polyline([[27.2979,33.7716],[27.2579,33.8116]],{color:'#00d4ff',weight:5,opacity:.8,dashArray:'10,5'}).addTo(map).bindTooltip('Marine Intake Pipeline');
}

// ── Gauge (Chart.js) ─────────────────────────────
function mkGauge(cid,val,mx,col){
  const ctx=document.getElementById(cid)?.getContext('2d');
  if(!ctx)return;
  const pct=Math.min(val/mx,1);
  if(charts[cid])charts[cid].destroy();
  charts[cid]=new Chart(ctx,{
    type:'doughnut',
    data:{datasets:[{data:[pct,1-pct],backgroundColor:[col,theme==='dark'?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.1)'],borderWidth:0,circumference:270,rotation:225}]},
    plugins:[{id:'ct',afterDraw(c){
      const {ctx:x,chartArea:{width:w,height:h,top,left:l}}=c;
      x.save();x.font=`bold ${Math.floor(w/5.5)}px Inter,Cairo,sans-serif`;
      x.fillStyle=col;x.textAlign='center';x.textBaseline='middle';
      x.fillText(val.toFixed(1),l+w/2,top+h/2+8);x.restore();
    }}],
    options:{responsive:true,animation:{duration:700,easing:'easeInOutQuart'},plugins:{legend:{display:false},tooltip:{enabled:false}},cutout:'76%'}
  });
}
function renderGauges(p){
  const pc=p.Pressure>95?'#ff4444':p.Pressure>80?'#ffa726':'#00d4ff';
  const vc=p.Vibration>4.5?'#ff4444':p.Vibration>3?'#ffa726':'#00e676';
  const tc=p.Turbidity>2.5?'#ff4444':'#a855f7';
  mkGauge('gPressure',p.Pressure,250,pc);
  mkGauge('gVibration',p.Vibration,100,vc);
  mkGauge('gTurbidity',p.Turbidity,100,tc);
}

// ── KPI Cards ─────────────────────────────────────
function renderKPIs(dec,rul){
  const el=document.getElementById('kpiRow');if(!el)return;
  const sev=dec.severity||'LOW';
  const sc=sev==='CRITICAL'?'neg':sev==='HIGH'?'neu':'pos';
  el.innerHTML=
    kpiCard(t('rs'),`${dec.risk_score}/100`,sev,sc)+
    kpiCard(t('cf'),`${dec.confidence_score}%`,'','')+
    kpiCard(t('rl'),`${rul.estimated_remaining_days} ${lang==='ar'?'يوم':'d'}`,'',rul.estimated_remaining_days>180?'pos':'neu')+
    kpiCard(t('mh'),rul.membrane_health_status||'-','',rul.membrane_health_status==='Good'?'pos':'neu');
}
function kpiCard(lbl,val,delta,cls){
  return `<div class="gc kpi"><span class="kv">${val}</span>${delta?`<span class="kd ${cls}">${delta}</span>`:''}<span class="kl">${lbl}</span></div>`;
}

// ── Diagnosis ─────────────────────────────────────
function renderDiag(d){
  const el=document.getElementById('diagCard');if(!el)return;
  const sev=d.severity||'LOW';
  el.className=`gc dg${sev==='CRITICAL'?' dng':sev==='HIGH'?' wrn':''}`;
  const diag = (lang==='en' && d.diagnosis_en) ? d.diagnosis_en : txApi(d.diagnosis||'-');
  const rec  = (lang==='en' && d.recommendation_en) ? d.recommendation_en : txApi(d.recommendation||'-');
  el.innerHTML=`<p><strong style="color:var(--acc)">${t('diag')}:</strong> ${diag}</p><p style="margin-top:8px"><strong style="color:var(--acc)">${t('rec')}:</strong> ${rec}</p>`;
}

// ── Line Chart ─────────────────────────────────────
function renderHistory(logs){
  const ctx=document.getElementById('histChart')?.getContext('2d');
  if(!ctx||!logs.length)return;
  const lb=logs.slice(-20).map(l=>l[1]?.substring(11,19)||'');
  const pr=logs.slice(-20).map(l=>l[2]||0);
  const vb=logs.slice(-20).map(l=>l[4]||0);
  if(charts.hist)charts.hist.destroy();
  charts.hist=new Chart(ctx,{type:'line',data:{labels:lb,datasets:[
    {label:t('pressure'),data:pr,borderColor:'#00d4ff',backgroundColor:'rgba(0,212,255,0.1)',tension:.4,fill:true,pointRadius:3},
    {label:t('vibration'),data:vb,borderColor:'#00e676',backgroundColor:'rgba(0,230,118,0.1)',tension:.4,fill:true,pointRadius:3},
  ]},options:{responsive:true,animation:{duration:600},plugins:{legend:{labels:{color:theme==='dark'?'#e8f4ff':'#1a202c',font:{family:'Cairo,Inter'}}}},scales:{x:{ticks:{color:theme==='dark'?'#8ab4d4':'#4a5568'},grid:{color:theme==='dark'?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.1)'}},y:{ticks:{color:theme==='dark'?'#8ab4d4':'#4a5568'},grid:{color:theme==='dark'?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.1)'}}}}});
}
function renderForecast(fc){
  const ctx=document.getElementById('foreChart')?.getContext('2d');
  if(!ctx||!fc.length)return;
  if(charts.fore)charts.fore.destroy();
  charts.fore=new Chart(ctx,{type:'line',data:{labels:fc.map(f=>txApi(f.month||'')),datasets:[
    {label:'TDS (mg/L)',data:fc.map(f=>f.predicted_tds),borderColor:'#ffa726',backgroundColor:'rgba(255,167,38,.1)',tension:.4,yAxisID:'y'},
    {label:'SEC (kWh/m³)',data:fc.map(f=>f.predicted_sec),borderColor:'#a855f7',backgroundColor:'rgba(168,85,247,.1)',tension:.4,yAxisID:'y1'},
  ]},options:{responsive:true,plugins:{legend:{labels:{color:theme==='dark'?'#e8f4ff':'#1a202c'}}},scales:{x:{ticks:{color:theme==='dark'?'#8ab4d4':'#4a5568'},grid:{color:theme==='dark'?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.1)'}},y:{position:'left',ticks:{color:'#ffa726'},grid:{color:theme==='dark'?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.1)'}},y1:{position:'right',ticks:{color:'#a855f7'},grid:{drawOnChartArea:false}}}}});
}
function renderEnergy(prices){
  const ctx=document.getElementById('energyChart')?.getContext('2d');
  if(!ctx||!prices)return;
  if(charts.energy)charts.energy.destroy();
  const colors=prices.map(p=>p<=3.5?'rgba(0,230,118,.8)':p>=6?'rgba(255,68,68,.8)':'rgba(0,212,255,.8)');
  charts.energy=new Chart(ctx,{type:'bar',data:{labels:Array.from({length:24},(_,i)=>`${i}:00`),datasets:[{label:t('epc'),data:prices,backgroundColor:colors,borderRadius:5,borderWidth:0}]},options:{responsive:true,plugins:{legend:{labels:{color:theme==='dark'?'#e8f4ff':'#1a202c'}}},scales:{x:{ticks:{color:theme==='dark'?'#8ab4d4':'#4a5568'},grid:{color:theme==='dark'?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.1)'}},y:{ticks:{color:theme==='dark'?'#8ab4d4':'#4a5568'},grid:{color:theme==='dark'?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.1)'}}}}});
}


// ── AR→EN Translation Dictionary for API Responses ────────────────────
const AR2EN = {
  // Severity
  "منخفض": "Low", "متوسط": "Medium", "مرتفع": "High", "حرج": "Critical",
  // Station status
  "طبيعي": "Normal", "تحذير": "Warning", "خطر": "Danger", "حرج": "Critical",
  // Membrane health
  "جيدة": "Good", "تحتاج فحص": "Needs Inspection", "سيئة": "Poor",
  // Fouling
  "الغشاء في حالة جيدة": "Membrane in good condition",
  "تحذير: بدء تراكم الترسبات": "Warning: Fouling buildup detected",
  "خطر: ترسبات شديدة": "Danger: Severe fouling detected",
  "تشغيل عملية التنظيف الكيميائي": "Initiating chemical cleaning process",
  "جاري تحليل بيانات الترسبات": "Analyzing fouling data",
  // Diagnosis patterns
  "الضغط مرتفع": "High pressure detected",
  "الضغط منخفض": "Low pressure detected",
  "الضغط طبيعي": "Pressure normal",
  "الاهتزاز مرتفع": "High vibration detected",
  "الاهتزاز طبيعي": "Vibration normal",
  "درجة الحرارة مرتفعة": "High temperature detected",
  "التعكر مرتفع": "High turbidity detected",
  "تدفق مرتفع": "High flow rate",
  "تدفق منخفض": "Low flow rate",
  "الملوحة مرتفعة": "High salinity detected",
  // Recommendations
  "يُنصح بالفحص الدوري": "Periodic inspection recommended",
  "استدعاء فريق الصيانة فوراً": "Dispatch maintenance team immediately",
  "مراقبة المحطة عن كثب": "Monitor station closely",
  "تشغيل نظام مكافحة التكلس": "Activate anti-scaling system",
  "فحص المضخة": "Inspect pump",
  "تنظيف المرشحات": "Clean filters",
  "مراجعة نظام التحكم": "Review control system",
  "خفض الضغط تدريجياً": "Gradually reduce pressure",
  "زيادة جرعة مواد المعالجة": "Increase treatment chemical dosing",
  // Cyber
  "حركة مرور آمنة": "Safe traffic detected",
  "هجوم محتمل": "Potential attack detected",
  "تم الحظر": "Blocked",
  "مسموح": "Allowed",
  // General
  "جيد": "Good", "ممتاز": "Excellent", "مقبول": "Acceptable",
  "حرج للغاية": "Extremely Critical",
  "لا توجد بيانات": "No data available",
  "خطأ في الاتصال": "Connection error",
  // Risk levels
  "منخفض الخطورة": "Low Risk", "متوسط الخطورة": "Medium Risk",
  "مرتفع الخطورة": "High Risk", "خطر شديد": "Critical Risk",
  // Energy
  "استهلاك مرتفع": "High consumption", "استهلاك منخفض": "Low consumption",
  "كفاءة عالية": "High efficiency", "كفاءة منخفضة": "Low efficiency",
  // Plume/Environmental
  "خطر بيئي منخفض": "Low Environmental Risk",
  "خطر بيئي متوسط": "Medium Environmental Risk",
  "خطر بيئي مرتفع": "High Environmental Risk",
  "تحليل البقعة": "Plume analysis",
  "جرعة المعالجة": "Treatment dosing",
};

const EN2AR = Object.fromEntries(Object.entries(AR2EN).map(([k,v])=>[v,k]));

/**
 * Translate API response text based on current language.
 * If lang=en, translate Arabic→English.
 * If lang=ar, keep Arabic (or translate English→Arabic).
 * Falls back to original text if no translation found.
 */
function txApi(text) {
  if (text === null || text === undefined) return '-';
  if (typeof text !== 'string') return String(text);
  if (lang !== 'en') return text; // keep Arabic as-is
  if (!text.trim()) return text;

  // 1. Exact dictionary match
  if (AR2EN[text]) return AR2EN[text];

  // 2. Pattern-based translations (regex)
  const PATTERNS = [
    // Months
    [/الشهر\s*(\d+)/g, 'Month $1'],
    // Maintenance ticket descriptions
    [/بداية ترسبات وتغيرات في غشاء الغشاء التناضحي.*?(?:\(RO Membrane Fouling\)\.?)?/g, 'Initial fouling in RO membrane (RO Membrane Fouling).'],
    [/خطر: ارتفاع حاد في أجهزة الضغط.*?$/gm, 'Danger: Sharp pressure increase - station pump may be affected.'],
    [/خطر:\s*ارتفاع/g, 'Danger: Pressure spike'],
    [/بداية ترسبات/g, 'Initial fouling buildup'],
    [/وتغيرات في غشاء/g, ' changes in membrane'],
    // Actions in logs
    [/مراقبة المحطة الانتقالية وانتصار من الانتقال الطارئ/g, 'Emergency transition monitoring - station status tracking.'],
    [/حركة دورية عمل عكسي وإطلاق نبضات مضغوطة لتقليت الترواب/g, 'Backwash cycle initiated - compressed pulses for fouling reduction.'],
    [/مراقبة المحطة.*?الطارئ/g, 'Emergency station monitoring.'],
    [/حركة دورية عمل عكسي/g, 'Periodic backwash cycle.'],
    [/مراقبة المحطة/g, 'Station monitoring.'],
    // Technician names
    [/م\.\s*محمود أنور/g, 'Eng. Mahmoud Anwar'],
    [/م\.\s*أحمد/g, 'Eng. Ahmed'],
    [/م\.\s*خالد/g, 'Eng. Khaled'],
    [/م\.\s*علي/g, 'Eng. Ali'],
    [/م\.\s*محمد/g, 'Eng. Mohamed'],
    [/م\.\s*كريم/g, 'Eng. Karim'],
    [/م\.\s*عمر/g, 'Eng. Omar'],
    [/م\.\s*يوسف/g, 'Eng. Youssef'],
    [/م\.\s*حسين/g, 'Eng. Hussein'],
    [/م\.\s*سامي/g, 'Eng. Sami'],
    // Critical remaining Arabic substrings
    [/الغشاء التناضحي/g, 'RO membrane'],
    [/الغشاء/g, 'membrane'],
    [/التناضح العكسي/g, 'reverse osmosis'],
    [/م\.\s*محمود الباز/g, 'Eng. Mahmoud Al-Baz'],
    [/م\.\s*محمود/g, 'Eng. Mahmoud'],
    [/م\.\s*الباز/g, 'Eng. Al-Baz'],
    // Fouling messages
    [/محاكاة تكيفية.*?الرواسب\.?/g, 'Adaptive simulation: micro-pulse fouling removal.'],
    [/حالة الأغشية مستقرة/g, 'Membrane status stable.'],
    [/رصد الترسبات/g, 'Fouling monitoring'],
    // Plume notes
    [/مؤشر مرتفع.*?المعالجة/g, 'High index - increase chlorine dosing and activate pre-filters.'],
    [/مستوى مقبول.*?الدوري/g, 'Acceptable level - continue periodic monitoring.'],
    [/مستوى معتدل.*?البقعة/g, 'Moderate level - continue periodic plume monitoring.'],
    [/استمر بالرصد الدوري/g, 'Continue periodic monitoring.'],
    [/استمر بالرصد الدوري للبقعة/g, 'Continue periodic plume monitoring.'],
    // Energy optimizer
    [/شغّل المضخات الثقيلة/g, 'Run heavy pumps'],
    [/للاستفادة من أقل أسعار الكهرباء/g, 'to benefit from lowest electricity prices.'],
    [/أسعار الكهرباء مستقرة/g, 'Electricity prices stable.'],
    [/استمر بالجدول الطبيعي/g, 'Continue normal schedule.'],
    // Action strings in logs
    [/متابعة المراقبة اللحظية/g, 'Continue real-time monitoring'],
    [/استمرار التشغيل المتوازن/g, 'maintain balanced operation.'],
    [/إيقاف طارئ محاكى للمضخة/g, 'Simulated emergency pump shutdown'],
    [/جدولة دورة غسيل عكسي/g, 'Schedule backwash cycle'],
    [/إطلاق نبضات ضغط ترددية/g, 'trigger pressure pulses'],
    // Misc
    [/تفتيت الرواسب/g, 'break down deposits'],
    [/فحص محاور الدوران/g, 'inspect shaft bearings'],
    [/رومان البلي/g, 'pump bearings'],
    [/فوراً/g, 'immediately'],
    // Status
    [/طبيعي/g, 'Normal'], [/تحذير/g, 'Warning'],
    [/حرج/g, 'Critical'], [/مرتفع/g, 'High'],
    [/منخفض/g, 'Low'], [/متوسط/g, 'Medium'],
    // Common action words
    [/مراقبة/g, 'Monitor'],
    [/تشغيل/g, 'Activate'],
    [/إيقاف/g, 'Stop'],
    [/فحص/g, 'Inspect'],
    [/تنظيف/g, 'Clean'],
    [/إنذار/g, 'Alert'],
    [/تحقق/g, 'Verify'],
    [/صيانة/g, 'Maintenance'],
    [/انتهى/g, 'Completed'],
    [/جاري/g, 'In Progress'],
    [/معلق/g, 'Pending'],
  ];

  let result = text;
  PATTERNS.forEach(([pattern, replacement]) => {
    result = result.replace(pattern, replacement);
  });

  // 3. Final fallback: replace any remaining Arabic char sequences with '?'
  // (only if result still has Arabic)
  // Uncomment if you want to hide untranslated Arabic:
  // result = result.replace(/[\u0600-\u06FF]+/g, '[...]');

  return result;
}

// ── Helpers ───────────────────────────────────────
function progBar(v,mx){
  const p=Math.min((v/mx)*100,100);
  const c=p>70?'#ff4444':p>40?'#ffa726':'#00d4ff';
  return `<div class="pb"><div class="pf" style="width:${p}%;background:linear-gradient(90deg,${c},${c}88)"></div></div>`;
}
function bdg(txt){
  const pos=['SECURE','NORMAL_ACOUSTIC','ALLOW_TRAFFIC','LOW_RISK','Good','Optimal','Open'];
  const neg=['BLOCKED','CRITICAL','HIGH_BIOLOGICAL_RISK','HIGH_ENERGY_CONSUMPTION','Needs_Inspection','BLOCKED_THREAT'];
  const wrn=['MODERATE_RISK','HIGH','Pending'];
  const cls=neg.includes(txt)?'berr':pos.includes(txt)?'bsuc':wrn.includes(txt)?'bwrn':'binf';
  return `<span class="bdg ${cls}">${txt||'-'}</span>`;
}
function mi(lbl,val){return `<div class="mi"><div class="mv">${val}</div><div class="ml">${lbl}</div></div>`;}
function mkTbl(cid,cols,rows){
  const el=document.getElementById(cid);if(!el)return;
  if(!rows.length){el.innerHTML=`<p style="color:var(--muted);padding:14px;text-align:center">${t('nodata')}</p>`;return;}
  const th=cols.map(c=>`<th>${c}</th>`).join('');
  const tr=rows.map(r=>`<tr>${r.map(c=>{
    const v=c??'-';
    const s=String(v);
    // Only translate plain text, not HTML (badges/icons already contain translated keys)
    const display = (s.includes('<') || s==='✅' || s==='⚠️') ? s : txApi(s);
    return `<td>${display}</td>`;
  }).join('')}</tr>`).join('');
  el.innerHTML=`<div class="tbl-wrap"><table class="tbl"><thead><tr>${th}</tr></thead><tbody>${tr}</tbody></table></div>`;
}


// ── Error Display Helper ──────────────────────────────
function showErr(containerId, msg) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `
    <div style="padding:24px;text-align:center;color:var(--err)">
      <div style="font-size:32px;margin-bottom:10px">⚠️</div>
      <div style="font-size:13px;color:var(--txt2)">${msg || 'Server connection error'}</div>
      <button onclick="refreshAll()" style="margin-top:12px;padding:6px 16px;border-radius:8px;border:1px solid var(--err);background:rgba(255,68,68,.1);color:var(--err);cursor:pointer;font-family:inherit;font-size:12px">↻ Retry</button>
    </div>`;
}
function showLoading(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = '<div style="padding:20px;text-align:center"><span class="spin"></span></div>';
}
// ── Tab: SCADA ────────────────────────────────────
async function loadScada(){
  const p=payload();
  renderGauges(p);
  showLoading('kpiRow');
  try{
    const [dec,rul,logs]=await Promise.all([aPost('/decision-engine',p),aPost('/predict-rul',p),aGet('/logs')]);
    renderKPIs(dec,rul);
    renderDiag(dec);
    renderHistory(logs.recent_logs||[]);
  }catch(e){
    console.error('SCADA:',e);
    showErr('kpiRow', 'API Error: ' + e.message);
    showErr('diagCard', 'Could not load data. Is the server running?');
  }
}

// ── Tab: Efficiency ───────────────────────────────
async function loadEff(){
  const p=payload(),pw=parseFloat(document.getElementById('power')?.value||45);
  showLoading('secM');showLoading('roM');
  try{
    const [sec,ro,foul,fore]=await Promise.all([
      aPost(`/energy-efficiency?power_kw=${pw}`,p),
      aPost('/predict-desalination-performance',desalPayload()),
      aPost('/self-healing-pulse',p),
      aPost('/forecast',p)
    ]);
    document.getElementById('secM').innerHTML=mi(t('ec'),`${sec.specific_energy_consumption_kwh_m3} kWh/m³`)+mi(t('ef'),bdg(sec.efficiency_status));
    const pr=ro.predictions||{};
    document.getElementById('roM').innerHTML=mi(t('pm'),`${pr.permeate_tds_mgL} mg/L`)+mi(t('rc'),`${pr.recovery_pct}%`)+mi(t('sr'),`${pr.salt_rejection_pct}%`)+mi(t('sk'),`${pr.sec_kwh_m3} kWh/m³`);
    const fi2=foul.calculated_fouling_index||0;
    const fc=fi2>65?'var(--err)':'var(--acc)';
    document.getElementById('foulM').innerHTML=`<div style="display:flex;align-items:center;gap:14px;margin-bottom:10px"><span style="font-size:30px;font-weight:700;color:${fc}">${fi2.toFixed(1)}</span><span style="color:var(--txt2)">${t('fi')}</span>${bdg(fi2>65?'CRITICAL':'SECURE')}</div>${progBar(fi2,150)}<p style="color:var(--txt2);font-size:12px;margin-top:6px">${(lang==='en'&&foul.message_en)?foul.message_en:txApi(foul.message||'')}</p>`;
    renderForecast(fore.forecast||[]);
  }catch(e){
    console.error('Efficiency:',e);
    showErr('secM', 'API Error: ' + e.message);
    showErr('roM', 'Could not load data.');
    showErr('foulM', 'Could not load data.');
  }
}

// ── Tab: AI Core ──────────────────────────────────
async function loadAI(){
  const p=payload();
  showLoading('aiDecM');showLoading('plumeM');
  try{
    const [dec,plume,en]=await Promise.all([
      aPost('/decision-engine',p),
      aPost('/advanced-ai-plume-analysis',{Turbidity:p.Turbidity,Temperature:p.Temperature,Salinity:p.Salinity}),
      aPost('/energy-market-optimizer',{})
    ]);
    const sev=dec.severity||'LOW';
    document.getElementById('aiDecM').innerHTML=`<div class="mg">${mi(t('rs'),`${dec.risk_score}/100 ${bdg(sev)}`)}${mi(t('cf'),`${dec.confidence_score}%`)}</div><div style="margin-top:14px;padding:14px;border-radius:10px;background:theme==='dark'?'rgba(255,255,255,.04)':'rgba(0,0,0,.04)'"><p><strong style="color:var(--acc)">${t('diag')}:</strong><br>${(lang==='en' && dec.diagnosis_en) ? dec.diagnosis_en : txApi(dec.diagnosis||'-')}</p><p style="margin-top:8px"><strong style="color:var(--acc)">${t('rec')}:</strong><br>${(lang==='en' && dec.recommendation_en) ? dec.recommendation_en : txApi(dec.recommendation||'-')}</p></div>`;
    document.getElementById('plumeM').innerHTML=`<div class="mg">${mi(t('pi'),plume.plume_spread_index)}${mi(t('dm'),`${plume.recommended_chemical_dosing_mgl} mg/L`)}${mi(t('er'),bdg(plume.environmental_risk_status))}${mi('Model',`<small style="color:var(--muted)">${plume.model_type||'-'}</small>`)}</div><p style="margin-top:10px;color:var(--txt2);font-size:12px">${(lang==='en'&&plume.analysis_notes_en)?plume.analysis_notes_en:txApi(plume.analysis_notes||'')}</p>`;
    document.getElementById('enM').innerHTML=`<div class="mg" style="margin-bottom:12px">${mi(t('cr'),`${en.estimated_energy_cost_reduction_pct}%`)}${mi(t('ap'),`${en.average_price_egp_kwh} EGP`)}</div><p style="color:var(--txt2);font-size:12px;margin-bottom:6px">${(lang==='en'&&en.recommendation_en)?en.recommendation_en:txApi(en.recommendation||'')}</p><p style="color:var(--acc);font-size:12px"><strong>${t('oh')}:</strong> ${(en.optimal_heavy_pumping_hours||[]).slice(0,6).join(', ')}:00</p>`;
    renderEnergy(en.hourly_prices);
  }catch(e){
    console.error('AI Core:',e);
    showErr('aiDecM', 'AI API Error: ' + e.message);
    showErr('plumeM', 'Could not load plume data.');
    showErr('enM', 'Could not load energy data.');
  }
}

// ── Tab: Cyber ────────────────────────────────────
async function loadCyber(){
  try{
    const [tk,cl]=await Promise.all([aGet('/maintenance-tickets'),aGet('/cybersecurity-logs')]);
    const tickets=tk.tickets||[];
    mkTbl('ticketsTbl',['ID','Timestamp','Priority','Description','Technician','Status'],tickets.map(r=>[r[0],r[1],bdg(r[2]),r[3],r[4],bdg(r[5])]));
    const clogs=cl.cyber_logs||[];
    mkTbl('fwTbl',['ID','Timestamp','Source IP','Attack Type','Action','Status'],clogs.map(r=>[r[0],r[1],r[2],r[3],r[4],bdg(r[5])]));
  }catch(e){
    console.error('Cyber:',e);
    showErr('ticketsTbl', 'API Error: ' + e.message);
    showErr('fwTbl', 'Could not load firewall logs.');
  }
}

// ── Tab: Reports ──────────────────────────────────
async function loadReports(){
  try{
    const d=await aGet('/logs');
    const logs=d.recent_logs||[];
    mkTbl('histTbl',['ID','Timestamp','Pressure','Turbidity','Vibration','Anomaly','Status','Action'],logs.map(l=>l.map((v,i)=>i===5?(v?'⚠️':'✅'):v)));
  }catch(e){
    console.error('Reports:',e);
    showErr('histTbl', 'API Error: ' + e.message);
  }
}

// ── Cyber Simulation ──────────────────────────────
async function doAtk(){
  try{
    const d=await aPost('/cybersecurity-scan',{source_ip:'192.168.1.99',sensor_pressure:110,sensor_turbidity:6,command_type:'OVERRIDE_VALVE'});
    const el=document.getElementById('cyberRes');
    el.style.cssText='background:rgba(255,68,68,.1);border:1px solid rgba(255,68,68,.3)';
    el.innerHTML=`<span style="color:var(--err)">🚨 ${d.message}</span><br><small>IP: 192.168.1.99 | ${bdg(d.cyber_status)}</small>`;
    loadCyber();
  }catch(e){console.error(e);}
}
async function doSafe(){
  try{
    const d=await aPost('/cybersecurity-scan',{source_ip:'192.168.1.50',sensor_pressure:65,sensor_turbidity:1.2,command_type:'READ_STATUS'});
    const el=document.getElementById('cyberRes');
    el.style.cssText='background:rgba(0,230,118,.1);border:1px solid rgba(0,230,118,.3)';
    el.innerHTML=`<span style="color:var(--ok)">✅ ${d.message}</span><br><small>IP: 192.168.1.50 | ${bdg(d.cyber_status)}</small>`;
  }catch(e){console.error(e);}
}

// ── CSV Export ────────────────────────────────────
async function doExport(){
  try{
    const r=await fetch(API+'/export-logs-csv',{headers:H});
    const b=await r.blob();
    const u=URL.createObjectURL(b);
    const a=document.createElement('a');
    a.href=u;a.download='aqua_dataset.csv';
    document.body.appendChild(a);a.click();
    document.body.removeChild(a);URL.revokeObjectURL(u);
    const el=document.getElementById('expSt');
    el.textContent=t('csvok');el.className='rs ok';el.classList.remove('hid');
  }catch(e){console.error(e);}
}

// ── PDF Report ────────────────────────────────────
async function doReport(){
  const btn = document.getElementById('rptBtn');
  btn.disabled = true; 
  btn.innerHTML = '<span class="spin"></span>';
  const st = document.getElementById('rptSt');
  try {
    const p = payload();
    const r = await fetch(`${API}/generate-report`, {method:'POST', headers:H, body:JSON.stringify(p)});
    if (r.ok) {
      const data = await r.json();
      if (data.success && data.pdf_base64) {
        // Download the file
        const link = document.createElement('a');
        link.href = 'data:application/pdf;base64,' + data.pdf_base64;
        link.download = data.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Show success message
        st.innerHTML = `<span style="color:#00e676;font-size:12px;">✅ تم حفظ نسخة في مجلد 'archived_reports'<br>وتحميل التقرير بنجاح!</span>`;
        st.className = 'rs ok';
        st.classList.remove('hid');
      }
    } else {
      throw new Error("Failed to generate report");
    }
  } catch(e) {
    st.textContent = "❌ حدث خطأ أثناء إنشاء التقرير";
    st.className = 'rs er';
    st.classList.remove('hid');
  } finally {
    btn.disabled = false;
    btn.innerHTML = `📄 <span data-i18n="genRpt">${t('genRpt') || 'إنشاء وأرشفة تقرير جديد'}</span>`;
  }
}

// ── Auto Refresh ──────────────────────────────────
function startRef(){if(refTmr)clearInterval(refTmr);refTmr=setInterval(()=>{if(autoRef)loadTab(curTab);},30000);}
function stopRef(){if(refTmr){clearInterval(refTmr);refTmr=null;}}
function toggleRef(){autoRef=document.getElementById('autoRefToggle')?.checked;}
function refreshAll(){loadTab(curTab);}

// ── Init ──────────────────────────────────────────
window.addEventListener('load',()=>{
  document.documentElement.setAttribute('data-theme',theme);
  document.documentElement.lang=lang;
  document.documentElement.dir='rtl';
  initSliders();
  translate();
  setInterval(tickClock,1000);
  tickClock();
  const pwI=document.getElementById('pw');
  if(pwI) pwI.addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});
  const unI=document.getElementById('un');
  if(unI) unI.addEventListener('keydown',e=>{if(e.key==='Enter')document.getElementById('pw')?.focus();});
});
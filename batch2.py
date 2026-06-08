#!/usr/bin/env python3
"""Batch 2 — Overview Enhancement patches"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def apply(name, old, new):
    assert old in content, f"ANCHOR NOT FOUND: {name}\n{repr(old[:100])}"
    return content.replace(old, new, 1)

# ── B2-1: Add prev-month + FIRE calculations after savingRate ─────────────────
content = apply('B2-1',
  "  const savingRate  = cf.income > 0 ? (cf.saving / cf.income * 100).toFixed(0) : 0;",
  """  const savingRate  = cf.income > 0 ? (cf.saving / cf.income * 100).toFixed(0) : 0;

  // Prev month MoM comparison
  const blnIdx   = BULAN_LIST.indexOf(bln);
  const prevBln  = BULAN_LIST[(blnIdx+11)%12];
  const prevThn  = blnIdx===0 ? String(parseInt(thn)-1) : thn;
  const cfPrev   = calcCashflowMonth(prevBln, prevThn);
  const incDelta = cfPrev.income>0 ? (cf.income-cfPrev.income)/cfPrev.income*100 : null;
  const spDelta  = cfPrev.spend>0  ? (cf.spend-cfPrev.spend)/cfPrev.spend*100   : null;
  const svDelta  = cfPrev.saving>0 ? (cf.saving-cfPrev.saving)/cfPrev.saving*100: null;

  // FIRE calculation (4% rule — 25× annual spending)
  const annualSpend = avgSpend * 12;
  const fireTarget  = parseFloat(STATE.config.fire_target||'0') || (annualSpend>0 ? annualSpend*25 : 0);
  const firePct     = fireTarget>0 ? Math.min(100, nw.netWorth/fireTarget*100) : 0;
  const annualSave  = cf.saving>0 ? cf.saving*12 : (parseFloat(savingRate)/100*(cf.income||avgSpend)*12);
  const yearsToFire = fireTarget>nw.netWorth && annualSave>0
    ? Math.ceil((fireTarget-nw.netWorth)/annualSave) : (nw.netWorth>=fireTarget&&fireTarget>0?0:null);

  // NW sparkline data (last 30 snapshots)
  const sparkData = snaps.slice(-30).map(s=>s.netWorth||0);""")

# ── B2-2: Enhance hero card — replace progress bar with dual progress ──────────
content = apply('B2-2',
  """    <div class="progress-to-target" style="margin-top:14px">
      <div class="progress-lbl"><span>Progress ke Rp1 Miliar</span><span>${pctTarget}%</span></div>
      <div class="progress-bar"><div class="progress-fill" style="width:${pctTarget}%"></div></div>
    </div>
  </div>""",
  """    <div style="margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:12px" class="hero-prog-grid">
      <div>
        <div class="progress-lbl"><span>🎯 Target Rp1M</span><span style="color:var(--gold)">${pctTarget}%</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:${pctTarget}%"></div></div>
      </div>
      <div>
        <div class="progress-lbl"><span>🔥 FIRE Progress</span><span style="color:var(--teal)">${firePct.toFixed(1)}%</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:${firePct}%;background:linear-gradient(90deg,var(--teal),#2dd4bf88)"></div></div>
      </div>
    </div>
    ${sparkData.length>1?`<div style="margin-top:14px;opacity:.7">${buildSparkline(sparkData)}</div>`:''}
  </div>""")

# ── B2-3: Add Savings Rate stat card to stat grid ─────────────────────────────
content = apply('B2-3',
  """    <div class="stat">
      <div class="stat-lbl">Wealth Growth</div>
      <div class="stat-val ${gls(nwChangePct)}">${nwChangePct!=null?fPct(nwChangePct):'—'}</div>
      <div class="stat-hint">vs hari sebelumnya</div>
    </div>
  </div>""",
  """    <div class="stat">
      <div class="stat-lbl">Wealth Growth</div>
      <div class="stat-val ${gls(nwChangePct)}">${nwChangePct!=null?fPct(nwChangePct):'—'}</div>
      <div class="stat-hint">vs hari sebelumnya</div>
    </div>
    <div class="stat ${savingRate>=30?'teal':''}">
      <div class="stat-lbl">Savings Rate</div>
      <div class="stat-val ${savingRate>=30?'teal':savingRate>=20?'':'rose'}">${savingRate}%</div>
      <div class="stat-hint">${savingRate>=30?'Excellent 🔥':savingRate>=20?'Good 👍':'Perlu ditingkatkan'}</div>
    </div>
    ${fireTarget>0?`
    <div class="stat teal">
      <div class="stat-lbl">FIRE Progress</div>
      <div class="stat-val teal">${firePct.toFixed(1)}%</div>
      <div class="stat-hint">${yearsToFire===0?'🎉 FIRE achieved!':yearsToFire!=null?'~'+yearsToFire+' tahun lagi':'Set target di Settings'}</div>
    </div>`:''}
  </div>""")

# ── B2-4: Add Monthly Scorecard card before commitHtml ────────────────────────
content = apply('B2-4',
  "  ${commitHtml}",
  """  <div class="card" style="margin-bottom:14px">
    <div class="card-title">📊 Monthly Scorecard — ${bln} ${thn}</div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">
      ${[
        {label:'Income',cur:cf.income,prev:cfPrev.income,color:'var(--green)',delta:incDelta},
        {label:'Spending',cur:cf.spend,prev:cfPrev.spend,color:'var(--rose)',delta:spDelta,invert:true},
        {label:'Savings',cur:cf.saving,prev:cfPrev.saving,color:'var(--teal)',delta:svDelta},
      ].map(m=>{
        const dir = m.delta==null?null:(m.invert?-m.delta:m.delta);
        const chipCls = dir==null?'neu':dir>=0?'up':'dn';
        const arrow = dir==null?'—':dir>=0?'↑':'↓';
        const deltaStr = m.delta!=null?(m.delta>=0?'+':'')+m.delta.toFixed(1)+'%':'—';
        return `<div style="background:var(--bg2);border-radius:var(--r);padding:12px;text-align:center">
          <div style="font-size:10px;color:var(--t3);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px">${m.label}</div>
          <div style="font-family:var(--mono);font-size:14px;font-weight:600;color:${m.color}">${fRp(m.cur)}</div>
          <div style="margin-top:6px"><span class="chip ${chipCls}" style="font-size:10px">${arrow} ${deltaStr} MoM</span></div>
          <div style="font-size:10px;color:var(--t3);margin-top:4px">${prevBln}: ${fRp(m.prev)}</div>
        </div>`;
      }).join('')}
    </div>
    ${cf.income>0?`<div style="margin-top:12px;padding-top:10px;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-size:12px">
      <span style="color:var(--t3)">Free Cash (sisa setelah semua)</span>
      <span style="font-family:var(--mono);font-weight:600;color:${cf.sisa>=0?'var(--green)':'var(--rose)'}">${fRp(cf.sisa)}</span>
    </div>`:''}
  </div>

  ${commitHtml}""")

# ── B2-5: Add FIRE info card before the two-column grid ───────────────────────
content = apply('B2-5',
  "  <div class=\"ov-grid\">",
  """  ${fireTarget>0?`
  <div class="card" style="margin-bottom:14px">
    <div class="card-title">🔥 FIRE Progress
      <button class="btn btn-ghost btn-xs" onclick="gotoPage('settings')" style="font-size:10px;color:var(--t3)">Atur target →</button>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:14px">
      <div style="background:var(--bg2);border-radius:var(--r);padding:12px">
        <div style="font-size:10px;color:var(--t3);text-transform:uppercase;margin-bottom:4px">FIRE Number</div>
        <div style="font-family:var(--mono);font-size:14px;font-weight:600;color:var(--teal)">${fRp(fireTarget)}</div>
        <div style="font-size:10px;color:var(--t3);margin-top:3px">25× pengeluaran tahunan</div>
      </div>
      <div style="background:var(--bg2);border-radius:var(--r);padding:12px">
        <div style="font-size:10px;color:var(--t3);text-transform:uppercase;margin-bottom:4px">Net Worth Saat Ini</div>
        <div style="font-family:var(--mono);font-size:14px;font-weight:600;color:var(--gold)">${fRp(nw.netWorth)}</div>
        <div style="font-size:10px;color:var(--t3);margin-top:3px">Gap: ${fRp(Math.max(0,fireTarget-nw.netWorth))}</div>
      </div>
      <div style="background:var(--bg2);border-radius:var(--r);padding:12px">
        <div style="font-size:10px;color:var(--t3);text-transform:uppercase;margin-bottom:4px">Estimasi</div>
        <div style="font-family:var(--mono);font-size:14px;font-weight:600;color:${yearsToFire===0?'var(--green)':'var(--t1)'}">${yearsToFire===0?'ACHIEVED 🎉':yearsToFire!=null?yearsToFire+' tahun':'—'}</div>
        <div style="font-size:10px;color:var(--t3);margin-top:3px">Annual saving: ${fRp(annualSave)}</div>
      </div>
    </div>
    <div class="progress-lbl" style="font-size:11px"><span>Progress</span><span style="color:var(--teal)">${firePct.toFixed(2)}%</span></div>
    <div class="progress-bar" style="height:8px"><div class="progress-fill" style="width:${firePct}%;background:linear-gradient(90deg,var(--teal),var(--gold))"></div></div>
  </div>`:''}

  <div class="ov-grid">""")

# ── B2-6: Add buildSparkline helper function before pageOverview ───────────────
content = apply('B2-6',
  "function pageOverview(){",
  """function buildSparkline(data){
  if(!data||data.length<2) return '';
  const w=280,h=40,pad=2;
  const min=Math.min(...data), max=Math.max(...data);
  const range=max-min||1;
  const pts=data.map((v,i)=>{
    const x=pad+(w-2*pad)*i/(data.length-1);
    const y=h-pad-(h-2*pad)*(v-min)/range;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
  const trend=data[data.length-1]>=data[0];
  return `<svg viewBox="0 0 ${w} ${h}" style="width:100%;height:40px;display:block"><polyline points="${pts}" fill="none" stroke="${trend?'var(--green)':'var(--rose)'}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/></svg>`;
}

function pageOverview(){""")

# ── B2-7: Add @media for hero progress grid responsive ────────────────────────
content = apply('B2-7',
  "@media(max-width:480px){",
  """@media(max-width:480px){
  .hero-prog-grid{grid-template-columns:1fr!important}
""")

print("All Batch 2 patches applied!")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Written {len(content)} chars")

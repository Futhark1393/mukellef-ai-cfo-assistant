// AI Traceability: Skills Agent wrote the dashboard SPA logic.
const API = '';
const fmt = v => '₺' + Number(v).toLocaleString('tr-TR',{minimumFractionDigits:2});

// Navigation
function navigate(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const el = document.getElementById('sec-'+section);
    if(el) el.classList.add('active');
    const nav = document.querySelector(`[data-nav="${section}"]`);
    if(nav) nav.classList.add('active');
    document.getElementById('page-title').textContent = nav ? nav.textContent.trim() : 'Dashboard';
    if(section === 'dashboard') loadDashboard();
    else if(section === 'cari') loadCari();
    else if(section === 'invoices') loadInvoices();
    else if(section === 'suppliers') loadSuppliers();
    else if(section === 'stock') loadStock();
    else if(section === 'bank') loadBank();
    else if(section === 'cashflow') loadCashflow();
    else if(section === 'checks') loadChecks();
    else if(section === 'tax') loadTax();
    else if(section === 'employees') loadEmployees();
    else if(section === 'vehicles') loadVehicles();
    else if(section === 'profitability') loadProfitability();
}

async function api(url) {
    try { const r = await fetch(API+url); return await r.json(); } catch(e) { return {success:false, error:e.message}; }
}
async function apiPost(url, body) {
    try {
        const r = await fetch(API+url, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
        return await r.json();
    } catch(e) { return {success:false, error:e.message}; }
}

function toast(msg, type='success') {
    const colors = {success:'linear-gradient(135deg,#10b981,#059669)', error:'linear-gradient(135deg,#f43f5e,#e11d48)', warning:'linear-gradient(135deg,#f59e0b,#d97706)'};
    const t = document.createElement('div');
    t.className = 'toast';
    t.style.background = colors[type]||colors.success;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(()=>{t.style.opacity='0';t.style.transition='opacity 0.4s';setTimeout(()=>t.remove(),400);},3000);
}

function tableHTML(headers, rows) {
    let h = '<table class="data-table"><thead><tr>' + headers.map(h=>`<th>${h}</th>`).join('') + '</tr></thead><tbody>';
    h += rows.map(r => '<tr>' + r.map(c=>`<td>${c}</td>`).join('') + '</tr>').join('');
    return h + '</tbody></table>';
}

function badge(text, type) { return `<span class="badge badge-${type}">${text}</span>`; }
function statCard(icon, value, label) {
    return `<div class="stat-card"><div class="stat-icon">${icon}</div><div class="stat-value">${value}</div><div class="stat-label">${label}</div></div>`;
}

// --- Dashboard ---
async function loadDashboard() {
    const el = document.getElementById('dash-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const [cari, suppliers, stock, bank, checks, employees] = await Promise.all([
        api('/api/cari/accounts'), api('/api/suppliers'), api('/api/stock'),
        api('/api/bank/summary'), api('/api/checks/summary'), api('/api/employees/summary')
    ]);
    const totalCari = cari.data ? cari.data.reduce((s,a)=>s+a.balance,0) : 0;
    const totalSupplier = suppliers.data ? suppliers.data.reduce((s,a)=>s+a.balance,0) : 0;
    const bankBal = bank.data ? bank.data.total_bank_balance : 0;
    const chkRec = checks.data ? checks.data.grand_total_receivable : 0;
    const chkPay = checks.data ? checks.data.grand_total_payable : 0;
    const empActive = employees.data ? employees.data.today_active : 0;

    el.innerHTML = `
        <div class="stats-grid">
            ${statCard('🏦', fmt(bankBal), 'Toplam Banka Bakiyesi')}
            ${statCard('👥', fmt(totalCari), 'Toplam Cari Alacak')}
            ${statCard('📦', fmt(totalSupplier), 'Toplam Tedarikçi Borç')}
            ${statCard('📝', fmt(chkRec), 'Alınacak Çek/Senet')}
            ${statCard('💸', fmt(chkPay), 'Ödenecek Çek/Senet')}
            ${statCard('👨‍💼', empActive + ' kişi', 'Bugün Aktif Personel')}
        </div>
        <div class="grid-2">
            <div class="glass-card">
                <div class="section-title">Günlük Nakit Akışı</div>
                ${bank.data ? bank.data.daily_breakdown.map(d =>
                    `<div class="flex-between mb-4"><span class="text-muted text-sm">${d.date}</span>
                    <span><span class="text-green">+${fmt(d.income)}</span> / <span class="text-red">-${fmt(d.expense)}</span></span></div>`
                ).join('') : ''}
            </div>
            <div class="glass-card">
                <div class="section-title">Stok Durumu</div>
                ${stock.data ? stock.data.map(s =>
                    `<div class="flex-between mb-4"><span>${s.name}</span>
                    <span>${s.low_stock ? badge(s.current_quantity+' '+s.unit,'red') : badge(s.current_quantity+' '+s.unit,'green')}</span></div>`
                ).join('') : ''}
            </div>
        </div>`;
}

// --- Cari ---
async function loadCari() {
    const el = document.getElementById('cari-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const res = await api('/api/cari/accounts');
    if(!res.data) { el.innerHTML = '<p class="text-red">Veri yüklenemedi</p>'; return; }
    el.innerHTML = tableHTML(['Hesap','Müşteri','Bakiye','Durum'],
        res.data.map(a => [a.account_id, a.customer_name, `<strong>${fmt(a.balance)}</strong>`, badge(a.status,'green')]));
}

// --- Invoices ---
async function loadInvoices() {
    const el = document.getElementById('inv-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const res = await api('/api/invoices');
    if(!res.data) { el.innerHTML = '<p class="text-red">Veri yüklenemedi</p>'; return; }
    el.innerHTML = `
        <div class="mb-6">
            <div class="glass-card">
                <div class="section-title">Fatura Yükle (OCR)</div>
                <input type="file" id="ocr-file" accept="image/*,.pdf" class="form-input mb-4">
                <button class="btn btn-brand" onclick="uploadOCR()">Fatura Tara</button>
                <div id="ocr-result" class="mt-4"></div>
            </div>
        </div>` +
        tableHTML(['Fatura No','Tedarikçi','Tarih','Tutar','Kategori','Durum'],
        res.data.map(i => [i.invoice_id, i.vendor_name, i.date, `<strong>${fmt(i.total_amount)}</strong>`, i.category,
            i.status==='processed' ? badge('İşlendi','green') : badge('Bekliyor','amber')]));
}

async function uploadOCR() {
    const file = document.getElementById('ocr-file');
    if(!file.files.length) { toast('Dosya seçin','warning'); return; }
    const fd = new FormData(); fd.append('file', file.files[0]);
    const res = await fetch(API+'/api/ocr/upload',{method:'POST',body:fd}).then(r=>r.json()).catch(()=>null);
    const el = document.getElementById('ocr-result');
    if(res && res.success) {
        el.innerHTML = `<div class="glass-card mt-4">
            <div class="flex-between mb-4"><span class="text-muted">Tedarikçi</span><strong>${res.vendor}</strong></div>
            <div class="flex-between mb-4"><span class="text-muted">Tarih</span><strong>${res.date}</strong></div>
            <div class="flex-between mb-4"><span class="text-muted">Tutar</span><strong class="text-green">${fmt(res.amount)}</strong></div>
            <div class="flex-between mb-4"><span class="text-muted">KDV</span><strong class="text-amber">${fmt(res.tax)}</strong></div>
            <div class="flex-between"><span class="text-muted">Kalem Sayısı</span><strong>${res.line_item_count}</strong></div>
        </div>`;
        toast('Fatura başarıyla tarandı!');
    } else { el.innerHTML = '<p class="text-red">Tarama başarısız</p>'; }
}

// --- Suppliers ---
async function loadSuppliers() {
    const el = document.getElementById('sup-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const res = await api('/api/suppliers');
    if(!res.data) return;
    el.innerHTML = tableHTML(['Tedarikçi ID','Firma Adı','Bakiye','Durum'],
        res.data.map(s => [s.supplier_id, s.supplier_name, `<strong class="text-red">${fmt(s.balance)}</strong>`, badge(s.status,'green')]));
}

// --- Stock ---
async function loadStock() {
    const el = document.getElementById('stock-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const res = await api('/api/stock');
    if(!res.data) return;
    el.innerHTML = tableHTML(['Stok ID','Ürün','Kategori','Miktar','Giren','Çıkan','Konum','Durum'],
        res.data.map(s => [s.stock_id, s.name, s.category, `<strong>${s.current_quantity} ${s.unit}</strong>`,
            `<span class="text-green">+${s.total_in}</span>`, `<span class="text-red">-${s.total_out}</span>`,
            s.location, s.low_stock ? badge('Düşük','red') : badge('Normal','green')]));
}

// --- Bank ---
async function loadBank() {
    const el = document.getElementById('bank-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const [accounts, summary] = await Promise.all([api('/api/bank/accounts'), api('/api/bank/summary')]);
    let html = '<div class="stats-grid mb-6">';
    if(summary.data) {
        html += statCard('💰', fmt(summary.data.total_bank_balance), 'Toplam Bakiye');
        html += statCard('📈', fmt(summary.data.total_income), 'Toplam Gelir');
        html += statCard('📉', fmt(summary.data.total_expense), 'Toplam Gider');
        html += statCard(summary.data.net_cashflow>=0?'✅':'⚠️', fmt(summary.data.net_cashflow), 'Net Nakit Akış');
    }
    html += '</div>';
    if(accounts.data) {
        html += '<div class="section-title">Banka Hesapları</div>';
        html += tableHTML(['Hesap','Banka','Tür','IBAN','Bakiye'],
            accounts.data.map(a => [a.account_id, a.bank_name, a.account_type, a.iban, `<strong>${fmt(a.balance)}</strong>`]));
    }
    el.innerHTML = html;
}

// --- Cashflow ---
async function loadCashflow() { /* form is static, no auto-load needed */ }

async function runCashflow() {
    const b = parseFloat(document.getElementById('cf-bal').value);
    const r = parseFloat(document.getElementById('cf-rev').value);
    const e = parseFloat(document.getElementById('cf-exp').value);
    if([b,r,e].some(isNaN)) { toast('Tüm alanları doldurun','warning'); return; }
    const [pred, scenarios] = await Promise.all([
        apiPost('/api/cashflow/predict', {current_balance:b,monthly_revenue:r,monthly_expense:e,months:6}),
        apiPost('/api/cashflow/scenarios', {current_balance:b,monthly_revenue:r,monthly_expense:e,months:6})
    ]);
    let html = '';
    if(pred.projections) {
        html += '<div class="glass-card mb-6"><div class="section-title">6 Aylık Projeksiyon</div>';
        html += tableHTML(['Ay','Gelir','Gider','Net','Bakiye'],
            pred.projections.map(p => [p.month, fmt(p.revenue), fmt(p.expense),
                `<span class="${p.net_cashflow>=0?'text-green':'text-red'}">${fmt(p.net_cashflow)}</span>`,
                `<strong class="${p.projected_balance>=0?'text-green':'text-red'}">${fmt(p.projected_balance)}</strong>`]));
        html += '</div>';
    }
    if(scenarios.data) {
        const s = scenarios.data.summary;
        html += '<div class="stats-grid">';
        html += statCard('🟢', fmt(s.best_case_final_balance), 'En İyi Senaryo');
        html += statCard('🟡', fmt(s.base_case_final_balance), 'Baz Senaryo');
        html += statCard('🔴', fmt(s.worst_case_final_balance), 'En Kötü Senaryo');
        html += '</div>';
    }
    document.getElementById('cf-result').innerHTML = html;
}

async function runExpense() {
    const t = parseFloat(document.getElementById('ea-total').value);
    const p = parseInt(document.getElementById('ea-periods').value);
    if(isNaN(t)||isNaN(p)||p<1) { toast('Alanları doldurun','warning'); return; }
    const res = await apiPost('/api/expense/allocate', {amount:t, months:p});
    const el = document.getElementById('ea-result');
    if(res.allocation) {
        let html = '<div class="glass-card mt-4"><div class="section-title">Dağılım Tablosu</div>';
        html += tableHTML(['Dönem','Tutar'], Object.entries(res.allocation).map(([k,v]) => [k, `<strong>${fmt(v)}</strong>`]));
        html += '</div>';
        el.innerHTML = html;
    }
}

// --- Checks ---
async function loadChecks() {
    const el = document.getElementById('checks-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const [checks, notes, summary] = await Promise.all([api('/api/checks'), api('/api/notes'), api('/api/checks/summary')]);
    let html = '';
    if(summary.data) {
        html += '<div class="stats-grid mb-6">';
        html += statCard('📥', fmt(summary.data.grand_total_receivable), 'Toplam Alacak');
        html += statCard('📤', fmt(summary.data.grand_total_payable), 'Toplam Borç');
        html += statCard('🔄', summary.data.checks.clearing_count+' adet', 'Takastaki Çekler');
        html += statCard('💵', fmt(summary.data.checks.clearing_amount), 'Takas Tutarı');
        html += '</div>';
    }
    if(checks.data) {
        html += '<div class="section-title">Çekler</div>';
        const statusMap = {portfolio:'Portföyde',clearing:'Takasta',paid:'Ödendi',pending:'Beklemede',bounced:'Karşılıksız'};
        const statusColor = {portfolio:'blue',clearing:'amber',paid:'green',pending:'cyan',bounced:'red'};
        html += tableHTML(['Çek No','Tür','Kişi/Firma','Tutar','Vade','Banka','Durum'],
            checks.data.map(c => [c.check_id, c.type==='received'?'Alınan':'Verilen',
                c.drawer||c.payee, `<strong>${fmt(c.amount)}</strong>`, c.due_date, c.bank,
                badge(statusMap[c.status]||c.status, statusColor[c.status]||'blue')]));
    }
    if(notes.data && notes.data.length) {
        html += '<div class="section-title mt-4">Senetler</div>';
        html += tableHTML(['Senet No','Tür','Kişi/Firma','Tutar','Vade','Durum'],
            notes.data.map(n => [n.note_id, n.type==='received'?'Alınan':'Verilen',
                n.drawer||n.payee, `<strong>${fmt(n.amount)}</strong>`, n.due_date,
                badge(n.status==='portfolio'?'Portföyde':'Beklemede', n.status==='portfolio'?'blue':'amber')]));
    }
    el.innerHTML = html;
}

// --- Tax ---
async function loadTax() {
    const el = document.getElementById('tax-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const [tax, payroll] = await Promise.all([api('/api/tax/summary'), api('/api/payroll')]);
    let html = '';
    if(tax.data) {
        const k = tax.data.kdv, m = tax.data.muhtasar;
        html += '<div class="stats-grid mb-6">';
        html += statCard('🧾', fmt(k.odenecek_kdv), 'Ödenecek KDV');
        html += statCard('📋', fmt(m.total_muhtasar), 'Muhtasar Toplam');
        html += statCard('💰', fmt(tax.data.payroll_summary.total_cost), 'Toplam Personel Maliyeti');
        html += '</div>';
        html += '<div class="grid-2 mb-6"><div class="glass-card"><div class="section-title">KDV Hesaplama</div>';
        html += `<div class="flex-between mb-4"><span class="text-muted">Hesaplanan KDV</span><strong>${fmt(k.hesaplanan_kdv)}</strong></div>`;
        html += `<div class="flex-between mb-4"><span class="text-muted">İndirilecek KDV</span><strong>${fmt(k.indirilecek_kdv)}</strong></div>`;
        html += `<div class="flex-between mb-4"><span class="text-muted">Ödenecek KDV</span><strong class="text-red">${fmt(k.odenecek_kdv)}</strong></div>`;
        html += `<div class="flex-between"><span class="text-muted">Devreden KDV</span><strong>${fmt(k.devreden_kdv)}</strong></div></div>`;
        html += `<div class="glass-card"><div class="section-title">Muhtasar</div>`;
        html += `<div class="flex-between mb-4"><span class="text-muted">Toplam Brüt Maaş</span><strong>${fmt(m.total_gross_salary)}</strong></div>`;
        html += `<div class="flex-between mb-4"><span class="text-muted">Gelir Vergisi Stopajı</span><strong class="text-red">${fmt(m.gelir_vergisi_stopaji)}</strong></div>`;
        html += `<div class="flex-between"><span class="text-muted">Damga Vergisi</span><strong>${fmt(m.damga_vergisi)}</strong></div></div></div>`;
    }
    if(payroll.data) {
        html += '<div class="section-title">Bordro</div>';
        html += tableHTML(['Personel','Pozisyon','Brüt','SGK','Gelir V.','Net Maaş','İşveren Maliyeti'],
            payroll.data.payslips.map(p => [p.name, p.role, fmt(p.gross_salary), fmt(p.sgk_worker),
                fmt(p.gelir_vergisi), `<strong class="text-green">${fmt(p.net_salary)}</strong>`,
                `<strong>${fmt(p.total_cost)}</strong>`]));
    }
    el.innerHTML = html;
}

// --- Employees ---
async function loadEmployees() {
    const el = document.getElementById('emp-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const [list, summary] = await Promise.all([api('/api/employees'), api('/api/employees/summary')]);
    let html = '';
    if(summary.data) {
        html += '<div class="stats-grid mb-6">';
        html += statCard('👥', summary.data.total_employees, 'Toplam Personel');
        html += statCard('✅', summary.data.today_active+' kişi', 'Bugün Aktif');
        html += statCard('⏱️', summary.data.avg_daily_hours+' saat', 'Ort. Günlük Mesai');
        html += statCard('📊', summary.data.total_hours_this_week+' saat', 'Haftalık Toplam');
        html += '</div>';
    }
    if(list.data) {
        html += tableHTML(['Personel','Pozisyon','Gün Sayısı','Toplam Saat','Ort. Saat','Bugün'],
            list.data.map(e => [e.name, e.role, e.days_present+' gün', e.total_hours+' saat',
                e.avg_hours+' saat',
                e.today_status==='active'?badge('Aktif','green'):e.today_status==='leave'?badge('İzinli','amber'):badge(e.today_status,'blue')]));
    }
    el.innerHTML = html;
}

// --- Vehicles ---
async function loadVehicles() {
    const el = document.getElementById('vhc-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const res = await api('/api/vehicles');
    if(!res.data) return;
    el.innerHTML = tableHTML(['Plaka','Marka','Yıl','Tür','Sigorta Bitiş','Kalan Gün','Toplam Gider','Durum'],
        res.data.map(v => [v.plate, v.brand, v.year, v.type, v.insurance_end,
            v.insurance_days_left+' gün', `<strong>${fmt(v.total_expenses)}</strong>`,
            v.insurance_expiring_soon ? badge('Yakında Bitiyor','red') : badge('Aktif','green')]));
}

// --- Profitability ---
async function loadProfitability() {
    const el = document.getElementById('prof-content');
    el.innerHTML = '<p class="text-muted">Yükleniyor...</p>';
    const res = await api('/api/profitability');
    if(!res.data) return;
    const s = res.data.summary;
    let html = '<div class="stats-grid mb-6">';
    html += statCard('💰', fmt(s.total_revenue), 'Toplam Gelir');
    html += statCard('📊', '%'+s.gross_margin_pct, 'Brüt Kar Marjı');
    html += statCard('💵', fmt(s.net_profit), 'Net Kar');
    html += statCard('📈', '%'+s.rantabilite_pct, 'Rantabilite (ROE)');
    html += '</div>';
    html += '<div class="grid-2 mb-6">';
    html += '<div class="glass-card"><div class="section-title">Üretim Ürünleri</div>';
    if(res.data.production.length) {
        html += tableHTML(['Ürün','Gelir','Maliyet','Brüt Kar','Marj'],
            res.data.production.map(p => [p.name, fmt(p.revenue), fmt(p.cogs),
                `<strong class="text-green">${fmt(p.gross_profit)}</strong>`, '%'+p.margin_pct]));
    }
    html += '</div><div class="glass-card"><div class="section-title">Ticaret Ürünleri</div>';
    if(res.data.trade.length) {
        html += tableHTML(['Ürün','Gelir','Maliyet','Brüt Kar','Marj'],
            res.data.trade.map(p => [p.name, fmt(p.revenue), fmt(p.cogs),
                `<strong class="text-green">${fmt(p.gross_profit)}</strong>`, '%'+p.margin_pct]));
    }
    html += '</div></div>';
    el.innerHTML = html;
}

// Init
document.addEventListener('DOMContentLoaded', () => navigate('dashboard'));

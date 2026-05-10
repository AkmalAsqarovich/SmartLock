from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3, os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'smartlock.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ism TEXT NOT NULL,
                familiya TEXT NOT NULL,
                qurilma TEXT NOT NULL DEFAULT 'Noma lum',
                vaqt TEXT NOT NULL,
                sana TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qurilma_nomi TEXT UNIQUE NOT NULL,
                joylashuv TEXT DEFAULT '',
                qoshilgan TEXT NOT NULL,
                faol INTEGER DEFAULT 1
            )
        ''')
        conn.commit()

init_db()

HTML = r"""<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Lock — Boshqaruv Paneli</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #09090f;
      --surface: #111118;
      --surface2: #17171f;
      --border: #1e1e2a;
      --border2: #2a2a38;
      --accent: #6ee7b7;
      --accent2: #34d399;
      --accent-dim: rgba(110,231,183,0.12);
      --accent-dim2: rgba(110,231,183,0.06);
      --red: #f87171;
      --red-dim: rgba(248,113,113,0.12);
      --yellow: #fbbf24;
      --blue: #60a5fa;
      --blue-dim: rgba(96,165,250,0.12);
      --text: #e8e8f0;
      --text2: #8888aa;
      --text3: #55556a;
      --font-head: 'Syne', sans-serif;
      --font-body: 'DM Sans', sans-serif;
      --font-mono: 'DM Mono', monospace;
      --radius: 14px;
      --radius-sm: 8px;
    }

    *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

    body {
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }

    body::before {
      content: '';
      position: fixed; inset: 0;
      background-image:
        linear-gradient(rgba(110,231,183,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(110,231,183,0.025) 1px, transparent 1px);
      background-size: 48px 48px;
      pointer-events: none;
      z-index: 0;
    }

    .sidebar {
      position: fixed; left:0; top:0; bottom:0;
      width: 240px;
      background: var(--surface);
      border-right: 1px solid var(--border);
      display: flex; flex-direction: column;
      z-index: 100;
    }

    .logo {
      padding: 28px 24px 20px;
      border-bottom: 1px solid var(--border);
    }
    .logo-icon {
      width: 40px; height: 40px;
      background: linear-gradient(135deg, var(--accent), #10b981);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px; margin-bottom: 12px;
      box-shadow: 0 0 24px rgba(110,231,183,0.3);
    }
    .logo h1 {
      font-family: var(--font-head);
      font-size: 18px; font-weight: 800;
      letter-spacing: -0.5px;
      color: var(--text);
    }
    .logo span {
      font-size: 11px; color: var(--text3);
      font-family: var(--font-mono);
      letter-spacing: 1px;
      text-transform: uppercase;
    }

    .nav { padding: 16px 12px; flex: 1; }
    .nav-label {
      font-size: 10px; color: var(--text3);
      text-transform: uppercase; letter-spacing: 1.5px;
      padding: 0 12px 8px;
      font-family: var(--font-mono);
    }
    .nav-item {
      display: flex; align-items: center; gap: 10px;
      padding: 10px 12px; border-radius: var(--radius-sm);
      cursor: pointer; color: var(--text2);
      font-size: 14px; font-weight: 500;
      transition: all 0.15s; margin-bottom: 2px;
      border: 1px solid transparent;
    }
    .nav-item:hover { background: var(--surface2); color: var(--text); }
    .nav-item.active {
      background: var(--accent-dim);
      color: var(--accent);
      border-color: rgba(110,231,183,0.15);
    }
    .nav-item .icon { font-size: 16px; width: 20px; text-align:center; }
    .nav-badge {
      margin-left: auto;
      background: var(--accent-dim);
      color: var(--accent);
      font-size: 11px; padding: 2px 7px;
      border-radius: 20px;
      font-family: var(--font-mono);
    }

    .sidebar-footer {
      padding: 16px;
      border-top: 1px solid var(--border);
    }
    .status-pill {
      display: flex; align-items: center; gap: 8px;
      background: var(--accent-dim2);
      border: 1px solid rgba(110,231,183,0.1);
      border-radius: 100px;
      padding: 8px 12px;
      font-size: 12px; color: var(--accent2);
    }
    .pulse-dot {
      width: 8px; height: 8px;
      background: var(--accent);
      border-radius: 50%;
      animation: pulse 1.8s infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.8)} }

    .main {
      margin-left: 240px;
      min-height: 100vh;
      position: relative; z-index: 1;
    }

    .topbar {
      padding: 20px 32px;
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between;
      background: rgba(9,9,15,0.8);
      backdrop-filter: blur(12px);
      position: sticky; top: 0; z-index: 50;
    }
    .topbar h2 {
      font-family: var(--font-head);
      font-size: 22px; font-weight: 700;
      letter-spacing: -0.5px;
    }
    .topbar .breadcrumb {
      font-size: 12px; color: var(--text3);
      font-family: var(--font-mono);
      margin-top: 2px;
    }
    .topbar-actions { display: flex; gap: 10px; align-items:center; }

    .btn {
      padding: 8px 16px; border-radius: var(--radius-sm);
      border: 1px solid var(--border2);
      background: var(--surface2);
      color: var(--text2); font-size: 13px;
      cursor: pointer; font-family: var(--font-body);
      font-weight: 500;
      transition: all 0.15s;
      display: flex; align-items: center; gap: 6px;
    }
    .btn:hover { border-color: var(--border2); color: var(--text); background: #1e1e28; }
    .btn-primary {
      background: var(--accent-dim);
      border-color: rgba(110,231,183,0.25);
      color: var(--accent);
    }
    .btn-primary:hover { background: rgba(110,231,183,0.18); }

    .content { padding: 28px 32px; }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px; margin-bottom: 28px;
    }
    .stat-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px 22px;
      position: relative; overflow: hidden;
      transition: border-color 0.2s;
    }
    .stat-card:hover { border-color: var(--border2); }
    .stat-card::before {
      content: '';
      position: absolute; top:0; left:0; right:0;
      height: 2px;
      background: linear-gradient(90deg, var(--accent), transparent);
      opacity: 0.6;
    }
    .stat-card.red::before { background: linear-gradient(90deg, var(--red), transparent); }
    .stat-card.blue::before { background: linear-gradient(90deg, var(--blue), transparent); }
    .stat-card.yellow::before { background: linear-gradient(90deg, var(--yellow), transparent); }
    .stat-label { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; font-family: var(--font-mono); }
    .stat-value {
      font-family: var(--font-head);
      font-size: 36px; font-weight: 800;
      color: var(--text); margin: 8px 0 4px;
      letter-spacing: -1px;
    }
    .stat-sub { font-size: 12px; color: var(--text3); }
    .stat-icon {
      position: absolute; right: 18px; top: 18px;
      font-size: 28px; opacity: 0.12;
    }

    .section { display: none; }
    .section.active { display: block; }

    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden; margin-bottom: 20px;
    }
    .panel-head {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between;
    }
    .panel-head h3 {
      font-family: var(--font-head);
      font-size: 15px; font-weight: 600;
    }

    table { width: 100%; border-collapse: collapse; }
    thead th {
      text-align: left;
      font-size: 11px; color: var(--text3);
      padding: 12px 20px;
      border-bottom: 1px solid var(--border);
      font-family: var(--font-mono);
      text-transform: uppercase; letter-spacing: 0.5px;
      font-weight: 500;
    }
    tbody td { padding: 14px 20px; border-bottom: 1px solid rgba(30,30,42,0.8); font-size: 14px; }
    tbody tr:last-child td { border-bottom: none; }
    tbody tr { transition: background 0.1s; }
    tbody tr:hover { background: var(--surface2); }

    .avatar {
      width: 34px; height: 34px; border-radius: 50%;
      background: linear-gradient(135deg, #1e3a5f, #1e4a3f);
      border: 1px solid var(--border2);
      display: flex; align-items: center; justify-content: center;
      font-family: var(--font-head);
      font-size: 12px; font-weight: 700; color: var(--accent);
      flex-shrink: 0;
    }
    .name-cell { display: flex; align-items: center; gap: 10px; }
    .chip {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 3px 10px; border-radius: 20px;
      font-size: 12px; font-family: var(--font-mono);
    }
    .chip.green { background: var(--accent-dim); color: var(--accent); border: 1px solid rgba(110,231,183,0.15); }
    .chip.red { background: var(--red-dim); color: var(--red); border: 1px solid rgba(248,113,113,0.15); }
    .chip.blue { background: var(--blue-dim); color: var(--blue); border: 1px solid rgba(96,165,250,0.15); }
    .chip.gray { background: var(--surface2); color: var(--text2); border: 1px solid var(--border2); }

    .empty-state { text-align:center; padding: 64px; color: var(--text3); font-size: 14px; }
    .empty-state .empty-icon { font-size: 40px; margin-bottom: 12px; opacity: 0.4; }

    .cal-nav {
      display: flex; align-items: center; gap: 8px;
      padding: 20px 24px 0;
    }
    .cal-nav h3 {
      font-family: var(--font-head);
      font-size: 20px; font-weight: 700;
      flex: 1;
    }
    .year-tabs {
      display: flex; gap: 8px;
      padding: 16px 24px;
      flex-wrap: wrap;
    }
    .year-tab {
      padding: 6px 14px; border-radius: 20px;
      border: 1px solid var(--border2);
      background: transparent; color: var(--text2);
      font-family: var(--font-mono); font-size: 13px;
      cursor: pointer; transition: all 0.15s;
    }
    .year-tab.active, .year-tab:hover {
      background: var(--accent-dim); color: var(--accent);
      border-color: rgba(110,231,183,0.2);
    }

    .months-grid {
      display: grid; grid-template-columns: repeat(4, 1fr);
      gap: 12px; padding: 16px 24px;
    }
    .month-card {
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 16px;
      cursor: pointer;
      transition: all 0.15s;
      text-align: center;
    }
    .month-card:hover, .month-card.active {
      border-color: rgba(110,231,183,0.25);
      background: var(--accent-dim);
    }
    .month-card .mname { font-family: var(--font-head); font-weight: 600; font-size: 15px; color: var(--text); }
    .month-card .mcount { font-size: 11px; color: var(--text3); margin-top: 4px; font-family: var(--font-mono); }

    .days-grid {
      display: grid; grid-template-columns: repeat(7, 1fr);
      gap: 8px; padding: 16px 24px;
    }
    .day-card {
      aspect-ratio: 1;
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      cursor: pointer; transition: all 0.15s;
      position: relative;
    }
    .day-card:hover, .day-card.has-data:hover {
      border-color: rgba(110,231,183,0.3);
      background: var(--accent-dim);
    }
    .day-card .dnum { font-family: var(--font-head); font-size: 16px; font-weight: 700; }
    .day-card .dcnt { font-size: 10px; color: var(--text3); font-family: var(--font-mono); }
    .day-card.has-data .dnum { color: var(--accent); }
    .day-card.has-data .dcnt { color: var(--accent2); }
    .day-card.today { border-color: rgba(110,231,183,0.4); }
    .day-card.today::after {
      content: '';
      position: absolute; bottom: 4px;
      width: 4px; height: 4px;
      background: var(--accent); border-radius: 50%;
    }

    .cal-breadcrumb {
      display: flex; align-items: center; gap: 6px;
      padding: 16px 24px 0;
      font-size: 12px; color: var(--text3);
      font-family: var(--font-mono);
    }
    .cal-breadcrumb span { cursor: pointer; }
    .cal-breadcrumb span:hover { color: var(--accent); }
    .cal-breadcrumb .sep { color: var(--text3); }

    .devices-grid {
      display: grid; grid-template-columns: repeat(3, 1fr);
      gap: 16px;
    }
    .device-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 22px;
      transition: all 0.2s;
      cursor: pointer;
      position: relative; overflow: hidden;
    }
    .device-card:hover { border-color: var(--border2); transform: translateY(-1px); }
    .device-card.active-device { border-color: rgba(110,231,183,0.2); }
    .device-card.active-device::before {
      content: '';
      position: absolute; top:0; left:0; right:0;
      height: 3px;
      background: linear-gradient(90deg, var(--accent), #34d399);
    }
    .device-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px; }
    .device-icon {
      width: 48px; height: 48px; border-radius: 12px;
      background: var(--accent-dim);
      display: flex; align-items: center; justify-content: center;
      font-size: 22px;
      border: 1px solid rgba(110,231,183,0.15);
    }
    .device-name { font-family: var(--font-head); font-size: 16px; font-weight: 700; margin-bottom: 3px; }
    .device-loc { font-size: 12px; color: var(--text3); }
    .device-stats { display: flex; gap: 20px; }
    .device-stat { }
    .device-stat .val { font-family: var(--font-head); font-size: 24px; font-weight: 800; color: var(--text); }
    .device-stat .lbl { font-size: 11px; color: var(--text3); font-family: var(--font-mono); }

    .modal-overlay {
      position: fixed; inset: 0;
      background: rgba(0,0,0,0.7);
      backdrop-filter: blur(4px);
      z-index: 1000;
      display: none; align-items: center; justify-content: center;
    }
    .modal-overlay.open { display: flex; }
    .modal {
      background: var(--surface);
      border: 1px solid var(--border2);
      border-radius: 20px;
      padding: 32px; width: 400px;
      box-shadow: 0 24px 64px rgba(0,0,0,0.6);
    }
    .modal h3 { font-family: var(--font-head); font-size: 20px; font-weight: 700; margin-bottom: 8px; }
    .modal p { font-size: 13px; color: var(--text2); margin-bottom: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 12px; color: var(--text3); margin-bottom: 6px; font-family: var(--font-mono); text-transform: uppercase; letter-spacing: 0.5px; }
    .form-group input, .form-group select {
      width: 100%; padding: 10px 14px;
      background: var(--bg);
      border: 1px solid var(--border2);
      border-radius: var(--radius-sm);
      color: var(--text); font-size: 14px;
      font-family: var(--font-body);
      outline: none; transition: border-color 0.15s;
    }
    .form-group input:focus, .form-group select:focus { border-color: rgba(110,231,183,0.4); }
    .modal-actions { display: flex; gap: 10px; margin-top: 24px; }

    @keyframes fadeIn {
      from { opacity:0; transform: translateY(8px); }
      to { opacity:1; transform: translateY(0); }
    }
    .fade-in { animation: fadeIn 0.25s ease forwards; }

    .time-chip {
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--text2);
      background: var(--surface2);
      border: 1px solid var(--border2);
      padding: 3px 9px; border-radius: 6px;
    }

    #liveTime {
      font-family: var(--font-mono);
      font-size: 13px; color: var(--text3);
    }
  </style>
</head>
<body>

<aside class="sidebar">
  <div class="logo">
    <div class="logo-icon">🔐</div>
    <h1>Smart Lock</h1>
    <span>v2.0 · Kirish tizimi</span>
  </div>
  <nav class="nav">
    <div class="nav-label">Navigatsiya</div>
    <div class="nav-item active" onclick="showSection('dashboard')">
      <span class="icon">📊</span> Dashboard
    </div>
    <div class="nav-item" onclick="showSection('calendar')">
      <span class="icon">📅</span> Kalendar
    </div>
    <div class="nav-item" onclick="showSection('devices')">
      <span class="icon">🚪</span> Qurilmalar
    </div>
    <div class="nav-item" onclick="showSection('all-records')">
      <span class="icon">📋</span> Barcha Kirish
      <span class="nav-badge" id="sidebarTotal">0</span>
    </div>
  </nav>
  <div class="sidebar-footer">
    <div class="status-pill">
      <div class="pulse-dot"></div>
      Server aktiv
    </div>
  </div>
</aside>

<main class="main">
  <div class="topbar">
    <div>
      <h2 id="pageTitle">Dashboard</h2>
      <div class="breadcrumb" id="pageBreadcrumb">Smart Lock / Asosiy panel</div>
    </div>
    <div class="topbar-actions">
      <span id="liveTime">--:--:--</span>
      <button class="btn btn-primary" onclick="loadAll()">↻ Yangilash</button>
    </div>
  </div>

  <div class="content">

    <section class="section active" id="sec-dashboard">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-label">Jami kirish</div>
          <div class="stat-value" id="st-total">0</div>
          <div class="stat-sub">Barcha vaqt</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-icon">📅</div>
          <div class="stat-label">Bugun</div>
          <div class="stat-value" id="st-today">0</div>
          <div class="stat-sub" id="st-today-date">—</div>
        </div>
        <div class="stat-card yellow">
          <div class="stat-icon">🚪</div>
          <div class="stat-label">Qurilmalar</div>
          <div class="stat-value" id="st-devices">0</div>
          <div class="stat-sub">Ulangan</div>
        </div>
        <div class="stat-card red">
          <div class="stat-icon">🕐</div>
          <div class="stat-label">So'nggi kirish</div>
          <div class="stat-value" style="font-size:20px;letter-spacing:0" id="st-last">—</div>
          <div class="stat-sub" id="st-last-who">Hech kim</div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <h3>Oxirgi kirish ro'yxati</h3>
          <span class="chip green" id="live-badge">● Jonli</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Shaxs</th>
              <th>Qurilma</th>
              <th>Vaqt</th>
              <th>Sana</th>
            </tr>
          </thead>
          <tbody id="dashTable">
            <tr><td colspan="5" class="empty-state"><div class="empty-icon">🔒</div>Yuklanmoqda...</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="section" id="sec-calendar">
      <div class="panel" id="calPanel">
        <div class="cal-breadcrumb" id="calBreadcrumb"></div>
        <div id="calView"></div>
      </div>
    </section>

    <section class="section" id="sec-devices">
      <div style="display:flex;justify-content:flex-end;margin-bottom:16px">
        <button class="btn btn-primary" onclick="openAddDevice()">+ Qurilma qo'shish</button>
      </div>
      <div class="devices-grid" id="devicesGrid">
        <div class="empty-state" style="grid-column:1/-1">Yuklanmoqda...</div>
      </div>
    </section>

    <section class="section" id="sec-all-records">
      <div class="panel">
        <div class="panel-head">
          <h3>Barcha kirish yozuvlari</h3>
          <div style="display:flex;gap:8px;align-items:center">
            <input type="text" id="searchInput" placeholder="Ism yoki qurilma bo'yicha qidirish..."
              style="background:var(--bg);border:1px solid var(--border2);border-radius:8px;padding:6px 12px;color:var(--text);font-size:13px;width:240px;outline:none"
              oninput="filterRecords()">
          </div>
        </div>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Shaxs</th>
              <th>Qurilma</th>
              <th>Vaqt</th>
              <th>Sana</th>
            </tr>
          </thead>
          <tbody id="allTable">
            <tr><td colspan="5" class="empty-state">Yuklanmoqda...</td></tr>
          </tbody>
        </table>
      </div>
    </section>

  </div>
</main>

<div class="modal-overlay" id="addDeviceModal">
  <div class="modal">
    <h3>Yangi qurilma qo'shish</h3>
    <p>ESP32 qurilmasi nomi va joylashuvini kiriting</p>
    <div class="form-group">
      <label>Qurilma nomi *</label>
      <input type="text" id="newDevName" placeholder="Masalan: Eshik 1">
    </div>
    <div class="form-group">
      <label>Joylashuv</label>
      <input type="text" id="newDevLoc" placeholder="Masalan: 1-qavat, Asosiy kirish">
    </div>
    <div class="modal-actions">
      <button class="btn" style="flex:1" onclick="closeModal()">Bekor qilish</button>
      <button class="btn btn-primary" style="flex:1" onclick="saveDevice()">Saqlash</button>
    </div>
  </div>
</div>

<script>
const MONTHS_UZ = ['Yanvar','Fevral','Mart','Aprel','May','Iyun','Iyul','Avgust','Sentabr','Oktabr','Noyabr','Dekabr'];
let allRecords = [], allDevices = [];
let calState = { view: 'year', year: null, month: null, day: null, device: null };

function getInitials(ism, familiya) {
  const a = (ism||'')[0]||'';
  const b = (familiya||'')[0]||'';
  return (a+b).toUpperCase() || '??';
}

function todayStr() {
  const n = new Date();
  return String(n.getDate()).padStart(2,'0') + '.' +
         String(n.getMonth()+1).padStart(2,'0') + '.' +
         n.getFullYear();
}

function formatRow(r, idx, total) {
  return `<tr class="fade-in">
    <td style="color:var(--text3);font-family:var(--font-mono);font-size:12px">${total - idx}</td>
    <td>
      <div class="name-cell">
        <div class="avatar">${getInitials(r.ism, r.familiya)}</div>
        <div>
          <div style="font-weight:500">${r.ism||''} ${r.familiya||''}</div>
        </div>
      </div>
    </td>
    <td><span class="chip blue">${r.qurilma||'—'}</span></td>
    <td><span class="time-chip">${r.vaqt||''}</span></td>
    <td style="color:var(--text3);font-size:13px;font-family:var(--font-mono)">${r.sana||''}</td>
  </tr>`;
}

async function loadAll() {
  try {
    const [rRes, dRes] = await Promise.all([
      fetch('/api/records'), fetch('/api/devices')
    ]);
    allRecords = await rRes.json();
    allDevices = await dRes.json();
    renderDashboard();
    renderDevices();
    filterRecords();
    if (document.getElementById('sec-calendar').classList.contains('active')) {
      renderCalendar();
    }
  } catch(e) { console.error(e); }
}

function renderDashboard() {
  const today = todayStr();
  const todayRecs = allRecords.filter(r => r.sana === today);
  const last = allRecords[allRecords.length - 1];

  document.getElementById('st-total').textContent = allRecords.length;
  document.getElementById('st-today').textContent = todayRecs.length;
  document.getElementById('st-today-date').textContent = today;
  document.getElementById('st-devices').textContent = allDevices.length;
  document.getElementById('sidebarTotal').textContent = allRecords.length;

  if (last) {
    document.getElementById('st-last').textContent = last.vaqt;
    document.getElementById('st-last-who').textContent = `${last.ism} ${last.familiya}`;
  }

  const tbody = document.getElementById('dashTable');
  const shown = allRecords.slice().reverse().slice(0, 20);
  if (shown.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-state"><div class="empty-icon">🚪</div>Hali ma'lumot yo'q. ESP32 kutilmoqda...</td></tr>`;
    return;
  }
  tbody.innerHTML = shown.map((r, i) => formatRow(r, i, allRecords.length)).join('');
}

function renderDevices() {
  const grid = document.getElementById('devicesGrid');
  if (allDevices.length === 0) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
      <div class="empty-icon">🚪</div>Qurilmalar yo'q. Yangi qurilma qo'shing.
    </div>`;
    return;
  }
  grid.innerHTML = allDevices.map(d => {
    const devRecs = allRecords.filter(r => r.qurilma === d.qurilma_nomi);
    const todayRecs = devRecs.filter(r => r.sana === todayStr());
    return `<div class="device-card ${devRecs.length > 0 ? 'active-device' : ''}" onclick="openDeviceCalendar('${d.qurilma_nomi}')">
      <div class="device-head">
        <div class="device-icon">🚪</div>
        <span class="chip ${d.faol ? 'green' : 'red'}">${d.faol ? '● Aktiv' : '○ Nofaol'}</span>
      </div>
      <div class="device-name">${d.qurilma_nomi}</div>
      <div class="device-loc">${d.joylashuv || 'Joylashuv ko\'rsatilmagan'}</div>
      <div class="device-stats" style="margin-top:16px">
        <div class="device-stat">
          <div class="val">${devRecs.length}</div>
          <div class="lbl">Jami</div>
        </div>
        <div class="device-stat">
          <div class="val">${todayRecs.length}</div>
          <div class="lbl">Bugun</div>
        </div>
      </div>
    </div>`;
  }).join('');
}

function openDeviceCalendar(deviceName) {
  calState.device = deviceName;
  calState.view = 'year';
  calState.year = new Date().getFullYear().toString();
  showSection('calendar');
}

let filteredRecs = [];
function filterRecords() {
  const q = (document.getElementById('searchInput')?.value || '').toLowerCase();
  filteredRecs = q
    ? allRecords.filter(r =>
        (`${r.ism} ${r.familiya}`).toLowerCase().includes(q) ||
        (r.qurilma||'').toLowerCase().includes(q))
    : allRecords;

  const tbody = document.getElementById('allTable');
  if (filteredRecs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-state"><div class="empty-icon">🔍</div>Natija topilmadi</td></tr>`;
    return;
  }
  const reversed = filteredRecs.slice().reverse();
  tbody.innerHTML = reversed.map((r, i) => formatRow(r, i, filteredRecs.length)).join('');
}

/* ===== CALENDAR (WITH DEVICE FILTER) ===== */
function renderCalendar() {
  const bc = document.getElementById('calBreadcrumb');
  const view = document.getElementById('calView');
  
  // Apply filter if device is selected
  const sourceRecords = calState.device 
    ? allRecords.filter(r => r.qurilma === calState.device)
    : allRecords;

  let deviceLabel = calState.device ? `<span class="chip blue" style="margin-right:10px">${calState.device}</span>` : '';

  if (calState.view === 'year' || !calState.year) {
    const years = [...new Set(sourceRecords.map(r => r.sana?.split('.')[2]).filter(Boolean))].sort();
    const currentYear = new Date().getFullYear().toString();
    if (!years.includes(currentYear)) years.push(currentYear);

    bc.innerHTML = `${deviceLabel} <span style="color:var(--text2)">Yil tanlang</span>`;
    view.innerHTML = `<div class="year-tabs">
      ${years.map(y => `<div class="year-tab ${y === calState.year ? 'active' : ''}" onclick="calSelectYear('${y}')">${y}</div>`).join('')}
    </div>`;
  }
  else if (calState.view === 'month') {
    bc.innerHTML = `${deviceLabel} 
      <span onclick="calGoBack('year')" style="color:var(--text);cursor:pointer">${calState.year}</span>
      <span class="sep"> / </span>
      <span style="color:var(--text2)">Oy tanlang</span>`;

    const montCounts = {};
    sourceRecords.filter(r => r.sana?.endsWith(calState.year)).forEach(r => {
      const m = r.sana.split('.')[1];
      montCounts[m] = (montCounts[m]||0)+1;
    });

    view.innerHTML = `<div class="months-grid">
      ${MONTHS_UZ.map((mn, i) => {
        const mKey = String(i+1).padStart(2,'0');
        const cnt = montCounts[mKey]||0;
        return `<div class="month-card ${mKey === calState.month ? 'active' : ''}" onclick="calSelectMonth('${mKey}')">
          <div class="mname">${mn}</div>
          <div class="mcount">${cnt} ta kirish</div>
        </div>`;
      }).join('')}
    </div>`;
  }
  else if (calState.view === 'day') {
    const mIdx = parseInt(calState.month)-1;
    bc.innerHTML = `${deviceLabel}
      <span onclick="calGoBack('year')" style="color:var(--text);cursor:pointer">${calState.year}</span>
      <span class="sep"> / </span>
      <span onclick="calGoBack('month')" style="color:var(--text);cursor:pointer">${MONTHS_UZ[mIdx]}</span>
      <span class="sep"> / </span>
      <span style="color:var(--text2)">Kun tanlang</span>`;

    const daysInMonth = new Date(calState.year, mIdx+1, 0).getDate();
    const dayCounts = {};
    sourceRecords
      .filter(r => r.sana?.split('.')[1] === calState.month && r.sana?.split('.')[2] === calState.year)
      .forEach(r => {
        const d = r.sana.split('.')[0];
        dayCounts[d] = (dayCounts[d]||0)+1;
      });

    const todayParts = todayStr().split('.');
    const isThisMonthYear = todayParts[1]===calState.month && todayParts[2]===calState.year;

    view.innerHTML = `<div class="days-grid">
      ${Array.from({length: daysInMonth}, (_,i) => {
        const d = String(i+1).padStart(2,'0');
        const cnt = dayCounts[d]||0;
        const isToday = isThisMonthYear && todayParts[0]===d;
        return `<div class="day-card ${cnt>0?'has-data':''} ${isToday?'today':''}" onclick="calSelectDay('${d}')">
          <div class="dnum">${i+1}</div>
          <div class="dcnt">${cnt>0 ? cnt+'✓' : ''}</div>
        </div>`;
      }).join('')}
    </div>`;
  }
  else if (calState.view === 'records') {
    const mIdx = parseInt(calState.month)-1;
    bc.innerHTML = `${deviceLabel}
      <span onclick="calGoBack('year')" style="color:var(--text);cursor:pointer">${calState.year}</span>
      <span class="sep"> / </span>
      <span onclick="calGoBack('month')" style="color:var(--text);cursor:pointer">${MONTHS_UZ[mIdx]}</span>
      <span class="sep"> / </span>
      <span onclick="calGoBack('day')" style="color:var(--text);cursor:pointer">${calState.day}</span>
      <span class="sep"> / </span>
      <span style="color:var(--text2)">Kirish ro'yxati</span>`;

    const dayRecs = sourceRecords.filter(r => r.sana === `${calState.day}.${calState.month}.${calState.year}`);

    view.innerHTML = `<table>
      <thead><tr>
        <th>#</th><th>Shaxs</th><th>Qurilma</th><th>Vaqt</th><th>Sana</th>
      </tr></thead>
      <tbody>
        ${dayRecs.length === 0
          ? `<tr><td colspan="5" class="empty-state"><div class="empty-icon">🔍</div>Bu kunda kirish yo'q</td></tr>`
          : dayRecs.slice().reverse().map((r,i) => formatRow(r,i,dayRecs.length)).join('')}
      </tbody>
    </table>`;
  }
}

function calSelectYear(y) { calState.year = y; calState.view = 'month'; renderCalendar(); }
function calSelectMonth(m) { calState.month = m; calState.view = 'day'; renderCalendar(); }
function calSelectDay(d) { calState.day = d; calState.view = 'records'; renderCalendar(); }
function calGoBack(to) {
  calState.view = to;
  if (to === 'year') { calState.month = null; calState.day = null; }
  if (to === 'month') { calState.day = null; }
  renderCalendar();
}

const SECTION_TITLES = {
  'dashboard': ['Dashboard', 'Smart Lock / Asosiy panel'],
  'calendar': ['Kalendar', 'Smart Lock / Sana bo\'yicha ko\'rish'],
  'devices': ['Qurilmalar', 'Smart Lock / ESP32 qurilmalar'],
  'all-records': ['Barcha Kirish', 'Smart Lock / Kirish yozuvlari'],
};

function showSection(name) {
  if (name !== 'calendar' && name !== 'devices') {
    calState.device = null; // Clear filter when leaving calendar or devices
  }

  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('sec-' + name).classList.add('active');
  
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(n => { if (n.getAttribute('onclick')?.includes(name)) n.classList.add('active'); });

  const [title, bc] = SECTION_TITLES[name] || [name, ''];
  document.getElementById('pageTitle').textContent = title;
  document.getElementById('pageBreadcrumb').textContent = bc;

  if (name === 'calendar') {
    if (!calState.year) calState.year = new Date().getFullYear().toString();
    if (!calState.view) calState.view = 'year';
    renderCalendar();
  }
}

function openAddDevice() {
  document.getElementById('addDeviceModal').classList.add('open');
}
function closeModal() {
  document.getElementById('addDeviceModal').classList.remove('open');
  document.getElementById('newDevName').value = '';
  document.getElementById('newDevLoc').value = '';
}
async function saveDevice() {
  const nom = document.getElementById('newDevName').value.trim();
  const joy = document.getElementById('newDevLoc').value.trim();
  if (!nom) return alert("Qurilma nomi majburiy!");
  try {
    await fetch('/api/devices', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ qurilma_nomi: nom, joylashuv: joy })
    });
    closeModal();
    await loadAll();
  } catch(e) { console.error(e); }
}

function updateClock() {
  document.getElementById('liveTime').textContent = new Date().toLocaleTimeString('uz-UZ');
}
setInterval(updateClock, 1000);
updateClock();

loadAll();
setInterval(loadAll, 5000);
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    return HTML

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({'xato': "JSON yuborilmadi"}), 400

    ism = data.get('ism', '').strip()
    familiya = data.get('familiya', '').strip()
    qurilma = data.get('qurilma', '').strip()

    if not ism or not familiya:
        return jsonify({'xato': "ism va familiya majburiy"}), 400
    if not qurilma:
        return jsonify({'xato': "qurilma nomi majburiy"}), 400

    now = datetime.now()
    vaqt = data.get('vaqt', now.strftime('%H:%M:%S'))
    sana = now.strftime('%d.%m.%Y')

    with get_db() as conn:
        conn.execute('''
            INSERT OR IGNORE INTO devices (qurilma_nomi, joylashuv, qoshilgan)
            VALUES (?, ?, ?)
        ''', (qurilma, '', now.isoformat()))
        conn.execute('''
            INSERT INTO records (ism, familiya, qurilma, vaqt, sana, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ism, familiya, qurilma, vaqt, sana, now.isoformat()))
        conn.commit()

    print(f"[+] {ism} {familiya} | {qurilma} | {vaqt} | {sana}")
    return jsonify({'status': 'ok', 'xabar': "Ma'lumot saqlandi"}), 200


@app.route('/api/records', methods=['GET'])
def get_records():
    with get_db() as conn:
        rows = conn.execute('SELECT * FROM records ORDER BY id ASC').fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/devices', methods=['GET'])
def get_devices():
    with get_db() as conn:
        rows = conn.execute('SELECT * FROM devices ORDER BY id ASC').fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/devices', methods=['POST'])
def add_device():
    data = request.get_json()
    if not data or not data.get('qurilma_nomi', '').strip():
        return jsonify({'xato': "qurilma_nomi majburiy"}), 400
    nom = data['qurilma_nomi'].strip()
    joy = data.get('joylashuv', '').strip()
    now = datetime.now().isoformat()
    try:
        with get_db() as conn:
            conn.execute('INSERT INTO devices (qurilma_nomi, joylashuv, qoshilgan) VALUES (?,?,?)',
                         (nom, joy, now))
            conn.commit()
        return jsonify({'status': 'ok'}), 200
    except sqlite3.IntegrityError:
        return jsonify({'xato': "Bu nom allaqachon mavjud"}), 409


if __name__ == '__main__':
    print("=" * 50)
    print("  🔐 Smart Lock Server ishga tushdi!")
    print(f"  📦 Baza: {DB_PATH}")
    print("  🌐 http://0.0.0.0:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)

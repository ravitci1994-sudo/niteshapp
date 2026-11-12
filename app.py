import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Fleet Operations Command Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

html_code = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Fleet Operations Dashboard</title>

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- SheetJS (xlsx parser) -->
  <script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>

  <!-- React 18 & ReactDOM -->
  <script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>

  <!-- Babel Standalone for JSX -->
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <!-- Lucide Icons -->
  <script src="https://unpkg.com/lucide@latest"></script>

  <!-- Framer Motion -->
  <script src="https://unpkg.com/framer-motion@10.16.4/dist/framer-motion.js"></script>

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700;800&display=swap" rel="stylesheet">

  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          }
        }
      }
    };
  </script>

  <style>
    :root {
      --bg-main: #0F1110;
      --bg-panel: #161917;
      --bg-header: #1B1E1C;
      --bg-hover: #1E2220;
      --border-color: #252A27;
      --border-sub: #202422;
      --accent: #D2DDB2;
      --accent-text: #1A2015;
      --text-main: #F1F5F2;
      --text-muted: #8F9A94;
      --num-total: #F1F5F2;
      --num-closed: #D2DDB2;
      --num-transit: #F4C5A9;
      --num-delay: #E5C3C3;
    }

    body {
      background: var(--bg-main);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
      transition: background 0.35s ease, color 0.35s ease;
    }

    ::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    ::-webkit-scrollbar-track {
      background: var(--bg-panel);
    }
    ::-webkit-scrollbar-thumb {
      background: var(--border-color);
      border-radius: 9999px;
    }

    .glass-panel {
      background: var(--bg-panel);
      border: 1px solid var(--border-color);
      transition: background 0.35s ease, border-color 0.35s ease;
    }

    .sidebar-active {
      background: var(--accent);
      color: var(--accent-text);
      box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
    }

    .accent-btn {
      background: var(--accent);
      color: var(--accent-text);
    }
    .accent-btn:hover {
      filter: brightness(0.92);
    }

    .grid-table {
      border: 1px solid var(--border-color);
      border-collapse: separate;
      border-spacing: 0;
      border-radius: 1rem;
      overflow: hidden;
    }
    .grid-table th {
      border-bottom: 2px solid var(--border-color);
      border-right: 1px solid var(--border-color);
      background: var(--bg-header);
      color: var(--text-main);
      font-weight: 900;
      font-size: 0.68rem;
      letter-spacing: 0.05em;
    }
    .grid-table th:last-child {
      border-right: none;
    }
    .grid-table td {
      border-bottom: 1px solid var(--border-sub);
      border-right: 1px solid var(--border-sub);
      color: var(--text-main);
    }
    .grid-table td:last-child {
      border-right: none;
    }
    .grid-table tr:last-child td {
      border-bottom: none;
    }
    .grid-table tbody tr:hover {
      background: var(--bg-hover);
    }
  </style>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel">
    const { useState, useMemo, useEffect } = React;
    const { motion, AnimatePresence } = window.Motion || {
      motion: {
        div: (props) => <div {...props}>{props.children}</div>,
        button: (props) => <button {...props}>{props.children}</button>,
      },
      AnimatePresence: ({ children }) => <>{children}</>
    };

    // 5 Built-in Color Themes
    const THEMES = {
      sage: {
        name: 'Sage Mint',
        dot: '#D2DDB2',
        vars: {
          '--bg-main': '#0F1110',
          '--bg-panel': '#161917',
          '--bg-header': '#1B1E1C',
          '--bg-hover': '#1E2220',
          '--border-color': '#252A27',
          '--border-sub': '#202422',
          '--accent': '#D2DDB2',
          '--accent-text': '#1A2015',
          '--text-main': '#F1F5F2',
          '--text-muted': '#8F9A94',
          '--num-total': '#FFFFFF',
          '--num-closed': '#D2DDB2',
          '--num-transit': '#F4C5A9',
          '--num-delay': '#E5C3C3',
        }
      },
      wine: {
        name: 'Wine Burgundy',
        dot: '#E12D61',
        vars: {
          '--bg-main': '#0D0105',
          '--bg-panel': '#19030A',
          '--bg-header': '#24040E',
          '--bg-hover': '#2A0510',
          '--border-color': '#42091B',
          '--border-sub': '#2E0613',
          '--accent': '#E12D61',
          '--accent-text': '#FFFFFF',
          '--text-main': '#FCE7EF',
          '--text-muted': '#C88EA1',
          '--num-total': '#FFFFFF',
          '--num-closed': '#34D399',
          '--num-transit': '#60A5FA',
          '--num-delay': '#FB7185',
        }
      },
      cyber: {
        name: 'Cyber Ocean',
        dot: '#38BDF8',
        vars: {
          '--bg-main': '#070B14',
          '--bg-panel': '#0F172A',
          '--bg-header': '#1E293B',
          '--bg-hover': '#17253B',
          '--border-color': '#26354D',
          '--border-sub': '#1E293B',
          '--accent': '#38BDF8',
          '--accent-text': '#082F49',
          '--text-main': '#F1F5F9',
          '--text-muted': '#94A3B8',
          '--num-total': '#FFFFFF',
          '--num-closed': '#4ADE80',
          '--num-transit': '#38BDF8',
          '--num-delay': '#F87171',
        }
      },
      emerald: {
        name: 'Emerald Matrix',
        dot: '#10B981',
        vars: {
          '--bg-main': '#040D0A',
          '--bg-panel': '#081C15',
          '--bg-header': '#0D281E',
          '--bg-hover': '#113327',
          '--border-color': '#1B4332',
          '--border-sub': '#123024',
          '--accent': '#10B981',
          '--accent-text': '#022C22',
          '--text-main': '#ECFDF5',
          '--text-muted': '#6EE7B7',
          '--num-total': '#FFFFFF',
          '--num-closed': '#34D399',
          '--num-transit': '#FBBF24',
          '--num-delay': '#FB7185',
        }
      },
      gold: {
        name: 'Royal Amber',
        dot: '#F59E0B',
        vars: {
          '--bg-main': '#0E0B06',
          '--bg-panel': '#18130A',
          '--bg-header': '#241C0E',
          '--bg-hover': '#292011',
          '--border-color': '#3D2F17',
          '--border-sub': '#2B2110',
          '--accent': '#F59E0B',
          '--accent-text': '#1C1302',
          '--text-main': '#FEF3C7',
          '--text-muted': '#D97706',
          '--num-total': '#FFFFFF',
          '--num-closed': '#A3E635',
          '--num-transit': '#FBBF24',
          '--num-delay': '#F87171',
        }
      }
    };

    const ClientBrandBadge = ({ name }) => {
      const lower = (name || '').toLowerCase();
      if (lower.includes('dhl')) {
        return (
          <div className="w-5 h-5 rounded bg-[#FFCC00] flex items-center justify-center shrink-0">
            <span className="text-[#D40511] font-black text-[7px]">DHL</span>
          </div>
        );
      }
      if (lower.includes('trackon')) {
        return (
          <div className="w-5 h-5 rounded bg-[#990000] flex items-center justify-center shrink-0">
            <span className="text-white font-black text-[8px]">T</span>
          </div>
        );
      }
      if (lower.includes('amazon')) {
        return (
          <div className="w-5 h-5 rounded bg-[#131921] border border-amber-500/40 flex items-center justify-center shrink-0">
            <span className="text-[#FF9900] font-black text-[10px]">a</span>
          </div>
        );
      }
      if (lower.includes('flipkart')) {
        return (
          <div className="w-5 h-5 rounded bg-[#2874F0] flex items-center justify-center shrink-0">
            <span className="text-[#FFE500] italic font-black text-[10px]">f</span>
          </div>
        );
      }
      const initial = (name || 'C').charAt(0).toUpperCase();
      return (
        <div className="w-5 h-5 rounded flex items-center justify-center shrink-0" style={{ background: 'var(--bg-header)', border: '1px solid var(--border-color)' }}>
          <span className="font-black text-[9px]" style={{ color: 'var(--accent)' }}>{initial}</span>
        </div>
      );
    };

    const INITIAL_RECORDS = [
      { id: 'TRP-9021', date: '2026-11-10', vehicleNo: 'DL-01-AB-1234', client: 'Amazon India', staff: 'Ramesh Kumar', route: 'Delhi Hub → Mumbai Sort', status: 'Trip Closed', remarks: 'Delayed at NH48 toll barrier' },
      { id: 'TRP-9022', date: '2026-11-09', vehicleNo: 'MH-04-CD-5678', client: 'Flipkart Wholesale', staff: 'Suresh Patil', route: 'Pune DC → Bengaluru WH', status: 'Trip Closed', remarks: 'Severe heavy rain & traffic jam' },
      { id: 'TRP-9023', date: '2026-11-08', vehicleNo: 'HR-26-EE-9901', client: 'Reliance Retail', staff: 'Vikram Singh', route: 'Gurugram → Jaipur DC', status: 'Trip Closed', remarks: 'Vehicle tyre breakdown at Rewari' },
      { id: 'TRP-9024', date: '2026-11-08', vehicleNo: 'KA-05-FF-4321', client: 'Amazon India', staff: 'Anand Rao', route: 'Bengaluru Hub → Chennai Yard', status: 'In-Transit', remarks: 'Single driver mandatory rest pause' },
      { id: 'TRP-9025', date: '2026-10-25', vehicleNo: 'GJ-01-GG-7788', client: 'Tata Consumer', staff: 'Jignesh Patel', route: 'Ahmedabad → Surat Plant', status: 'Trip Closed', remarks: 'Delivered seamlessly on schedule' },
      { id: 'TRP-9026', date: '2026-10-22', vehicleNo: 'UP-14-HH-3344', client: 'Flipkart Wholesale', staff: 'Mohan Verma', route: 'Noida Plant → Kanpur DC', status: 'Trip Closed', remarks: 'Mechanical radiator coolant leak' },
      { id: 'TRP-9027', date: '2026-11-05', vehicleNo: 'TN-02-JJ-6655', client: 'Reliance Retail', staff: 'Karthik Raja', route: 'Chennai Hub → Madurai DC', status: 'Trip Closed', remarks: 'Driver sickness delay during haul' },
      { id: 'TRP-9028', date: '2026-09-18', vehicleNo: 'WB-02-KK-1122', client: 'Tata Consumer', staff: 'Subhash Roy', route: 'Kolkata Hub → Patna Hub', status: 'Trip Closed', remarks: 'On schedule line haul handover' },
      { id: 'TRP-9029', date: '2026-11-07', vehicleNo: 'DL-01-LM-9944', client: 'BlueDart Express', staff: 'Mohit Pandey', route: 'Delhi Hub → Lucknow Sorting', status: 'Trip Closed', remarks: 'Unloading dock traffic congestion' },
      { id: 'TRP-9030', date: '2026-11-10', vehicleNo: 'HR-55-XY-8811', client: 'Delhivery Crossdock', staff: 'Kuldeep Gill', route: 'Sonipat DC → Ludhiana TC', status: 'Trip Closed', remarks: 'On time standard transit' },
    ];

    function App() {
      const [records, setRecords] = useState(INITIAL_RECORDS);
      const [uploadedFileCount, setUploadedFileCount] = useState(0);
      const [activeTab, setActiveTab] = useState('overall');
      const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

      // Theme state
      const [themeKey, setThemeKey] = useState('sage');
      const [showThemeMenu, setShowThemeMenu] = useState(false);

      const [selectedDate, setSelectedDate] = useState('2026-11-10');
      const [showCalendar, setShowCalendar] = useState(false);
      const [selectedClientFilter, setSelectedClientFilter] = useState('');
      const [selectedStaffFilter, setSelectedStaffFilter] = useState('');
      const [calMonth, setCalMonth] = useState(10);
      const [calYear, setCalYear] = useState(2026);

      const [aiDelayCategory, setAiDelayCategory] = useState('ALL');
      const [aiGenerating, setAiGenerating] = useState(false);
      const [aiReportOutput, setAiReportOutput] = useState(null);

      // Apply selected theme variables to document root
      useEffect(() => {
        const themeObj = THEMES[themeKey] || THEMES.sage;
        Object.entries(themeObj.vars).forEach(([k, v]) => {
          document.documentElement.style.setProperty(k, v);
        });
      }, [themeKey]);

      useEffect(() => {
        if (window.lucide) {
          window.lucide.createIcons();
        }
      }, [activeTab, selectedDate, showCalendar, mobileMenuOpen, aiDelayCategory, aiReportOutput, records, themeKey, showThemeMenu]);

      const handleMultipleFileUpload = async (e) => {
        const files = Array.from(e.target.files || []);
        if (files.length === 0) return;

        let accumulated = [];

        for (let fIdx = 0; fIdx < files.length; fIdx++) {
          const file = files[fIdx];
          try {
            const buffer = await file.arrayBuffer();
            const workbook = XLSX.read(new Uint8Array(buffer), { type: 'array', cellDates: true });
            
            workbook.SheetNames.forEach((sheetName) => {
              const sheet = workbook.Sheets[sheetName];
              if (!sheet || !sheet['!ref']) return;

              const json = XLSX.utils.sheet_to_json(sheet, { defval: '', raw: false });
              if (!Array.isArray(json) || json.length === 0) return;

              json.forEach((row, idx) => {
                const keys = Object.keys(row).map(k => String(k).trim());
                if (keys.length === 0) return;

                const getValue = (candidateKeywords) => {
                  const matchedKey = keys.find(k => {
                    const norm = k.toLowerCase().replace(/[^a-z0-9]/g, '');
                    return candidateKeywords.some(c => norm.includes(c));
                  });
                  return matchedKey ? String(row[matchedKey]).trim() : '';
                };

                const rawVehicle = getValue(['vehicleno', 'vehicle', 'truck', 'regno', 'vehicle_num', 'lorry', 'truckno', 'rcno']);
                const rawClient = getValue(['client', 'customer', 'account', 'party', 'consignor', 'consignee', 'branch', 'hub']);
                const rawStaff = getValue(['staff', 'driver', 'pilot', 'drivername', 'operator', 'executive']);
                const rawRoute = getValue(['route', 'corridor', 'lane', 'source', 'dest', 'from', 'to', 'trip']);
                const rawStatus = getValue(['status', 'tripstatus', 'arrivalstatus', 'currentstatus']);
                const rawRemarks = getValue(['remark', 'reason', 'delay', 'comment', 'cause', 'issue']);
                const rawTripId = getValue(['tripid', 'trip', 'id', 'challan', 'docket', 'cnno', 'lrno']);
                const rawDate = getValue(['date', 'arrival', 'closing', 'closed', 'dispatch', 'start']);

                if (!rawVehicle && !rawClient && !rawRoute && !rawTripId) {
                  return;
                }

                let formattedDate = '2026-11-10';
                if (rawDate) {
                  const parsed = new Date(rawDate);
                  if (!isNaN(parsed.getTime())) {
                    formattedDate = parsed.toISOString().split('T')[0];
                  } else {
                    const matchedStr = String(rawDate).match(/\d{4}[-/.]\d{1,2}[-/.]\d{1,2}/) || String(rawDate).match(/\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}/);
                    if (matchedStr) {
                      formattedDate = matchedStr[0].replace(/\//g, '-').replace(/\./g, '-');
                    }
                  }
                }

                const statusVal = rawStatus || 'Trip Closed';
                const remarksVal = rawRemarks || (statusVal.toLowerCase().includes('delay') ? 'Delayed arrival recorded' : 'On-time movement');

                accumulated.push({
                  id: rawTripId || `TRP-${fIdx + 1}-${idx + 1}`,
                  date: formattedDate,
                  vehicleNo: (rawVehicle || `VEHICLE-${idx + 1}`).toUpperCase(),
                  client: rawClient || 'Default Account',
                  staff: rawStaff || 'Assigned Driver',
                  route: rawRoute || 'Origin → Destination Hub',
                  status: statusVal,
                  remarks: remarksVal
                });
              });
            });
          } catch (err) {
            console.error(`Error processing file ${file.name}:`, err);
          }
        }

        if (accumulated.length > 0) {
          setRecords(accumulated);
          setUploadedFileCount(files.length);
          setSelectedDate(accumulated[0].date);
        } else {
          alert('Excel me se data read nahi ho paya. Kripya check karein ki Excel sheet me columns sahi format me hon.');
        }

        e.target.value = '';
      };

      const metrics = useMemo(() => {
        const total = records.length;
        const inTransit = records.filter(r => r.status.toLowerCase().includes('transit') || r.status.toLowerCase().includes('run')).length;
        const delayed = records.filter(r => {
          const rem = (r.remarks || '').toLowerCase();
          const st = (r.status || '').toLowerCase();
          return st.includes('delay') || rem.includes('breakdown') || rem.includes('jam') || rem.includes('leak') || rem.includes('rest') || rem.includes('congestion') || rem.includes('sickness');
        }).length;
        const closed = Math.max(0, total - inTransit - delayed);

        return { total, inTransit, closed, delayed };
      }, [records]);

      const clientStats = useMemo(() => {
        const map = {};
        records.forEach(r => {
          const client = r.client || 'Unknown Client';
          if (!map[client]) {
            map[client] = { name: client, total: 0, closed: 0, delayed: 0 };
          }
          map[client].total += 1;
          const rem = (r.remarks || '').toLowerCase();
          const isDelayed = r.status.toLowerCase().includes('delay') || rem.includes('delay') || rem.includes('breakdown') || rem.includes('jam') || rem.includes('leak') || rem.includes('rest') || rem.includes('congestion');
          if (isDelayed) {
            map[client].delayed += 1;
          } else {
            const isInTransit = r.status.toLowerCase().includes('transit') || r.status.toLowerCase().includes('run');
            if (!isInTransit) { map[client].closed += 1; }
          }
        });

        return Object.values(map).map(c => {
          const onTimeRate = c.total > 0 ? Math.round(((c.total - c.delayed) / c.total) * 100) : 100;
          return { ...c, sla: Math.max(0, onTimeRate) };
        }).sort((a, b) => b.total - a.total);
      }, [records]);

      const staffStats = useMemo(() => {
        const map = {};
        records.forEach(r => {
          const staff = r.staff || 'Unknown Staff';
          if (!map[staff]) {
            map[staff] = { name: staff, total: 0, closed: 0, delayed: 0 };
          }
          map[staff].total += 1;
          const rem = (r.remarks || '').toLowerCase();
          const isDelayed = r.status.toLowerCase().includes('delay') || rem.includes('delay') || rem.includes('breakdown') || rem.includes('jam') || rem.includes('leak') || rem.includes('rest') || rem.includes('congestion');
          if (isDelayed) {
            map[staff].delayed += 1;
          } else {
            const isInTransit = r.status.toLowerCase().includes('transit') || r.status.toLowerCase().includes('run');
            if (!isInTransit) { map[staff].closed += 1; }
          }
        });

        return Object.values(map).map(s => {
          const onTimeRate = s.total > 0 ? Math.round(((s.total - s.delayed) / s.total) * 100) : 100;
          return { ...s, sla: Math.max(0, onTimeRate) };
        }).sort((a, b) => b.total - a.total);
      }, [records]);

      const routeStats = useMemo(() => {
        const map = {};
        records.forEach(r => {
          const route = r.route || 'Unknown Corridor';
          if (!map[route]) {
            map[route] = { name: route, total: 0, closed: 0, delayed: 0 };
          }
          map[route].total += 1;
          const rem = (r.remarks || '').toLowerCase();
          const isDelayed = r.status.toLowerCase().includes('delay') || rem.includes('delay') || rem.includes('breakdown') || rem.includes('jam') || rem.includes('leak') || rem.includes('rest') || rem.includes('congestion');
          if (isDelayed) {
            map[route].delayed += 1;
          } else {
            const isInTransit = r.status.toLowerCase().includes('transit') || r.status.toLowerCase().includes('run');
            if (!isInTransit) { map[route].closed += 1; }
          }
        });

        return Object.values(map).map(rt => {
          const onTimeRate = rt.total > 0 ? Math.round(((rt.total - rt.delayed) / rt.total) * 100) : 100;
          return { ...rt, sla: Math.max(0, onTimeRate) };
        }).sort((a, b) => b.total - a.total);
      }, [records]);

      const filteredArrivals = useMemo(() => {
        return records.filter(r => {
          const matchDate = !selectedDate || r.date === selectedDate;
          const matchClient = !selectedClientFilter || r.client === selectedClientFilter;
          const matchStaff = !selectedStaffFilter || r.staff === selectedStaffFilter;
          return matchDate && matchClient && matchStaff;
        });
      }, [records, selectedDate, selectedClientFilter, selectedStaffFilter]);

      const delayedRecords = useMemo(() => {
        return records.filter(r => {
          const rem = (r.remarks || '').toLowerCase();
          const st = (r.status || '').toLowerCase();
          return st.includes('delay') || rem.includes('breakdown') || rem.includes('jam') || rem.includes('leak') || rem.includes('rest') || rem.includes('congestion') || rem.includes('sickness');
        });
      }, [records]);

      const categorizedDelays = useMemo(() => {
        return delayedRecords.map(r => {
          const rem = (r.remarks || '').toLowerCase();
          let category = 'Other Delay';
          let actionRequired = 'Investigate corridor timeline with local supervisor';

          if (rem.includes('breakdown') || rem.includes('leak') || rem.includes('tyre') || rem.includes('mechanical') || rem.includes('coolant')) {
            category = 'Breakdown';
            actionRequired = 'Deploy emergency mobile mechanic & arrange towing relief';
          } else if (rem.includes('driver sickness') || rem.includes('driver issue') || rem.includes('driver absence')) {
            category = 'Driver Issue';
            actionRequired = 'Summon backup standby pilot & collect driver medical note';
          } else if (rem.includes('traffic') || rem.includes('toll') || rem.includes('nh48') || rem.includes('jam') || rem.includes('rain')) {
            category = 'Traffic Jam';
            actionRequired = 'Issue bypass highway diversion GPS coordinates via control tower';
          } else if (rem.includes('single driver') || rem.includes('rest') || rem.includes('fatigue')) {
            category = 'Single Driver';
            actionRequired = 'Enforce 45-min mandatory log & schedule twin-driver crew for >400km';
          } else if (rem.includes('dock') || rem.includes('unloading') || rem.includes('congestion') || rem.includes('wh')) {
            category = 'Dock Jam';
            actionRequired = 'Escalate with client WH dock coordinator to authorize fast-track bay';
          }

          return { ...r, category, actionRequired };
        });
      }, [delayedRecords]);

      const filteredAiDelays = useMemo(() => {
        if (aiDelayCategory === 'ALL') return categorizedDelays;
        return categorizedDelays.filter(d => d.category === aiDelayCategory);
      }, [categorizedDelays, aiDelayCategory]);

      const uniqueClients = useMemo(() => Array.from(new Set(records.map(r => r.client))).filter(Boolean), [records]);
      const uniqueStaff = useMemo(() => Array.from(new Set(records.map(r => r.staff))).filter(Boolean), [records]);

      const daysInMonth = (year, month) => new Date(year, month + 1, 0).getDate();
      const firstDayOffset = (year, month) => new Date(year, month, 1).getDay();

      const calendarDays = useMemo(() => {
        const days = [];
        const totalDays = daysInMonth(calYear, calMonth);
        const offset = firstDayOffset(calYear, calMonth);
        const adjustedOffset = offset === 0 ? 6 : offset - 1;

        for (let i = 0; i < adjustedOffset; i++) {
          days.push(null);
        }
        for (let d = 1; d <= totalDays; d++) {
          const dateStr = `${calYear}-${String(calMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
          days.push({ day: d, dateStr });
        }
        return days;
      }, [calYear, calMonth]);

      const handleGenerateAiReport = () => {
        setAiGenerating(true);
        setTimeout(() => {
          setAiGenerating(false);
          setAiReportOutput({
            summary: `Automated analysis completed across ${delayedRecords.length} delayed operations. Critical friction identified in Rewari corridor and NH48 toll junction.`,
            criticalFlags: [
              'High frequency breakdown on Haryana/Rajasthan freight corridor (DL/HR vehicles). Recommend mandatory fleet radiator & tyre pressure inspections prior to departure.',
              'Single Driver regulations breached on long hauls exceeding 500km (KA-05-FF-4321). Enforce dual-pilot rosters for all south-bound transit.',
              'Flipkart & Reliance retail delivery docks experiencing 3.2 hr average handover turnarounds. Issue formal dock bay reservation notices to client hub managers.'
            ],
            immediateOrders: [
              'Action Order #1: Route vehicle HR-26-EE-9901 to nearest authorized workshop for suspension check.',
              'Action Order #2: Issue automated driver changeover alert for Bangalore-Chennai corridor.',
              'Action Order #3: Apply contractual grace period waivers for NH48 toll choke points.'
            ]
          });
        }, 800);
      };

      const getSlaStyle = (sla) => {
        if (sla >= 80) return { color: 'var(--num-closed)' };
        if (sla >= 50) return { color: 'var(--num-transit)' };
        return { color: 'var(--num-delay)' };
      };

      return (
        <div className="flex flex-col md:flex-row min-h-screen">
          
          {/* Mobile Top Bar */}
          <div className="md:hidden glass-panel px-4 py-3 flex items-center justify-between sticky top-0 z-50">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg accent-btn flex items-center justify-center shadow-lg">
                <i data-lucide="shield" className="w-4 h-4"></i>
              </div>
              <div>
                <span className="font-black text-xs tracking-wider">FLEET CONTROL</span>
                <p className="text-[9px] font-mono tracking-tight" style={{ color: 'var(--text-muted)' }}>Logistics Command Center</p>
              </div>
            </div>
            <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-1.5 rounded-lg" style={{ background: 'var(--bg-header)', color: 'var(--accent)' }}>
              <i data-lucide={mobileMenuOpen ? "x" : "menu"} className="w-5 h-5"></i>
            </button>
          </div>

          {/* Mobile Drawer */}
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div 
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="md:hidden fixed inset-x-0 top-14 bottom-0 z-40 p-4 flex flex-col space-y-2 backdrop-blur-xl"
                style={{ background: 'var(--bg-main)' }}
              >
                {[
                  { id: 'overall', label: 'Over All Performance', icon: 'activity' },
                  { id: 'client', label: 'Client Wise Performance', icon: 'briefcase' },
                  { id: 'staff', label: 'Staff Wise Performance', icon: 'user' },
                  { id: 'arrival', label: 'Day Wise Arrival Report', icon: 'calendar' },
                  { id: 'delay', label: 'Only Delay Arrival Report', icon: 'alert-triangle' },
                  { id: 'ai_review', label: 'AI Delay Review', icon: 'bot' },
                ].map((item, idx) => (
                  <button
                    key={item.id}
                    onClick={() => { setActiveTab(item.id); setMobileMenuOpen(false); }}
                    className={`w-full flex items-center space-x-3 px-4 py-3.5 rounded-2xl text-[11px] font-bold transition-all ${
                      activeTab === item.id ? 'sidebar-active' : ''
                    }`}
                    style={activeTab !== item.id ? { color: 'var(--text-muted)' } : {}}
                  >
                    <i data-lucide={item.icon} className="w-4 h-4 shrink-0"></i>
                    <span>{item.label}</span>
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Desktop Sidebar */}
          <aside className="hidden md:flex md:w-60 glass-panel border-r p-4 flex-col shrink-0 justify-between">
            <div className="space-y-6">
              <div className="flex items-center space-x-3 px-2 py-1">
                <div className="w-9 h-9 rounded-xl accent-btn flex items-center justify-center shadow-lg">
                  <i data-lucide="shield" className="w-4 h-4"></i>
                </div>
                <div>
                  <span className="font-black text-xs tracking-wider">FLEET CONTROL</span>
                  <p className="text-[9px] font-mono tracking-tight" style={{ color: 'var(--text-muted)' }}>Logistics Command Center</p>
                </div>
              </div>

              <nav className="space-y-1.5">
                {[
                  { id: 'overall', label: 'Over All Performance', icon: 'activity' },
                  { id: 'client', label: 'Client Wise Performance', icon: 'briefcase' },
                  { id: 'staff', label: 'Staff Wise Performance', icon: 'user' },
                  { id: 'arrival', label: 'Day Wise Arrival Report', icon: 'calendar' },
                  { id: 'delay', label: 'Only Delay Arrival Report', icon: 'alert-triangle' },
                  { id: 'ai_review', label: 'AI Delay Review', icon: 'bot' },
                ].map((item) => {
                  const isActive = activeTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveTab(item.id)}
                      className={`relative w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-2xl text-[11px] font-bold transition-all ${
                        isActive ? 'sidebar-active' : ''
                      }`}
                      style={!isActive ? { color: 'var(--text-muted)' } : {}}
                    >
                      <i data-lucide={item.icon} className="w-4 h-4 shrink-0"></i>
                      <span className="truncate tracking-wide">{item.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>

            <div className="pt-4 border-t text-[10px] font-mono flex items-center justify-between px-2" style={{ borderColor: 'var(--border-color)', color: 'var(--text-muted)' }}>
              <span>SYSTEM</span>
              <span className="flex items-center space-x-1.5">
                <span className="w-1.5 h-1.5 rounded-full animate-ping" style={{ background: 'var(--accent)' }}></span>
                <span className="font-bold" style={{ color: 'var(--accent)' }}>ONLINE</span>
              </span>
            </div>
          </aside>

          {/* Main Workspace */}
          <main className="flex-1 p-3 md:p-7 max-w-7xl mx-auto w-full space-y-5">
            
            {/* Top Bar with Theme Switcher & Upload Button */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b" style={{ borderColor: 'var(--border-color)' }}>
              <div>
                <h1 className="text-2xl md:text-3xl font-black tracking-tight">
                  {activeTab === 'overall' && 'Over All Performance'}
                  {activeTab === 'client' && 'Client Wise Performance Report'}
                  {activeTab === 'staff' && 'Staff Wise Performance Report'}
                  {activeTab === 'arrival' && 'Day Wise Arrival Chronology'}
                  {activeTab === 'delay' && 'Only Delay Arrival Exceptions'}
                  {activeTab === 'ai_review' && 'AI Operational Delay Review'}
                </h1>
                <p className="text-xs font-medium mt-0.5" style={{ color: 'var(--text-muted)' }}>
                  Real-time operational telemetry, SLA compliance, and dispatch management
                </p>
              </div>

              <div className="flex items-center space-x-2.5 shrink-0">
                
                {/* THEME / COLOUR SWITCHER BUTTON */}
                <div className="relative">
                  <button
                    onClick={() => setShowThemeMenu(!showThemeMenu)}
                    className="flex items-center space-x-2 px-3.5 py-2 rounded-xl text-[11px] font-bold border transition"
                    style={{ background: 'var(--bg-header)', borderColor: 'var(--border-color)', color: 'var(--text-main)' }}
                  >
                    <span className="w-3 h-3 rounded-full" style={{ background: THEMES[themeKey].dot }}></span>
                    <i data-lucide="palette" className="w-3.5 h-3.5" style={{ color: 'var(--accent)' }}></i>
                    <span>Theme: {THEMES[themeKey].name}</span>
                    <i data-lucide="chevron-down" className="w-3 h-3" style={{ color: 'var(--text-muted)' }}></i>
                  </button>

                  {showThemeMenu && (
                    <div className="absolute right-0 mt-2 w-48 rounded-2xl p-2 shadow-2xl z-50 glass-panel space-y-1">
                      {Object.entries(THEMES).map(([k, th]) => (
                        <button
                          key={k}
                          onClick={() => { setThemeKey(k); setShowThemeMenu(false); }}
                          className="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-bold transition"
                          style={{
                            background: themeKey === k ? 'var(--bg-hover)' : 'transparent',
                            color: 'var(--text-main)'
                          }}
                        >
                          <div className="flex items-center space-x-2.5">
                            <span className="w-3 h-3 rounded-full border border-white/20" style={{ background: th.dot }}></span>
                            <span>{th.name}</span>
                          </div>
                          {themeKey === k && <i data-lucide="check" className="w-3.5 h-3.5" style={{ color: 'var(--accent)' }}></i>}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Upload Excel Button */}
                {activeTab === 'overall' && (
                  <label className="flex items-center space-x-2 px-4 py-2 rounded-xl accent-btn text-[11px] font-black cursor-pointer transition-all shadow-sm">
                    <i data-lucide="upload-cloud" className="w-4 h-4"></i>
                    <span>{uploadedFileCount > 0 ? `${uploadedFileCount} File(s) Uploaded` : 'Upload Multiple Excel'}</span>
                    <input
                      type="file"
                      accept=".xlsx, .xls, .csv"
                      multiple
                      onChange={handleMultipleFileUpload}
                      className="hidden"
                    />
                  </label>
                )}
              </div>
            </div>

            {/* CLEAN BORDERLESS NUMBERS ONLY (NO CARDS) */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 py-3 px-1 border-b" style={{ borderColor: 'var(--border-color)' }}>
              <motion.div
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}
                className="flex items-baseline space-x-3 border-l-2 pl-4"
                style={{ borderColor: 'var(--num-total)' }}
              >
                <span className="text-3xl md:text-4xl font-black font-mono tracking-tight" style={{ color: 'var(--num-total)' }}>
                  {metrics.total}
                </span>
                <div>
                  <div className="text-[11px] font-black uppercase tracking-wider">TOTAL TRIPS</div>
                  <div className="text-[9px] font-medium" style={{ color: 'var(--text-muted)' }}>All recorded dispatches</div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.08 }}
                className="flex items-baseline space-x-3 border-l-2 pl-4"
                style={{ borderColor: 'var(--num-closed)' }}
              >
                <span className="text-3xl md:text-4xl font-black font-mono tracking-tight" style={{ color: 'var(--num-closed)' }}>
                  {metrics.closed}
                </span>
                <div>
                  <div className="text-[11px] font-black uppercase tracking-wider">TOTAL TRIP CLOSED</div>
                  <div className="text-[9px] font-medium" style={{ color: 'var(--text-muted)' }}>Successfully delivered</div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.16 }}
                className="flex items-baseline space-x-3 border-l-2 pl-4"
                style={{ borderColor: 'var(--num-transit)' }}
              >
                <span className="text-3xl md:text-4xl font-black font-mono tracking-tight" style={{ color: 'var(--num-transit)' }}>
                  {metrics.inTransit}
                </span>
                <div>
                  <div className="text-[11px] font-black uppercase tracking-wider">IN-TRANSIT VEHICLE</div>
                  <div className="text-[9px] font-medium" style={{ color: 'var(--text-muted)' }}>Active on route</div>
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.24 }}
                className="flex items-baseline space-x-3 border-l-2 pl-4"
                style={{ borderColor: 'var(--num-delay)' }}
              >
                <span className="text-3xl md:text-4xl font-black font-mono tracking-tight" style={{ color: 'var(--num-delay)' }}>
                  {metrics.delayed}
                </span>
                <div>
                  <div className="text-[11px] font-black uppercase tracking-wider">DELAY TRIP CLOSED</div>
                  <div className="text-[9px] font-medium" style={{ color: 'var(--text-muted)' }}>Exceptions & late arrivals</div>
                </div>
              </motion.div>
            </div>

            {/* Tab Views */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                {activeTab === 'overall' && (
                  <div className="space-y-6">
                    {/* CLIENT WISE */}
                    <div className="glass-panel rounded-3xl p-5 space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'var(--bg-header)', border: '1px solid var(--border-color)', color: 'var(--accent)' }}>
                            <i data-lucide="briefcase" className="w-4 h-4"></i>
                          </div>
                          <h2 className="text-sm font-black tracking-wide">Client Wise Performance Report</h2>
                        </div>
                        <span className="text-[10px] font-mono px-3 py-1 rounded-xl font-bold" style={{ background: 'var(--bg-header)', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>
                          {clientStats.length} Accounts
                        </span>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-[11px] grid-table">
                          <thead>
                            <tr>
                              <th className="py-3 px-4">CLIENT NAME</th>
                              <th className="py-3 px-4 text-center">TOTAL TRIPS</th>
                              <th className="py-3 px-4 text-center">TRIP CLOSED</th>
                              <th className="py-3 px-4 text-center">DELAY CLOSED</th>
                              <th className="py-3 px-4 text-center">ON-TIME SLA %</th>
                            </tr>
                          </thead>
                          <tbody>
                            {clientStats.map((c, i) => (
                              <tr key={i} className="transition-colors">
                                <td className="py-3 px-4 flex items-center space-x-3">
                                  <ClientBrandBadge name={c.name} />
                                  <span className="font-bold tracking-wide">{c.name}</span>
                                </td>
                                <td className="py-3 px-4 text-center font-mono font-bold">{c.total}</td>
                                <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-closed)' }}>{c.closed}</td>
                                <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-delay)' }}>{c.delayed}</td>
                                <td className="py-3 px-4 text-center">
                                  <span className="font-mono text-sm font-black" style={getSlaStyle(c.sla)}>{c.sla}%</span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* STAFF WISE */}
                    <div className="glass-panel rounded-3xl p-5 space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'var(--bg-header)', border: '1px solid var(--border-color)', color: 'var(--accent)' }}>
                            <i data-lucide="user" className="w-4 h-4"></i>
                          </div>
                          <h2 className="text-sm font-black tracking-wide">Staff Wise Performance Report</h2>
                        </div>
                        <span className="text-[10px] font-mono px-3 py-1 rounded-xl font-bold" style={{ background: 'var(--bg-header)', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>
                          {staffStats.length} Drivers
                        </span>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-[11px] grid-table">
                          <thead>
                            <tr>
                              <th className="py-3 px-4">STAFF / DRIVER</th>
                              <th className="py-3 px-4 text-center">TOTAL ASSIGNED</th>
                              <th className="py-3 px-4 text-center">TRIP CLOSED</th>
                              <th className="py-3 px-4 text-center">DELAY CLOSED</th>
                              <th className="py-3 px-4 text-center">ON-TIME SLA %</th>
                            </tr>
                          </thead>
                          <tbody>
                            {staffStats.map((s, i) => (
                              <tr key={i} className="transition-colors">
                                <td className="py-3 px-4 font-bold tracking-wide">{s.name}</td>
                                <td className="py-3 px-4 text-center font-mono font-bold">{s.total}</td>
                                <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-closed)' }}>{s.closed}</td>
                                <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-delay)' }}>{s.delayed}</td>
                                <td className="py-3 px-4 text-center">
                                  <span className="font-mono text-sm font-black" style={getSlaStyle(s.sla)}>{s.sla}%</span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* ROUTE WISE */}
                    <div className="glass-panel rounded-3xl p-5 space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'var(--bg-header)', border: '1px solid var(--border-color)', color: 'var(--accent)' }}>
                            <i data-lucide="map-pin" className="w-4 h-4"></i>
                          </div>
                          <h2 className="text-sm font-black tracking-wide">Route Wise Performance Report</h2>
                        </div>
                        <span className="text-[10px] font-mono px-3 py-1 rounded-xl font-bold" style={{ background: 'var(--bg-header)', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>
                          {routeStats.length} Corridors
                        </span>
                      </div>

                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-[11px] grid-table">
                          <thead>
                            <tr>
                              <th className="py-3 px-4">ROUTE / CORRIDOR</th>
                              <th className="py-3 px-4 text-center">TOTAL DISPATCHES</th>
                              <th className="py-3 px-4 text-center">TRIP CLOSED</th>
                              <th className="py-3 px-4 text-center">DELAY CLOSED</th>
                              <th className="py-3 px-4 text-center">CORRIDOR SLA %</th>
                            </tr>
                          </thead>
                          <tbody>
                            {routeStats.map((r, i) => (
                              <tr key={i} className="transition-colors">
                                <td className="py-3 px-4 font-mono font-bold">{r.name}</td>
                                <td className="py-3 px-4 text-center font-mono font-bold">{r.total}</td>
                                <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-closed)' }}>{r.closed}</td>
                                <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-delay)' }}>{r.delayed}</td>
                                <td className="py-3 px-4 text-center">
                                  <span className="font-mono text-sm font-black" style={getSlaStyle(r.sla)}>{r.sla}%</span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'client' && (
                  <div className="glass-panel rounded-3xl p-5 space-y-4">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[11px] grid-table">
                        <thead>
                          <tr>
                            <th className="py-3 px-4">CLIENT NAME</th>
                            <th className="py-3 px-4 text-center">TOTAL TRIPS</th>
                            <th className="py-3 px-4 text-center">TRIP CLOSED</th>
                            <th className="py-3 px-4 text-center">DELAY CLOSED</th>
                            <th className="py-3 px-4 text-center">ON-TIME SLA %</th>
                          </tr>
                        </thead>
                        <tbody>
                          {clientStats.map((c, i) => (
                            <tr key={i} className="transition-colors">
                              <td className="py-3 px-4 flex items-center space-x-3">
                                <ClientBrandBadge name={c.name} />
                                <span className="font-bold tracking-wide">{c.name}</span>
                              </td>
                              <td className="py-3 px-4 text-center font-mono font-bold">{c.total}</td>
                              <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-closed)' }}>{c.closed}</td>
                              <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-delay)' }}>{c.delayed}</td>
                              <td className="py-3 px-4 text-center">
                                <span className="font-mono text-sm font-black" style={getSlaStyle(c.sla)}>{c.sla}%</span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {activeTab === 'staff' && (
                  <div className="glass-panel rounded-3xl p-5 space-y-4">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[11px] grid-table">
                        <thead>
                          <tr>
                            <th className="py-3 px-4">STAFF / DRIVER</th>
                            <th className="py-3 px-4 text-center">TOTAL ASSIGNED</th>
                            <th className="py-3 px-4 text-center">TRIP CLOSED</th>
                            <th className="py-3 px-4 text-center">DELAY CLOSED</th>
                            <th className="py-3 px-4 text-center">ON-TIME SLA %</th>
                          </tr>
                        </thead>
                        <tbody>
                          {staffStats.map((s, i) => (
                            <tr key={i} className="transition-colors">
                              <td className="py-3 px-4 font-bold tracking-wide">{s.name}</td>
                              <td className="py-3 px-4 text-center font-mono font-bold">{s.total}</td>
                              <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-closed)' }}>{s.closed}</td>
                              <td className="py-3 px-4 text-center font-mono font-bold" style={{ color: 'var(--num-delay)' }}>{s.delayed}</td>
                              <td className="py-3 px-4 text-center">
                                <span className="font-mono text-sm font-black" style={getSlaStyle(s.sla)}>{s.sla}%</span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {activeTab === 'arrival' && (
                  <div className="glass-panel rounded-3xl p-5 space-y-5">
                    <div className="flex flex-wrap items-center justify-between gap-3 pb-2">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'var(--bg-header)', border: '1px solid var(--border-color)', color: 'var(--accent)' }}>
                          <i data-lucide="calendar" className="w-4 h-4"></i>
                        </div>
                        <h2 className="text-sm font-black tracking-wide">Day Wise Arrival Chronology</h2>
                      </div>

                      <div className="flex flex-wrap items-center gap-2.5">
                        <select
                          value={selectedClientFilter}
                          onChange={(e) => setSelectedClientFilter(e.target.value)}
                          className="text-[11px] font-bold rounded-xl px-4 py-2 focus:outline-none cursor-pointer border"
                          style={{ background: 'var(--bg-header)', borderColor: 'var(--border-color)', color: 'var(--text-main)' }}
                        >
                          <option value="">All Clients</option>
                          {uniqueClients.map((cl, idx) => <option key={idx} value={cl}>{cl}</option>)}
                        </select>

                        <select
                          value={selectedStaffFilter}
                          onChange={(e) => setSelectedStaffFilter(e.target.value)}
                          className="text-[11px] font-bold rounded-xl px-4 py-2 focus:outline-none cursor-pointer border"
                          style={{ background: 'var(--bg-header)', borderColor: 'var(--border-color)', color: 'var(--text-main)' }}
                        >
                          <option value="">All Staff / Drivers</option>
                          {uniqueStaff.map((st, idx) => <option key={idx} value={st}>{st}</option>)}
                        </select>

                        <div className="relative">
                          <button
                            onClick={() => setShowCalendar(!showCalendar)}
                            className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-mono font-bold border transition"
                            style={{ background: 'var(--bg-header)', borderColor: 'var(--border-color)', color: 'var(--accent)' }}
                          >
                            <i data-lucide="calendar" className="w-4 h-4"></i>
                            <span>{selectedDate || 'Select Date'}</span>
                            <i data-lucide="chevron-down" className="w-3 h-3"></i>
                          </button>

                          {showCalendar && (
                            <div className="absolute right-0 mt-2 z-50 w-60 glass-panel rounded-2xl p-4 shadow-2xl space-y-3">
                              <div className="flex items-center justify-between text-xs font-bold">
                                <button onClick={() => { if (calMonth === 0) { setCalMonth(11); setCalYear(calYear - 1); } else { setCalMonth(calMonth - 1); } }} className="p-1.5 rounded-lg" style={{ color: 'var(--accent)' }}>
                                  <i data-lucide="chevron-left" className="w-4 h-4"></i>
                                </button>
                                <span className="font-mono text-[11px]">
                                  {["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][calMonth]} {calYear}
                                </span>
                                <button onClick={() => { if (calMonth === 11) { setCalMonth(0); setCalYear(calYear + 1); } else { setCalMonth(calMonth + 1); } }} className="p-1.5 rounded-lg" style={{ color: 'var(--accent)' }}>
                                  <i data-lucide="chevron-right" className="w-4 h-4"></i>
                                </button>
                              </div>
                              <div className="grid grid-cols-7 text-center text-[10px] font-black font-mono" style={{ color: 'var(--text-muted)' }}>
                                <span>MO</span><span>TU</span><span>WE</span><span>TH</span><span>FR</span><span>SA</span><span>SU</span>
                              </div>
                              <div className="grid grid-cols-7 gap-1">
                                {calendarDays.map((item, idx) => {
                                  if (!item) return <div key={idx} className="h-7 w-7"></div>;
                                  const isSelected = selectedDate === item.dateStr;
                                  return (
                                    <button
                                      key={idx}
                                      onClick={() => { setSelectedDate(item.dateStr); setShowCalendar(false); }}
                                      className={`h-7 w-7 rounded-lg text-[10px] font-mono font-bold flex items-center justify-center transition-colors ${
                                        isSelected ? 'accent-btn' : ''
                                      }`}
                                    >
                                      {item.day}
                                    </button>
                                  );
                                })}
                              </div>
                              <div className="pt-2 border-t flex items-center justify-between text-[10px]" style={{ borderColor: 'var(--border-color)' }}>
                                <button onClick={() => { setSelectedDate(''); setShowCalendar(false); }} className="font-black" style={{ color: 'var(--num-delay)' }}>Clear Date</button>
                                <button onClick={() => setShowCalendar(false)} className="font-black" style={{ color: 'var(--text-muted)' }}>Close</button>
                              </div>
                            </div>
                          )}
                        </div>

                        {(selectedDate || selectedClientFilter || selectedStaffFilter) && (
                          <button
                            onClick={() => { setSelectedDate(''); setSelectedClientFilter(''); setSelectedStaffFilter(''); }}
                            className="p-2 rounded-xl border transition"
                            style={{ background: 'var(--bg-header)', borderColor: 'var(--border-color)', color: 'var(--num-delay)' }}
                            title="Reset Filters"
                          >
                            <i data-lucide="x" className="w-4 h-4"></i>
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[11px] grid-table">
                        <thead>
                          <tr>
                            <th className="py-3 px-4">VEHICLE NO</th>
                            <th className="py-3 px-4">CLIENT</th>
                            <th className="py-3 px-4">STAFF / DRIVER</th>
                            <th className="py-3 px-4">ROUTE</th>
                            <th className="py-3 px-4">ARRIVAL STATUS</th>
                            <th className="py-3 px-4">REMARKS</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredArrivals.length === 0 ? (
                            <tr>
                              <td colSpan="6" className="py-12 text-center font-mono font-bold text-xs" style={{ color: 'var(--text-muted)' }}>
                                No matching dispatches found.
                              </td>
                            </tr>
                          ) : (
                            filteredArrivals.map((row, idx) => (
                              <tr key={idx} className="transition-colors">
                                <td className="py-3 px-4 font-mono font-bold tracking-wide">{row.vehicleNo}</td>
                                <td className="py-3 px-4 flex items-center space-x-3">
                                  <ClientBrandBadge name={row.client} />
                                  <span className="font-bold tracking-wide">{row.client}</span>
                                </td>
                                <td className="py-3 px-4 font-medium">{row.staff}</td>
                                <td className="py-3 px-4 font-mono text-[10px]" style={{ color: 'var(--text-muted)' }}>{row.route}</td>
                                <td className="py-3 px-4">
                                  <span className="px-2.5 py-1 rounded-md text-[9px] font-black uppercase tracking-wider" style={{
                                    background: 'var(--bg-header)',
                                    color: row.status.toLowerCase().includes('closed') ? 'var(--num-closed)' : 'var(--num-transit)'
                                  }}>
                                    {row.status}
                                  </span>
                                </td>
                                <td className="py-3 px-4 text-[10px] font-medium italic" style={{ color: 'var(--text-muted)' }}>{row.remarks}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {activeTab === 'delay' && (
                  <div className="glass-panel rounded-3xl p-5 space-y-4">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[11px] grid-table">
                        <thead>
                          <tr>
                            <th className="py-3 px-4">TRIP ID</th>
                            <th className="py-3 px-4">VEHICLE NO</th>
                            <th className="py-3 px-4">CLIENT</th>
                            <th className="py-3 px-4">STAFF / DRIVER</th>
                            <th className="py-3 px-4">ROUTE</th>
                            <th className="py-3 px-4">DELAY REMARKS</th>
                          </tr>
                        </thead>
                        <tbody>
                          {delayedRecords.map((d, i) => (
                            <tr key={i} className="transition-colors">
                              <td className="py-3 px-4 font-mono font-medium" style={{ color: 'var(--text-muted)' }}>{d.id}</td>
                              <td className="py-3 px-4 font-mono font-bold">{d.vehicleNo}</td>
                              <td className="py-3 px-4 flex items-center space-x-3">
                                <ClientBrandBadge name={d.client} />
                                <span className="font-bold">{d.client}</span>
                              </td>
                              <td className="py-3 px-4 font-medium">{d.staff}</td>
                              <td className="py-3 px-4 font-mono text-[10px]" style={{ color: 'var(--text-muted)' }}>{d.route}</td>
                              <td className="py-3 px-4">
                                <span className="inline-block px-3 py-1 rounded-lg text-[10px] font-bold" style={{ background: 'var(--bg-header)', color: 'var(--num-delay)' }}>
                                  {d.remarks}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {activeTab === 'ai_review' && (
                  <div className="space-y-6">
                    <div className="glass-panel rounded-3xl p-5 space-y-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: 'var(--bg-header)', border: '1px solid var(--border-color)', color: 'var(--accent)' }}>
                            <i data-lucide="bot" className="w-4 h-4"></i>
                          </div>
                          <h2 className="text-sm font-black tracking-wide">Root Cause Delay Categorization</h2>
                        </div>

                        <button
                          onClick={handleGenerateAiReport}
                          disabled={aiGenerating}
                          className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl accent-btn text-[11px] font-black cursor-pointer transition-colors shadow-sm shrink-0"
                        >
                          <i data-lucide={aiGenerating ? "loader" : "sparkles"} className={`w-4 h-4 ${aiGenerating ? 'animate-spin' : ''}`}></i>
                          <span>{aiGenerating ? 'Analyzing Remarks...' : 'Generate AI Action Plan'}</span>
                        </button>
                      </div>

                      <div className="flex flex-wrap items-center gap-2 pt-2">
                        {[
                          { id: 'ALL', label: 'All Delays' },
                          { id: 'Breakdown', label: 'Breakdown / Mechanical' },
                          { id: 'Driver Issue', label: 'Driver Issue / Absence' },
                          { id: 'Traffic Jam', label: 'Traffic Jam / Highway' },
                          { id: 'Single Driver', label: 'Single Driver Fatigue' },
                          { id: 'Dock Jam', label: 'Dock Congestion' },
                        ].map(cat => {
                          const count = cat.id === 'ALL' ? categorizedDelays.length : categorizedDelays.filter(c => c.category === cat.id).length;
                          const isActive = aiDelayCategory === cat.id;
                          return (
                            <button
                              key={cat.id}
                              onClick={() => setAiDelayCategory(cat.id)}
                              className={`px-3 py-1.5 rounded-xl text-[10px] font-bold transition flex items-center space-x-2 border ${
                                isActive ? 'accent-btn' : ''
                              }`}
                              style={!isActive ? { background: 'var(--bg-header)', borderColor: 'var(--border-color)', color: 'var(--text-muted)' } : { borderColor: 'transparent' }}
                            >
                              <span>{cat.label}</span>
                              <span className="px-1.5 py-0.5 rounded-md text-[9px] font-mono bg-black/20">
                                {count}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {aiReportOutput && (
                      <div className="glass-panel rounded-3xl p-6 space-y-4">
                        <div className="flex items-center space-x-2 text-xs font-black uppercase tracking-wider" style={{ color: 'var(--accent)' }}>
                          <i data-lucide="zap" className="w-4 h-4"></i>
                          <span>AI Operational Directive</span>
                        </div>
                        <p className="text-sm font-medium leading-relaxed">{aiReportOutput.summary}</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                          <div className="space-y-2 p-4 rounded-2xl border" style={{ background: 'var(--bg-header)', borderColor: 'var(--border-color)' }}>
                            <div className="text-[10px] font-black uppercase tracking-wider" style={{ color: 'var(--num-delay)' }}>Operational Bottlenecks</div>
                            <ul className="space-y-1.5 text-xs list-disc list-inside font-medium leading-snug" style={{ color: 'var(--text-muted)' }}>
                              {aiReportOutput.criticalFlags.map((flag, idx) => <li key={idx}>{flag}</li>)}
                            </ul>
                          </div>
                          <div className="space-y-2 p-4 rounded-2xl border" style={{ background: 'var(--bg-header)', borderColor: 'var(--border-color)' }}>
                            <div className="text-[10px] font-black uppercase tracking-wider" style={{ color: 'var(--num-closed)' }}>Immediate Actions</div>
                            <ul className="space-y-1.5 text-xs list-disc list-inside font-medium leading-snug" style={{ color: 'var(--text-muted)' }}>
                              {aiReportOutput.immediateOrders.map((ord, idx) => <li key={idx}>{ord}</li>)}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}

                    <div className="glass-panel rounded-3xl p-5 space-y-4">
                      <div className="overflow-x-auto">
                        <table className="w-full text-left text-[11px] grid-table">
                          <thead>
                            <tr>
                              <th className="py-3 px-4">VEHICLE NO</th>
                              <th className="py-3 px-4">CLIENT</th>
                              <th className="py-3 px-4">CATEGORY</th>
                              <th className="py-3 px-4">DELAY REMARKS</th>
                              <th className="py-3 px-4">ACTION REQUIRED</th>
                            </tr>
                          </thead>
                          <tbody>
                            {filteredAiDelays.map((v, i) => (
                              <tr key={i} className="transition-colors">
                                <td className="py-3 px-4 font-mono font-bold">{v.vehicleNo}</td>
                                <td className="py-3 px-4 flex items-center space-x-3">
                                  <ClientBrandBadge name={v.client} />
                                  <span className="font-bold">{v.client}</span>
                                </td>
                                <td className="py-3 px-4">
                                  <span className="px-2.5 py-1 rounded-md text-[9px] font-black uppercase" style={{ background: 'var(--bg-header)', color: 'var(--num-delay)' }}>
                                    {v.category}
                                  </span>
                                </td>
                                <td className="py-3 px-4 text-[10px] font-medium italic" style={{ color: 'var(--text-muted)' }}>{v.remarks}</td>
                                <td className="py-3 px-4">
                                  <span className="font-bold text-[10px] flex items-center space-x-2" style={{ color: 'var(--num-closed)' }}>
                                    <i data-lucide="arrow-right" className="w-3.5 h-3.5 shrink-0"></i>
                                    <span>{v.actionRequired}</span>
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>

          </main>
        </div>
      );
    }

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
  </script>
</body>
</html>
"""

components.html(html_code, height=950, scrolling=True)

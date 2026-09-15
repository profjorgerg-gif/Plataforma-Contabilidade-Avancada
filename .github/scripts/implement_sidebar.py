from pathlib import Path
p=Path('public/app.js'); s=p.read_text(encoding='utf-8')
old="""    let inner = `<div class=\"masthead\"><div class=\"masthead-row\">
      <div>
        <h1 class=\"serif\">Contabilidade Avançada</h1>
        <div class=\"kicker\">Sala de aula — provisões, resultado, destinações, IRPF e ganho de capital</div>
      </div>
      <div class=\"userbadge\">${roleLabel}: <b>${esc(state.user.name)}</b>
        <button id=\"btn-logout\">sair</button>
      </div>
    </div>
    ${renderNav()}
    </div>
    <div class=\"wrap\">`;"""
new="""    let inner = `<div class=\"app-shell\"><aside class=\"sidebar\" id=\"app-sidebar\"><div class=\"sidebar-brand\"><div class=\"sidebar-logo\">CA</div><div><b>Contabilidade Avançada</b><small>CEDUP Hermann Hering</small></div></div>${renderNav()}<div class=\"sidebar-user\"><span>${roleLabel}</span><b>${esc(state.user.name)}</b><button id=\"btn-logout\">Sair</button></div></aside><div class=\"app-main\"><div class=\"mobile-bar\"><button id=\"btn-sidebar-toggle\" aria-label=\"Abrir menu\">☰</button><div><b>Contabilidade Avançada</b><small>${roleLabel}</small></div></div><div class=\"masthead\"><div class=\"masthead-row\"><div><h1 class=\"serif\">Contabilidade Avançada</h1><div class=\"kicker\">Sala de aula — provisões, resultado, destinações, IRPF e ganho de capital</div></div></div></div><div class=\"wrap\">`;"""
if old not in s: raise SystemExit('render shell não encontrado')
s=s.replace(old,new)
s=s.replace("    inner += `</div>`;\n    root.innerHTML = inner;", "    inner += `</div></div></div><div class=\"sidebar-overlay\" id=\"sidebar-overlay\"></div>`;\n    root.innerHTML = inner;")
oldnav="""    return `<div class=\"topnav\">` + items.map(([key,label]) => {
      let active = false;
      if (key.startsWith('professor:')){
        active = state.view === 'professor' && state.professorTab === key.split(':')[1];
      } else {
        active = state.view === key;
      }
      return `<div class=\"nav-item ${active?'active':''}\" data-nav=\"${key}\">${esc(label)}</div>`;
    }).join('') + `</div>`;"""
newnav="""    const icons={dashboard:'⌂',notas:'★',manual:'▤',suporte:'◉','professor:turmas':'▦','professor:planejamento':'▣','professor:acompanhamento':'▥','professor:correcoes':'!','professor:relatorios':'▧','professor:backup':'⇩','professor:auditoria':'◎','professor:operacional':'▤','professor:checklist':'✓','professor:guia':'◇',usuarios:'♙'};
    const groups = role==='professor' ? [['GESTÃO',['professor:turmas','professor:planejamento']],['ACOMPANHAMENTO',['professor:acompanhamento','professor:correcoes','professor:relatorios']],['FERRAMENTAS',['professor:backup','professor:auditoria']],['ORIENTAÇÕES',['professor:operacional','professor:checklist','professor:guia','manual']],['OUTROS',['suporte']]] : role==='aluno' ? [['APRENDIZADO',['dashboard','notas','manual']],['OUTROS',['suporte']]] : [['ADMINISTRAÇÃO',['usuarios']],['OUTROS',['suporte']]];
    const byKey=Object.fromEntries(items);
    return `<nav class=\"side-nav\">`+groups.map(([title,keys])=>`<div class=\"side-group\"><div class=\"side-group-title\">${title}</div>${keys.filter(k=>byKey[k]).map(key=>{let active=key.startsWith('professor:')?(state.view==='professor'&&state.professorTab===key.split(':')[1]):state.view===key;return `<button class=\"nav-item ${active?'active':''}\" data-nav=\"${key}\"><span class=\"nav-icon\">${icons[key]||'•'}</span><span>${esc(byKey[key])}</span></button>`;}).join('')}</div>`).join('')+`</nav>`;"""
if oldnav not in s: raise SystemExit('renderNav não encontrado')
s=s.replace(oldnav,newnav)
needle="""    const logout = document.getElementById('btn-logout');
    if (logout) logout.addEventListener('click', () => requestLogoutWithBackup());"""
replacement=needle+"""
    const sidebar=document.getElementById('app-sidebar'), sidebarToggle=document.getElementById('btn-sidebar-toggle'), sidebarOverlay=document.getElementById('sidebar-overlay');
    const closeSidebar=()=>document.body.classList.remove('sidebar-open');
    if(sidebarToggle) sidebarToggle.addEventListener('click',()=>document.body.classList.toggle('sidebar-open'));
    if(sidebarOverlay) sidebarOverlay.addEventListener('click',closeSidebar);"""
s=s.replace(needle,replacement)
s=s.replace("        const key = item.getAttribute('data-nav');", "        const key = item.getAttribute('data-nav');\n        document.body.classList.remove('sidebar-open');")
p.write_text(s,encoding='utf-8')

p=Path('public/index.html'); h=p.read_text(encoding='utf-8')
anchor='  /* Login */\n'
css='''  /* Layout principal com menu lateral */\n  #cont-avancada .app-shell { min-height:100vh; display:flex; background:var(--paper); }\n  #cont-avancada .sidebar { width:270px; flex:0 0 270px; min-height:100vh; position:sticky; top:0; align-self:flex-start; height:100vh; overflow-y:auto; background:#101826; color:#F4F7FA; border-right:1px solid #26384A; display:flex; flex-direction:column; z-index:50; }\n  #cont-avancada .sidebar-brand { display:flex; gap:11px; align-items:center; padding:22px 18px; border-bottom:1px solid #26384A; }\n  #cont-avancada .sidebar-logo { width:40px; height:40px; border-radius:9px; display:grid; place-items:center; background:#17364A; color:#59C3E1; font-weight:800; border:1px solid #2E8CA8; }\n  #cont-avancada .sidebar-brand b { display:block; font-size:14px; line-height:1.2; }\n  #cont-avancada .sidebar-brand small { display:block; color:#91A8BA; font-size:11px; margin-top:3px; }\n  #cont-avancada .side-nav { padding:12px 0; flex:1; }\n  #cont-avancada .side-group { margin:0 0 10px; }\n  #cont-avancada .side-group-title { padding:10px 20px 6px; font-size:10px; letter-spacing:.11em; color:#6F879A; font-weight:700; }\n  #cont-avancada .sidebar .nav-item { width:100%; display:flex; align-items:center; gap:11px; border:0; border-left:3px solid transparent; background:transparent; color:#B8C7D4; padding:10px 17px; text-align:left; cursor:pointer; font:inherit; font-size:13.5px; }\n  #cont-avancada .sidebar .nav-item:hover { background:#182536; color:#fff; }\n  #cont-avancada .sidebar .nav-item.active { background:#223147; border-left-color:#2E8CA8; color:#fff; font-weight:600; }\n  #cont-avancada .nav-icon { width:21px; text-align:center; color:#62B8D0; font-size:15px; flex:0 0 21px; }\n  #cont-avancada .sidebar-user { border-top:1px solid #26384A; padding:14px 18px 18px; }\n  #cont-avancada .sidebar-user span,#cont-avancada .sidebar-user b { display:block; }\n  #cont-avancada .sidebar-user span { color:#71899B; font-size:10px; text-transform:uppercase; letter-spacing:.08em; }\n  #cont-avancada .sidebar-user b { font-size:12.5px; margin:3px 0 10px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }\n  #cont-avancada .sidebar-user button { border:1px solid #3B5063; background:transparent; color:#B8C7D4; border-radius:4px; padding:6px 11px; cursor:pointer; }\n  #cont-avancada .app-main { min-width:0; flex:1; }\n  #cont-avancada .app-main .wrap { max-width:1180px; }\n  #cont-avancada .mobile-bar { display:none; }\n  #cont-avancada .sidebar-overlay { display:none; }\n  @media (max-width:900px){\n    #cont-avancada .sidebar { position:fixed; left:0; top:0; transform:translateX(-102%); transition:transform .2s ease; box-shadow:8px 0 28px rgba(0,0,0,.25); }\n    body.sidebar-open #cont-avancada .sidebar { transform:translateX(0); }\n    #cont-avancada .sidebar-overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); z-index:40; }\n    body.sidebar-open #cont-avancada .sidebar-overlay { display:block; }\n    #cont-avancada .mobile-bar { display:flex; align-items:center; gap:12px; position:sticky; top:0; z-index:30; background:#101826; color:#F4F7FA; padding:10px 14px; border-bottom:1px solid #26384A; }\n    #cont-avancada .mobile-bar button { border:1px solid #3B5063; background:#15202F; color:#fff; width:38px; height:36px; border-radius:5px; font-size:20px; cursor:pointer; }\n    #cont-avancada .mobile-bar b,#cont-avancada .mobile-bar small { display:block; }\n    #cont-avancada .mobile-bar small { color:#91A8BA; font-size:10px; }\n    #cont-avancada .masthead { padding:16px 18px 12px; }\n    #cont-avancada .wrap { padding:20px 14px 50px; }\n  }\n\n'''
if anchor not in h: raise SystemExit('âncora CSS não encontrada')
h=h.replace(anchor,css+anchor,1)
p.write_text(h,encoding='utf-8')

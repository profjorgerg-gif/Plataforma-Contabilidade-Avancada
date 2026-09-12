from pathlib import Path
import re

app=Path('public/app.js')
s=app.read_text(encoding='utf-8')

anchor='''  function renderBackup(){\n'''
if anchor not in s: raise SystemExit('renderBackup anchor not found')
block=r'''  // ---- Backup opcional antes de sair ----
  function logoutBackupTimestamp(){
    const d=new Date(), p=n=>String(n).padStart(2,'0');
    return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}_${p(d.getHours())}-${p(d.getMinutes())}-${p(d.getSeconds())}`;
  }
  async function buildCurrentUserBackup(){
    const u=state.user||{}, role=u.role||'usuario';
    const base={plataforma:'Contabilidade Avançada',geradoEm:new Date().toISOString(),usuario:{nome:u.name||'',email:u.email||'',perfil:role,matricula:u.matricula||''}};
    if(role==='professor'){
      try{ await loadPlanningAll(); }catch(e){}
      const names=new Set(); (state.turmas||[]).forEach(t=>(t.students||[]).forEach(a=>names.add((a.nome||'').trim())));
      const alunos=(state.roster||[]).filter(r=>names.has((r.name||'').trim()));
      return {...base,turmas:state.turmas||[],alunos,planejamentos:state.planningRecords||{semester:[],lesson:[]},cadastrosPlanejamento:state.planningCatalog||null};
    }
    if(role==='aluno'){
      return {...base,turma:state.studentTurma||null,progresso:state.progress||null};
    }
    return base;
  }
  async function downloadCurrentUserBackup(){
    const payload=await buildCurrentUserBackup();
    const role=((state.user&&state.user.role)||'usuario').replace(/[^a-z0-9_-]/gi,'_').toLowerCase();
    const name=`backup_contabilidade_avancada_${role}_${logoutBackupTimestamp()}.json`;
    downloadText(name,JSON.stringify(payload,null,2),'application/json;charset=utf-8');
    try{ await logAudit('backup_saida',`${state.user ? state.user.name : 'Usuário'} gerou backup antes de sair.`); }catch(e){}
  }
  function closeLogoutBackupModal(){ const el=document.getElementById('logout-backup-overlay'); if(el)el.remove(); }
  async function finishLogout(){
    try{ await logAudit('logout',`${state.user ? state.user.name : 'Usuário'} saiu da plataforma.`); }catch(e){}
    await signOut(auth);
  }
  function requestLogoutWithBackup(){
    if(document.getElementById('logout-backup-overlay')) return;
    const overlay=document.createElement('div'); overlay.id='logout-backup-overlay'; overlay.className='logout-backup-overlay';
    overlay.innerHTML=`<div class="logout-backup-modal" role="dialog" aria-modal="true" aria-labelledby="logout-backup-title">
      <div class="logout-backup-icon">💾</div>
      <h2 id="logout-backup-title" class="serif">Fazer um backup antes de sair?</h2>
      <p>Baixe um arquivo com os seus dados desta plataforma, com a data e a hora no nome do arquivo.<br><b>Recomendado, mas opcional.</b></p>
      <button class="logout-backup-primary" id="btn-backup-and-logout">Sim, baixar backup e sair</button>
      <button class="logout-backup-secondary" id="btn-logout-without-backup">Sair sem backup</button>
      <button class="logout-backup-cancel" id="btn-cancel-logout" aria-label="Cancelar saída">Cancelar</button>
    </div>`;
    document.body.appendChild(overlay);
    const yes=document.getElementById('btn-backup-and-logout'), no=document.getElementById('btn-logout-without-backup'), cancel=document.getElementById('btn-cancel-logout');
    if(cancel) cancel.addEventListener('click',closeLogoutBackupModal);
    overlay.addEventListener('click',e=>{ if(e.target===overlay) closeLogoutBackupModal(); });
    if(no) no.addEventListener('click',async()=>{ yes.disabled=true; no.disabled=true; closeLogoutBackupModal(); await finishLogout(); });
    if(yes) yes.addEventListener('click',async()=>{ yes.disabled=true; no.disabled=true; yes.textContent='Gerando backup...'; try{ await downloadCurrentUserBackup(); closeLogoutBackupModal(); await finishLogout(); }catch(e){ console.error('Erro ao gerar backup de saída',e); yes.disabled=false; no.disabled=false; yes.textContent='Sim, baixar backup e sair'; alert('Não foi possível gerar o backup. Você pode tentar novamente ou sair sem backup.'); } });
  }

'''
s=s.replace(anchor,block+anchor,1)

# Fluxo principal de logout: não limpar estado antes do backup
pattern=r"    const logout = document\.getElementById\('btn-logout'\);\n    if \(logout\) logout\.addEventListener\('click', async \(\) => \{.*?\n    \}\);\n\n    document\.querySelectorAll\('\.module-row'\)"
repl="    const logout = document.getElementById('btn-logout');\n    if (logout) logout.addEventListener('click', () => requestLogoutWithBackup());\n\n    document.querySelectorAll('.module-row')"
s,n=re.subn(pattern,repl,s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'main logout replace failed: {n}')

# Professor aguardando aprovação também usa o mesmo fluxo opcional
old="""    const b=document.getElementById('btn-pending-logout');\n    if (b) b.addEventListener('click', async()=>{ await signOut(auth); });"""
new="""    const b=document.getElementById('btn-pending-logout');\n    if (b) b.addEventListener('click', ()=>requestLogoutWithBackup());"""
if old not in s: raise SystemExit('pending logout anchor not found')
s=s.replace(old,new,1)

app.write_text(s,encoding='utf-8')

idx=Path('public/index.html')
h=idx.read_text(encoding='utf-8')
css=r'''
  /* Backup opcional ao sair */
  #cont-avancada .logout-backup-overlay, .logout-backup-overlay {
    position:fixed; inset:0; z-index:99999; display:flex; align-items:center; justify-content:center;
    padding:16px; background:rgba(15,26,36,.62); backdrop-filter:blur(2px);
  }
  #cont-avancada .logout-backup-modal, .logout-backup-modal {
    width:min(474px,calc(100vw - 32px)); background:#fff; border-radius:18px; padding:38px 34px 30px;
    box-shadow:0 18px 60px rgba(0,0,0,.28); text-align:center; color:#17314d;
  }
  #cont-avancada .logout-backup-icon, .logout-backup-icon { font-size:38px; line-height:1; margin-bottom:16px; }
  #cont-avancada .logout-backup-modal h2, .logout-backup-modal h2 { margin:0 0 10px; font-size:28px; line-height:1.08; }
  #cont-avancada .logout-backup-modal p, .logout-backup-modal p { margin:0 auto 22px; max-width:390px; color:#617083; font-size:15px; line-height:1.7; }
  #cont-avancada .logout-backup-modal button, .logout-backup-modal button { width:100%; min-height:42px; border-radius:6px; font-weight:600; font-size:14px; cursor:pointer; }
  #cont-avancada .logout-backup-primary, .logout-backup-primary { border:0; background:#bf7025; color:#fff; margin-bottom:9px; }
  #cont-avancada .logout-backup-secondary, .logout-backup-secondary { border:1px solid #d0d8e1; background:#fff; color:#17314d; margin-bottom:10px; }
  #cont-avancada .logout-backup-cancel, .logout-backup-cancel { border:0!important; background:transparent!important; color:#617083!important; min-height:30px!important; font-weight:500!important; }
  #cont-avancada .logout-backup-modal button:disabled, .logout-backup-modal button:disabled { opacity:.55; cursor:wait; }
  @media (max-width:520px){
    #cont-avancada .logout-backup-modal, .logout-backup-modal { padding:28px 20px 22px; border-radius:14px; }
    #cont-avancada .logout-backup-modal h2, .logout-backup-modal h2 { font-size:23px; }
    #cont-avancada .logout-backup-modal p, .logout-backup-modal p { font-size:14px; line-height:1.55; }
  }
'''
if '</style>' not in h: raise SystemExit('style closing not found')
h=h.replace('</style>',css+'\n</style>',1)
idx.write_text(h,encoding='utf-8')

readme=Path('README.md')
r=readme.read_text(encoding='utf-8')
section='''\n\n## Backup ao sair\n\nAo acionar **Sair**, qualquer usuário autenticado recebe uma confirmação opcional para baixar um backup JSON antes do logout. O arquivo inclui somente os dados pertinentes ao próprio perfil e recebe data e hora no nome. O usuário também pode escolher **Sair sem backup**.\n'''
if '## Backup ao sair' not in r: r+=section
readme.write_text(r,encoding='utf-8')

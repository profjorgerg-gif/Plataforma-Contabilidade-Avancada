from pathlib import Path
import re
p=Path('public/app.js')
s=p.read_text(encoding='utf-8')
# imports
s=s.replace("  getFirestore, doc, getDoc, setDoc, updateDoc, collection, getDocs, query,\n  where, documentId\n", "  getFirestore, doc, getDoc, setDoc, updateDoc, collection, getDocs, query,\n  where, documentId, orderBy, limit\n")
# state filters
s=s.replace("    accessAuditOnly: false,\n", "    accessAuditOnly: false,\n    auditUserFilter: '',\n    auditRoleFilter: '',\n    auditTurmaFilter: '',\n    auditTypeFilter: '',\n    auditStartDate: '',\n    auditEndDate: '',\n")
# replace audit functions
start=s.index("  // ---- Auditoria (professor) ----")
end=s.index("  // ---- Planejamento docente (professor) ----", start)
new=r'''  // ---- Auditoria pedagógica e log formal de acessos ----
  function roleLabelFor(role){
    return role === 'professor' ? 'professor' : (role === 'admin' ? 'usuário mestre' : (role === 'pending_professor' ? 'professor pendente' : 'aluno'));
  }
  async function resolveProfessorUidByName(name){
    if(!name) return '';
    try{
      const snap=await getDocs(query(collection(db,'users'),where('name','==',name)));
      let uid=''; snap.forEach(d=>{ if(!uid && ['professor','admin'].includes(d.data().role)) uid=d.id; });
      return uid;
    }catch(e){ return ''; }
  }
  async function auditContext(){
    const u=state.user||{};
    if(u.role==='professor') return {professorUid:u.uid||'',turmaId:'',turmaName:''};
    if(u.role==='aluno'){
      const t=state.studentTurma||{};
      const professorUid=u.professorUid||await resolveProfessorUidByName(t.professor||'');
      if(professorUid && state.user) state.user.professorUid=professorUid;
      return {professorUid,turmaId:t.id||u.turmaId||'',turmaName:t.name||u.turmaName||''};
    }
    return {professorUid:'',turmaId:'',turmaName:''};
  }
  async function logAudit(type, detail, extra={}){
    const u=state.user||{}; if(!u.uid) return;
    try{
      const ctx=await auditContext(), ts=Date.now();
      const entry={
        type, detail, actor:u.name||'Sistema', actorUid:u.uid, role:u.role||'', email:u.email||'', ts,
        professorUid:extra.professorUid!==undefined?extra.professorUid:ctx.professorUid,
        turmaId:extra.turmaId!==undefined?extra.turmaId:ctx.turmaId,
        turmaName:extra.turmaName!==undefined?extra.turmaName:ctx.turmaName,
        moduleId:extra.moduleId||'', source:'web'
      };
      await setDoc(doc(db,'audit_logs',`${ts}_${u.uid}_${Math.random().toString(36).slice(2,8)}`),entry);
    }catch(e){ console.error('audit log error',e); }
  }
  async function loadAuditoria(){
    try{
      if(!state.user || !['professor','admin'].includes(state.user.role)){ state.auditLog=[]; return; }
      let qref;
      if(state.user.role==='admin') qref=query(collection(db,'audit_logs'),orderBy('ts','desc'),limit(1000));
      else qref=query(collection(db,'audit_logs'),where('professorUid','==',state.user.uid),limit(1000));
      const snap=await getDocs(qref), out=[]; snap.forEach(d=>out.push({id:d.id,...d.data()}));
      out.sort((a,b)=>(b.ts||0)-(a.ts||0)); state.auditLog=out;
    }catch(e){ console.error('audit load error',e); state.auditLog=[]; }
  }

'''
s=s[:start]+new+s[end:]
# render admin audit route + nav
s=s.replace("    else if (state.view === 'usuarios') inner += renderUsuarios();\n", "    else if (state.view === 'usuarios') inner += renderUsuarios();\n    else if (state.view === 'auditoria') inner += renderAuditoria();\n")
s=s.replace("    else items = [['suporte','Suporte'],['usuarios','Usuários']];", "    else items = [['suporte','Suporte'],['usuarios','Usuários'],['auditoria','Auditoria']];")
# replace renderAuditoria
rs=s.index("  function renderAuditoria(){")
re=s.index("  function renderCorrecoesPendentes(){",rs)
render=r'''  function renderAuditoria(){
    const all=state.auditLog||[];
    const users=[...new Set(all.map(e=>e.actor).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
    const turmas=[...new Set(all.map(e=>e.turmaName).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
    const types=[...new Set(all.map(e=>e.type).filter(Boolean))].sort();
    const start=state.auditStartDate?new Date(state.auditStartDate+'T00:00:00').getTime():null;
    const end=state.auditEndDate?new Date(state.auditEndDate+'T23:59:59').getTime():null;
    const log=all.filter(e=>(!state.accessAuditOnly||['login','logout'].includes(e.type))&&(!state.auditUserFilter||e.actor===state.auditUserFilter)&&(!state.auditRoleFilter||e.role===state.auditRoleFilter)&&(!state.auditTurmaFilter||e.turmaName===state.auditTurmaFilter)&&(!state.auditTypeFilter||e.type===state.auditTypeFilter)&&(!start||Number(e.ts)>=start)&&(!end||Number(e.ts)<=end));
    let html=`<div class="section-title">Auditoria Pedagógica e Log de Acessos</div>`;
    html+=`<div class="note">${state.user.role==='admin'?'Visão administrativa: movimentações de todos os alunos e professores.':'Visão do professor: movimentações dos alunos vinculados às suas turmas e suas próprias ações.'} Os registros são cronológicos e somente para consulta.</div>`;
    html+=`<div class="toolbar"><button class="btn-outline ${!state.accessAuditOnly?'active':''}" id="audit-all">Todos os eventos</button><button class="btn-outline ${state.accessAuditOnly?'active':''}" id="audit-access">Somente login/logout</button><button class="btn-outline" id="audit-clear-filters">Limpar filtros</button><button class="btn-brass" id="audit-export-csv">Exportar CSV</button></div>`;
    html+=`<div class="planning-grid"><div class="planning-field"><label>Usuário</label><select id="audit-user-filter"><option value="">Todos</option>${users.map(v=>`<option ${state.auditUserFilter===v?'selected':''}>${esc(v)}</option>`).join('')}</select></div><div class="planning-field"><label>Perfil</label><select id="audit-role-filter"><option value="">Todos</option>${[['aluno','Aluno'],['professor','Professor'],['admin','Usuário Mestre']].map(([v,l])=>`<option value="${v}" ${state.auditRoleFilter===v?'selected':''}>${l}</option>`).join('')}</select></div><div class="planning-field"><label>Turma</label><select id="audit-turma-filter"><option value="">Todas</option>${turmas.map(v=>`<option ${state.auditTurmaFilter===v?'selected':''}>${esc(v)}</option>`).join('')}</select></div><div class="planning-field"><label>Evento</label><select id="audit-type-filter"><option value="">Todos</option>${types.map(v=>`<option ${state.auditTypeFilter===v?'selected':''}>${esc(v)}</option>`).join('')}</select></div><div class="planning-field"><label>Data inicial</label><input id="audit-start-date" type="date" value="${esc(state.auditStartDate)}"></div><div class="planning-field"><label>Data final</label><input id="audit-end-date" type="date" value="${esc(state.auditEndDate)}"></div></div>`;
    html+=`<div class="thread-preview" style="margin:12px 0">${log.length} evento(s) exibido(s).</div>`;
    if(!log.length) return html+`<div class="empty-state">Nenhum evento encontrado para os filtros selecionados.</div>`;
    html+=`<div class="table-scroll"><table class="roster"><tr><th>Data/Hora</th><th>Usuário</th><th>Perfil</th><th>Turma</th><th>Evento</th><th>Descrição</th></tr>`;
    log.forEach(e=>{html+=`<tr><td style="white-space:nowrap">${esc(e.ts?new Date(e.ts).toLocaleString('pt-BR'):'—')}</td><td><b>${esc(e.actor||'Sistema')}</b>${e.email?`<div class="cell-status">${esc(e.email)}</div>`:''}</td><td>${esc(roleLabelFor(e.role||''))}</td><td>${esc(e.turmaName||'—')}</td><td>${esc(e.type||'—')}</td><td>${esc(e.detail||'')}</td></tr>`;});
    return html+`</table></div>`;
  }

'''
s=s[:rs]+render+s[re:]
# nav handler admin audit
s=s.replace("        if (key === 'usuarios'){ state.view = 'usuarios'; await loadUsuarios(); render(); return; }", "        if (key === 'usuarios'){ state.view = 'usuarios'; await loadUsuarios(); render(); return; }\n        if (key === 'auditoria'){ state.view='auditoria'; await loadAuditoria(); render(); return; }")
# audit handlers replace existing simple handler insertion point before Turmas
needle="    // ---- Turmas: list / creation ----"
handlers=r'''    const auditAll=document.getElementById('audit-all'); if(auditAll)auditAll.addEventListener('click',()=>{state.accessAuditOnly=false;render();});
    const auditAccess=document.getElementById('audit-access'); if(auditAccess)auditAccess.addEventListener('click',()=>{state.accessAuditOnly=true;render();});
    [['audit-user-filter','auditUserFilter'],['audit-role-filter','auditRoleFilter'],['audit-turma-filter','auditTurmaFilter'],['audit-type-filter','auditTypeFilter'],['audit-start-date','auditStartDate'],['audit-end-date','auditEndDate']].forEach(([id,key])=>{const el=document.getElementById(id);if(el)el.addEventListener('change',()=>{state[key]=el.value;render();});});
    const auditClear=document.getElementById('audit-clear-filters');if(auditClear)auditClear.addEventListener('click',()=>{state.accessAuditOnly=false;state.auditUserFilter='';state.auditRoleFilter='';state.auditTurmaFilter='';state.auditTypeFilter='';state.auditStartDate='';state.auditEndDate='';render();});
    const auditCsv=document.getElementById('audit-export-csv');if(auditCsv)auditCsv.addEventListener('click',()=>{const rows=[['Data/Hora','Usuário','E-mail','Perfil','Turma','Evento','Descrição']];(state.auditLog||[]).forEach(e=>rows.push([e.ts?new Date(e.ts).toLocaleString('pt-BR'):'',e.actor||'',e.email||'',roleLabelFor(e.role||''),e.turmaName||'',e.type||'',e.detail||'']));const csv=rows.map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(';')).join('\n');downloadText('auditoria_contabilidade_avancada.csv',csv,'text/csv;charset=utf-8');});

'''
s=s.replace(needle,handlers+needle)
# add logout helper before render
insert="  // ---- Render ----\n"
logout=r'''  async function performLogout(){
    try{ await logAudit('logout',`${state.user&&state.user.name?state.user.name:'Usuário'} encerrou a sessão na plataforma.`); }catch(e){}
    await signOut(auth);
  }
  function requestLogoutWithBackup(){
    if(confirm('Deseja fazer um backup antes de sair?\n\nOK = sair (o backup continua disponível no menu Backup)\nCancelar = permanecer conectado')) performLogout();
  }

'''
s=s.replace(insert,logout+insert)
# enrich student user with turma
s=s.replace("state.user = { name: academicName, email: profile.email || fbUser.email || '', role: 'aluno', uid: fbUser.uid, matricula: informedMatricula };", "state.user = { name: academicName, email: profile.email || fbUser.email || '', role: 'aluno', uid: fbUser.uid, matricula: informedMatricula, turmaId: enrollment.turma.id, turmaName: enrollment.turma.name };")
# write
p.write_text(s,encoding='utf-8')

# rules
rp=Path('firestore.rules'); r=rp.read_text(encoding='utf-8')
marker="    // Armazenamento pedagógico da plataforma. Contas pending_professor ficam\n"
audit_rules=r'''    // Auditoria formal: cada usuário grava apenas eventos em seu próprio nome.
    // Professor lê somente os eventos vinculados a ele; Usuário Mestre lê todos.
    match /audit_logs/{logId} {
      allow create: if isActiveUser() && request.resource.data.actorUid == request.auth.uid;
      allow read: if isActiveUser() && (
        myRole() == 'admin' ||
        (myRole() == 'professor' && resource.data.professorUid == request.auth.uid) ||
        resource.data.actorUid == request.auth.uid
      );
      allow update, delete: if false;
    }

'''
r=r.replace(marker,audit_rules+marker)
rp.write_text(r,encoding='utf-8')

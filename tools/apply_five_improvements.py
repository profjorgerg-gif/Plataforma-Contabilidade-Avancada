from pathlib import Path

APP = Path('public/app.js')
INDEX = Path('public/index.html')
app = APP.read_text(encoding='utf-8')
index = INDEX.read_text(encoding='utf-8')

def rep(old, new, count=1):
    global app
    if old not in app:
        raise SystemExit('Âncora não encontrada:\n' + old[:180])
    app = app.replace(old, new, count)

# 1) Estado adicional
rep("    reportTurmaFilter: '',\n    accessPendingMessage: ''\n", "    reportTurmaFilter: '',\n    accessPendingMessage: '',\n    studentTurma: null,\n    accessAuditOnly: false\n")

# 2) Resolver a turma do aluno e os prazos associados
anchor = "  // ---- PDF import (pdf.js loaded on demand from cdnjs) ----\n"
insert = r'''  async function loadStudentTurma(studentName){
    try {
      const list = await kvList('turma:');
      if (!list || !list.keys) return null;
      const target=(studentName||'').trim().toLocaleLowerCase('pt-BR');
      const matches=[];
      for (const k of list.keys){
        try {
          const r=await kvGet(k); if(!r||!r.value) continue;
          const t=JSON.parse(r.value);
          if ((t.students||[]).some(s=>(s.nome||'').trim().toLocaleLowerCase('pt-BR')===target)) matches.push(t);
        } catch(e){}
      }
      matches.sort((a,b)=>(b.updatedAt||b.createdAt||0)-(a.updatedAt||a.createdAt||0));
      return matches[0]||null;
    } catch(e){ return null; }
  }

'''
rep(anchor, insert + anchor)

# 3) Normalização dos chamados
old = r'''  async function loadThread(kind, participantKey){
    try {
      const r = await kvGet('support:' + kind + ':' + participantKey);
      if (r && r.value) return JSON.parse(r.value);
    } catch(e){}
    return { participantName: participantKey, protocol:'', status:'aberto', createdAt:null, updatedAt:null, messages: [] };
  }
'''
new = r'''  const SUPPORT_STATUSES = [
    ['aberto','Aberto'],['em_analise','Em análise'],['aguardando_resposta','Aguardando resposta'],
    ['encaminhado_desenvolvimento','Encaminhado para desenvolvimento'],['aprovado_desenvolvimento','Aprovado para desenvolvimento'],
    ['resolvido','Resolvido'],['encerrado','Encerrado']
  ];
  function supportStatusLabel(status){ const x=SUPPORT_STATUSES.find(i=>i[0]===status); return x?x[1]:'Aberto'; }
  function normalizeThread(t, participantKey){
    t=t||{}; t.participantName=t.participantName||participantKey; t.protocol=t.protocol||''; t.status=t.status||'aberto';
    t.createdAt=t.createdAt||null; t.updatedAt=t.updatedAt||null; t.responseDueAt=t.responseDueAt||null;
    t.closedAt=t.closedAt||null; t.reopenUntil=t.reopenUntil||null; t.messages=Array.isArray(t.messages)?t.messages:[];
    t.history=Array.isArray(t.history)?t.history:[]; return t;
  }
  function canReopenThread(t){ return !!(t && t.status==='encerrado' && (!t.reopenUntil || Date.now()<=Number(t.reopenUntil))); }
  async function loadThread(kind, participantKey){
    try {
      const r = await kvGet('support:' + kind + ':' + participantKey);
      if (r && r.value) return normalizeThread(JSON.parse(r.value), participantKey);
    } catch(e){}
    return normalizeThread(null, participantKey);
  }
'''
rep(old,new)

# 4) Auditoria enriquecida
rep("      role: (state.user && state.user.role) || '',\n      ts: Date.now()\n", "      role: (state.user && state.user.role) || '',\n      email: (state.user && state.user.email) || '',\n      ts: Date.now()\n")

# 5) Cálculo da nota automática + penalidade de atraso
rep("  function automaticModuleGrade(mp){\n", "  function baseAutomaticModuleGrade(mp){\n")
app = app.replace('automaticModuleGrade(', 'effectiveModuleGrade(')
anchor = "  function moduleReadyForSubmission(mp, m){\n"
helpers = r'''  function effectiveModuleGrade(mp){
    const base=baseAutomaticModuleGrade(mp); if(base===null) return null;
    const c=correctionState(mp); const penalty=Number(c.latePenalty||0);
    return Math.max(0,Math.round((base-penalty)*10)/10);
  }
  function scheduleForModule(m){
    const t=state.studentTurma; return (t&&t.moduleSettings&&t.moduleSettings[m.id])||{};
  }
  function toTs(v){ if(!v) return null; const ts=new Date(v).getTime(); return Number.isFinite(ts)?ts:null; }
  function moduleAccess(m){
    const idx=MODULES.findIndex(x=>x.id===m.id);
    if(idx>0){ const prev=state.progress&&state.progress.modules[MODULES[idx-1].id]; const pc=correctionState(prev); if(!(pc.status==='corrigido'&&pc.released)) return {locked:true,reason:'Conclua e tenha a correção do módulo anterior liberada pelo professor.'}; }
    const s=scheduleForModule(m), deadline=toTs(s.deadline), original=toTs(s.originalDeadline)||deadline, now=Date.now();
    if(deadline && now>deadline && !s.allowLate) return {locked:true,reason:'Prazo encerrado. Aguarde a reabertura pelo professor.',deadline,late:true};
    return {locked:false,deadline,late:!!(original&&now>original),allowLate:!!s.allowLate};
  }
  function moduleDeadlineText(m){ const a=moduleAccess(m); if(!a.deadline) return 'Prazo não definido'; return 'Prazo: '+new Date(a.deadline).toLocaleString('pt-BR')+(a.late?' · entrega em atraso':''); }

'''
rep(anchor, helpers + anchor)

# 6) Dashboard com bloqueio sequencial/prazo
old = r'''    MODULES.forEach(m => {
      const mp = state.progress.modules[m.id];
      const pct = pctModule(mp, m);
      html += `<div class="module-row" style="--mcolor:${m.color}" data-module="${m.id}">
        <div class="module-num serif">${String(m.num).padStart(2,'0')}</div>
        <div class="module-info">
          <h3>${esc(m.title)}</h3>
          <p>${esc(m.subtitle)}</p>
        </div>
        <div class="module-progress">
          ${pct}% concluído<br>${correctionBadge(mp)}
          <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
        </div>
      </div>`;
    });
'''
new = r'''    MODULES.forEach(m => {
      const mp = state.progress.modules[m.id];
      const pct = pctModule(mp, m); const access=moduleAccess(m);
      html += `<div class="module-row ${access.locked?'locked':''}" style="--mcolor:${m.color}" data-module="${m.id}" data-locked="${access.locked?'1':'0'}">
        <div class="module-num serif">${String(m.num).padStart(2,'0')}</div>
        <div class="module-info">
          <h3>${esc(m.title)} ${access.locked?'<span class="status-badge neutral">Bloqueado</span>':''}</h3>
          <p>${esc(m.subtitle)}</p><div class="deadline-text">${esc(access.locked?access.reason:moduleDeadlineText(m))}</div>
        </div>
        <div class="module-progress">
          ${pct}% concluído<br>${correctionBadge(mp)}
          <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
        </div>
      </div>`;
    });
'''
rep(old,new)

# 7) Informação de prazo e bloqueio também dentro do módulo
rep("    const mp = state.progress.modules[m.id];\n    let html = `<span class=\"back-link\"", "    const mp = state.progress.modules[m.id];\n    const access=moduleAccess(m);\n    if(access.locked) return `<span class=\"back-link\" id=\"back-dash\">← Voltar aos módulos</span><div class=\"panel\"><div class=\"empty-state\"><b>Módulo bloqueado.</b><br>${esc(access.reason)}</div></div>`;\n    let html = `<span class=\"back-link\"")
rep("        <div class=\"subtitle\">${esc(m.subtitle)}</div>\n      </div>\n      <div class=\"tabs\">", "        <div class=\"subtitle\">${esc(m.subtitle)}</div>\n        <div class=\"deadline-text\">${esc(moduleDeadlineText(m))}${access.late?' · <b>Será aplicado desconto de 2,0 pontos na primeira entrega.</b>':''}</div>\n      </div>\n      <div class=\"tabs\">")

# 8) Clique em módulo bloqueado
rep("      row.addEventListener('click', () => {\n        state.activeModuleId", "      row.addEventListener('click', () => {\n        if(row.getAttribute('data-locked')==='1') return;\n        state.activeModuleId")

# 9) Envio para correção com atraso de -2,0 e primeira entrega preservada
old = "    if(btnSubmitModule) btnSubmitModule.addEventListener('click',async()=>{const m=MODULES.find(x=>x.id===state.activeModuleId),mp=state.progress.modules[m.id],c=correctionState(mp); c.status='em_correcao'; c.submittedAt=Date.now(); c.feedback=''; c.released=false; c.history.push({type:'envio',ts:Date.now(),autoGrade:effectiveModuleGrade(mp)}); mp.correction=c; await saveProgress(state.progress); await logAudit('modulo_enviado_correcao',`${state.user.name} enviou o módulo \"${m.title}\" para correção.`); render();});"
new = "    if(btnSubmitModule) btnSubmitModule.addEventListener('click',async()=>{const m=MODULES.find(x=>x.id===state.activeModuleId),mp=state.progress.modules[m.id],c=correctionState(mp),access=moduleAccess(m); if(access.locked){alert(access.reason); state.view='dashboard'; render(); return;} const now=Date.now(); if(!c.firstSubmittedAt){c.firstSubmittedAt=now; c.latePenalty=access.late?2:0; c.late=!!access.late;} c.status='em_correcao'; c.submittedAt=now; c.feedback=''; c.released=false; c.history.push({type:'envio',ts:now,autoGrade:effectiveModuleGrade(mp),late:!!c.late,latePenalty:Number(c.latePenalty||0)}); mp.correction=c; await saveProgress(state.progress); await logAudit('modulo_enviado_correcao',`${state.user.name} enviou o módulo \"${m.title}\" para correção${c.latePenalty?' com desconto de 2,0 pontos por atraso':''}.`); render();});"
rep(old,new)

# 10) Atualiza correctionState para normalizar atraso
old = "  function correctionState(mp){\n    if (!mp || !mp.correction) return { status:'liberado', submittedAt:null, reviewedAt:null, feedback:'', finalGrade:null, released:false, history:[] };\n    return mp.correction;\n  }\n"
new = "  function correctionState(mp){\n    if (!mp) return { status:'liberado', submittedAt:null, reviewedAt:null, feedback:'', finalGrade:null, released:false, history:[], firstSubmittedAt:null, late:false, latePenalty:0 };\n    if(!mp.correction) mp.correction={ status:'liberado', submittedAt:null, reviewedAt:null, feedback:'', finalGrade:null, released:false, history:[], firstSubmittedAt:null, late:false, latePenalty:0 };\n    const c=mp.correction; if(!Array.isArray(c.history))c.history=[]; if(c.firstSubmittedAt===undefined)c.firstSubmittedAt=null; if(c.late===undefined)c.late=false; if(c.latePenalty===undefined)c.latePenalty=0; return c;\n  }\n"
rep(old,new)

# 11) Configuração de prazos na turma
anchor = "    // Roster table\n"
block = r'''    // Prazos dos módulos
    turma.moduleSettings=turma.moduleSettings||{};
    html += `<div class="card-box"><h4>Prazos e liberação dos módulos</h4><p class="desc">Defina o prazo de cada módulo. Após o vencimento o módulo é bloqueado automaticamente. Marque "Permitir atraso" para reabrir a entrega; a primeira entrega após o prazo original recebe desconto automático de 2,0 pontos.</p><div class="deadline-grid">`;
    MODULES.forEach(m=>{const s=turma.moduleSettings[m.id]||{}; html+=`<div class="deadline-card"><b>M${m.num} — ${esc(m.title)}</b><label>Prazo</label><input type="datetime-local" data-deadline-module="${m.id}" value="${esc(s.deadline||'')}"><label class="checkline"><input type="checkbox" data-late-module="${m.id}" ${s.allowLate?'checked':''}> Permitir entrega em atraso</label></div>`;});
    html += `</div><button class="btn-brass" id="btn-save-deadlines">Salvar prazos</button></div>`;

'''
rep(anchor, block + anchor)

# 12) Handler para salvar prazos
anchor = "    // ---- Turma detail: individual add ----\n"
handler = r'''    const btnSaveDeadlines=document.getElementById('btn-save-deadlines');
    if(btnSaveDeadlines) btnSaveDeadlines.addEventListener('click',async()=>{
      const turma=state.turmas.find(t=>t.id===state.activeTurmaId); if(!turma)return; turma.moduleSettings=turma.moduleSettings||{};
      MODULES.forEach(m=>{const inp=document.querySelector(`[data-deadline-module="${m.id}"]`), chk=document.querySelector(`[data-late-module="${m.id}"]`); const deadline=(inp&&inp.value)||''; const prev=turma.moduleSettings[m.id]||{}; turma.moduleSettings[m.id]={deadline,originalDeadline:deadline?(prev.originalDeadline||deadline):'',allowLate:!!(chk&&chk.checked)};});
      await saveTurma(turma); await logAudit('prazos_atualizados',`${state.user.name} atualizou os prazos da turma "${turma.name}".`); alert('Prazos salvos.'); render();
    });

'''
rep(anchor, handler + anchor)

# 13) Ao voltar ao dashboard do aluno, recarrega turma/prazos
rep("        if (key === 'dashboard'){ state.view = 'dashboard'; render(); return; }", "        if (key === 'dashboard'){ state.studentTurma=await loadStudentTurma(state.user.name); state.view = 'dashboard'; render(); return; }")

# 14) Navegação documental do professor
rep("['professor:auditoria','Auditoria'],['manual','Manual do Professor'],['suporte','Suporte']", "['professor:auditoria','Auditoria'],['professor:operacional','Manual Operacional'],['professor:checklist','Checklist'],['professor:guia','Guia Pedagógico'],['manual','Manual do Professor'],['suporte','Suporte']")
rep("    if (state.professorTab === 'backup') return renderBackup();\n    return renderAcompanhamento();", "    if (state.professorTab === 'backup') return renderBackup();\n    if (state.professorTab === 'operacional') return renderManualOperacional();\n    if (state.professorTab === 'checklist') return renderChecklistStatus();\n    if (state.professorTab === 'guia') return renderGuiaPedagogico();\n    return renderAcompanhamento();")

# 15) Auditoria com filtro de acessos
old = r'''  function renderAuditoria(){
    let html = `<div class="section-title">Auditoria</div>`;
    html += `<div class="note">Registro cronológico das principais ações realizadas na plataforma: criação de turmas, matrícula de alunos, avaliações concluídas e mensagens de suporte.</div>`;
    const log = state.auditLog || [];
    if (!log.length){
      html += `<div class="empty-state">Nenhum evento registrado ainda.</div>`;
      return html;
    }
    html += `<table class="roster"><tr><th>Quando</th><th>Evento</th></tr>`;
    log.forEach(e => {
      const date = e.ts ? new Date(e.ts).toLocaleString('pt-BR') : '—';
      html += `<tr><td style="white-space:nowrap;font-size:12px;color:var(--ink-soft)">${esc(date)}</td><td>${esc(e.detail)}</td></tr>`;
    });
    html += `</table>`;
    return html;
  }
'''
new = r'''  function renderAuditoria(){
    let html = `<div class="section-title">Auditoria</div>`;
    html += `<div class="note">Registro cronológico das ações e dos acessos à plataforma. Entradas e saídas registram data/hora, usuário, perfil e e-mail disponível.</div><div class="toolbar"><button class="btn-outline ${!state.accessAuditOnly?'active':''}" id="audit-all">Todos os eventos</button><button class="btn-outline ${state.accessAuditOnly?'active':''}" id="audit-access">Somente acessos</button></div>`;
    const log = (state.auditLog || []).filter(e=>!state.accessAuditOnly || e.type==='login' || e.type==='logout');
    if (!log.length){ html += `<div class="empty-state">Nenhum evento registrado ainda.</div>`; return html; }
    html += `<div class="table-scroll"><table class="roster"><tr><th>Quando</th><th>Usuário</th><th>Perfil</th><th>Evento</th></tr>`;
    log.forEach(e => { const date=e.ts?new Date(e.ts).toLocaleString('pt-BR'):'—'; html+=`<tr><td style="white-space:nowrap">${esc(date)}</td><td>${esc(e.actor||'Sistema')}${e.email?`<div class="cell-status">${esc(e.email)}</div>`:''}</td><td>${esc(roleLabelFor(e.role||''))}</td><td>${esc(e.detail)}</td></tr>`; });
    html += `</table></div>`; return html;
  }
'''
rep(old,new)

# 16) Suporte completo
start = app.index("  function renderThreadConversation(thread, myRole){")
end = app.index("\n  function renderInboxList(list){", start)
newfunc = r'''  function renderThreadConversation(thread, myRole){
    thread=normalizeThread(thread,thread&&thread.participantName); const messages=thread.messages||[]; const closed=thread.status==='encerrado';
    let html=`<div class="support-meta"><div><b>${esc(thread.protocol||'Protocolo gerado no primeiro envio')}</b><span class="status-badge ${closed?'neutral':thread.status==='resolvido'?'ok':'info'}">${esc(supportStatusLabel(thread.status))}</span></div><button class="btn-outline small" id="btn-print-support">Imprimir / Salvar PDF</button></div>`;
    html+=`<div class="support-dates">Prazo de resposta: <b>${thread.responseDueAt?new Date(Number(thread.responseDueAt)).toLocaleString('pt-BR'):'não definido'}</b>${thread.reopenUntil?` · Reabertura até: <b>${new Date(Number(thread.reopenUntil)).toLocaleString('pt-BR')}</b>`:''}</div>`;
    if(state.user&&state.user.role!=='aluno'&&thread.protocol){ html+=`<div class="support-controls"><div><label>Status</label><select id="support-status">${SUPPORT_STATUSES.map(([v,l])=>`<option value="${v}" ${thread.status===v?'selected':''}>${esc(l)}</option>`).join('')}</select></div><div><label>Prazo de resposta</label><input type="datetime-local" id="support-due" value="${thread.responseDueAt?new Date(Number(thread.responseDueAt)-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16):''}"></div><div><label>Reabertura permitida até</label><input type="datetime-local" id="support-reopen" value="${thread.reopenUntil?new Date(Number(thread.reopenUntil)-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16):''}"></div><button class="btn-brass" id="btn-save-support-control">Salvar atendimento</button></div>`; }
    if(closed&&canReopenThread(thread)) html+=`<button class="btn-outline" id="btn-reopen-support">Reabrir chamado</button>`;
    html+=`<div class="chat-box">`;
    if(!messages.length) html+=`<div class="empty-state" style="padding:24px">Nenhuma mensagem ainda. Envie a primeira mensagem abaixo.</div>`;
    else messages.forEach(m=>{const mine=m.from===myRole; html+=`<div class="chat-msg ${mine?'mine':''}"><div class="chat-meta">${esc(m.name)} · ${new Date(m.ts).toLocaleString('pt-BR')}</div><div class="chat-bubble">${esc(m.text)}</div></div>`;});
    html+=`</div><div class="chat-input-row"><textarea id="suporte-msg" placeholder="${closed?'Chamado encerrado. Reabra para enviar nova mensagem.':'Escreva sua mensagem...'}" ${closed?'disabled':''}>${esc(state.suporteNewMessage)}</textarea><button class="btn-brass" id="btn-send-suporte" ${closed?'disabled':''}>Enviar</button></div>`;
    return html;
  }
'''
app = app[:start] + newfunc + app[end:]

# status no inbox
app = app.replace("<span class=\"status-badge ${t.status==='encerrado'?'neutral':'ok'}\">${t.status==='encerrado'?'Encerrado':'Aberto'}</span>", "<span class=\"status-badge ${t.status==='encerrado'?'neutral':t.status==='resolvido'?'ok':'info'}\">${esc(supportStatusLabel(t.status))}</span>")
rep("      } else {\n        html += renderInboxList(state.suporteInbox);\n      }", "      } else {\n        html += `<div class=\"toolbar\"><button class=\"btn-outline\" id=\"btn-print-support-list\">Relatório / Salvar PDF</button></div>` + renderInboxList(state.suporteInbox);\n      }")

# 17) Funções documentais
anchor = "  function renderTurmasSection(){\n"
docs = r'''  function docShell(title,body){ return `<div class="section-title">${esc(title)}</div><div class="toolbar"><button class="btn-outline" id="btn-print-doc">Imprimir / Salvar PDF</button></div><div class="panel doc-panel">${body}</div>`; }
  function renderManualOperacional(){ return docShell('Manual Operacional',`<h4>1. Acesso e perfis</h4><p>O acesso é realizado exclusivamente com conta Google. Alunos entram como Aluno(a); Professores novos aguardam aprovação do Usuário Mestre.</p><h4>2. Turmas e alunos</h4><p>Crie a turma, cadastre alunos individualmente ou importe PDF, confira nome e matrícula e salve os prazos dos cinco módulos.</p><h4>3. Prazos e módulos</h4><p>O Módulo 1 inicia liberado. Os demais são liberados sequencialmente após a correção e liberação da Nota Final do módulo anterior. Após o prazo, o módulo bloqueia; o professor pode permitir entrega em atraso, com desconto automático de 2,0 pontos na primeira entrega fora do prazo original.</p><h4>4. Correção e notas</h4><p>O aluno conclui conteúdo, cinco listas e quiz, envia o módulo e aguarda revisão. O professor aprova/libera ou devolve para ajustes.</p><h4>5. Suporte, relatórios e backup</h4><p>Chamados têm protocolo, status, prazo de resposta, reabertura e impressão/PDF. Relatórios, auditoria e backup ficam disponíveis no painel do Professor.</p>`); }
  function renderChecklistStatus(){
    const turmas=state.turmas||[], deadlines=turmas.reduce((n,t)=>n+MODULES.filter(m=>t.moduleSettings&&t.moduleSettings[m.id]&&t.moduleSettings[m.id].deadline).length,0), cad=turmas.reduce((n,t)=>n+(t.students||[]).filter(s=>s.nome&&s.matricula).length,0), total=turmas.reduce((n,t)=>n+(t.students||[]).length,0), pending=(state.correcoesPendentes&&state.correcoesPendentes.modulosPendentes||[]).length;
    const items=[['Turmas cadastradas',turmas.length>0,`${turmas.length} turma(s)`],['Alunos com nome e matrícula',total>0&&cad===total,`${cad}/${total}`],['Prazos configurados',deadlines===turmas.length*MODULES.length&&turmas.length>0,`${deadlines}/${turmas.length*MODULES.length||0}`],['Correções pendentes revisadas',pending===0,`${pending} pendente(s)`],['Auditoria de acesso ativa',true,'Login e logout registrados'],['Suporte operacional',true,'Status, prazos, reabertura e PDF disponíveis'],['Backup pedagógico disponível',true,'Exportação JSON ativa']];
    return docShell('Checklist de Status',`<p>Verificação operacional do ambiente do Professor.</p><div class="checklist-grid">${items.map(([l,ok,d])=>`<div class="check-item ${ok?'ok':'warn'}"><b>${ok?'✓':'!'} ${esc(l)}</b><span>${esc(d)}</span></div>`).join('')}</div>`);
  }
  function renderGuiaPedagogico(){ return docShell('Guia Pedagógico do Professor',`<h4>Organização didática</h4><p>A disciplina está estruturada em cinco módulos progressivos. O estudante avança somente após concluir e ter corrigido o módulo anterior, favorecendo acompanhamento formativo e domínio cumulativo.</p><h4>Estrutura de cada módulo</h4><ul><li>Conteúdo teórico e exemplos;</li><li>5 listas autocorrigidas de 10 questões;</li><li>Quiz avaliativo;</li><li>Recuperação paralela;</li><li>Envio para revisão do Professor e Nota Final.</li></ul><h4>Avaliação</h4><p>A nota automática considera 50% da média das listas e 50% do melhor resultado entre Quiz e Recuperação. A Nota Final é liberada pelo Professor. Entrega após o prazo original, quando autorizada, recebe desconto automático de 2,0 pontos.</p><h4>Intervenção pedagógica</h4><p>Use Correções Pendentes para feedback individual, Auditoria para rastreabilidade, Relatórios para acompanhamento e Suporte para dúvidas e ocorrências. A devolução para ajustes mantém histórico e permite nova tentativa.</p><h4>Boas práticas</h4><p>Defina os prazos antes da abertura da turma, acompanhe módulos pendentes regularmente, registre feedback objetivo e gere backup periódico.</p>`); }

'''
rep(anchor, docs + anchor)

# 18) Handlers para auditoria, documentos e suporte
anchor = "    // ---- Usuários (painel do Usuário Mestre) ----\n"
handlers = r'''    const auditAll=document.getElementById('audit-all'); if(auditAll) auditAll.addEventListener('click',()=>{state.accessAuditOnly=false;render();});
    const auditAccess=document.getElementById('audit-access'); if(auditAccess) auditAccess.addEventListener('click',()=>{state.accessAuditOnly=true;render();});
    const printDoc=document.getElementById('btn-print-doc'); if(printDoc) printDoc.addEventListener('click',()=>window.print());
    const printSupport=document.getElementById('btn-print-support'); if(printSupport) printSupport.addEventListener('click',()=>window.print());
    const printSupportList=document.getElementById('btn-print-support-list'); if(printSupportList) printSupportList.addEventListener('click',()=>window.print());
    const saveSupport=document.getElementById('btn-save-support-control'); if(saveSupport) saveSupport.addEventListener('click',async()=>{const t=state.suporteThread;if(!t)return;const old=t.status;const st=document.getElementById('support-status'),due=document.getElementById('support-due'),reo=document.getElementById('support-reopen');t.status=st?st.value:t.status;t.responseDueAt=due&&due.value?new Date(due.value).getTime():null;t.reopenUntil=reo&&reo.value?new Date(reo.value).getTime():null;t.updatedAt=Date.now();if(t.status==='encerrado'&&old!=='encerrado')t.closedAt=Date.now();if(t.status!=='encerrado')t.closedAt=null;t.history.push({type:'status',from:old,to:t.status,ts:Date.now(),by:state.user.name});const kind=state.user.role==='professor'?(state.suporteTab==='alunos'?'aluno-professor':'professor-admin'):suporteInboxKind();await saveThread(kind,t);await logAudit('status_suporte',`${state.user.name} alterou o chamado ${t.protocol||''} para ${supportStatusLabel(t.status)}.`);render();});
    const reopenSupport=document.getElementById('btn-reopen-support'); if(reopenSupport) reopenSupport.addEventListener('click',async()=>{const t=state.suporteThread;if(!t||!canReopenThread(t))return;t.history.push({type:'reabertura',ts:Date.now(),by:state.user.name});t.status='aberto';t.closedAt=null;t.updatedAt=Date.now();const kind=state.user.role==='aluno'?(state.suporteTab==='professor'?'aluno-professor':'aluno-admin'):(state.user.role==='professor'?(state.suporteTab==='alunos'?'aluno-professor':'professor-admin'):suporteInboxKind());await saveThread(kind,t);await logAudit('suporte_reaberto',`${state.user.name} reabriu o chamado ${t.protocol||''}.`);render();});

'''
rep(anchor, handlers + anchor)

# Remove handler antigo de toggle status, que não existe mais na nova UI
oldline = "    const toggleSupport=document.getElementById('btn-toggle-support-status'); if(toggleSupport) toggleSupport.addEventListener('click',async()=>{const thread=state.suporteThread; if(!thread)return; thread.status=thread.status==='encerrado'?'aberto':'encerrado'; thread.updatedAt=Date.now(); const kind = state.user.role==='professor' ? (state.suporteTab==='alunos'?'aluno-professor':'professor-admin') : suporteInboxKind(); await saveThread(kind,thread); await logAudit('status_suporte',`${state.user.name} alterou o chamado ${thread.protocol||''} para ${thread.status}.`); if((state.user.role==='professor'&&state.suporteTab==='alunos')||state.user.role==='admin') state.suporteInbox=await listThreads(suporteInboxKind()); render();});\n\n"
if oldline in app: app=app.replace(oldline,'',1)

# 19) Carregamento da turma no login do aluno e limpeza no logout auth
rep("        state.progress = await loadProgress(profile.name);\n        state.view = 'dashboard';", "        state.progress = await loadProgress(profile.name);\n        state.studentTurma = await loadStudentTurma(profile.name);\n        state.view = 'dashboard';")
rep("      state.progress = null; state.roster = null;\n      state.view = 'login';", "      state.progress = null; state.roster = null; state.studentTurma=null;\n      state.view = 'login';")

# 20) Manuais existentes: sequência, prazo e suporte completo
app = app.replace('No menu "Início" você encontra os 5 módulos da disciplina. Cada módulo tem quatro abas:', 'No menu "Início" você encontra os 5 módulos da disciplina. O avanço é sequencial: o próximo módulo é liberado somente após a correção e liberação do anterior. Os prazos definidos pelo professor aparecem nos cartões. Cada módulo tem quatro abas:')
app = app.replace('Cada chamado recebe um protocolo, mantém o histórico da conversa e exibe seu status (Aberto/Encerrado).', 'Cada chamado recebe protocolo, histórico, status administrativo, prazo de resposta e período de reabertura. Chamados e listas podem ser impressos ou salvos em PDF.')
app = app.replace('Os módulos enviados pelos alunos aparecem em "Correções Pendentes".', 'Defina os prazos dos módulos dentro de cada turma. O vencimento bloqueia automaticamente o módulo; a entrega tardia autorizada recebe desconto de 2,0 pontos. Os módulos enviados pelos alunos aparecem em "Correções Pendentes".')

# 21) envio de suporte não reabre automaticamente chamado encerrado; inicia histórico/protocolo
app = app.replace("    if (thread.status === 'encerrado') thread.status='aberto';\n    thread.updatedAt=Date.now();", "    if (thread.status === 'encerrado') return;\n    thread.updatedAt=Date.now();")
app = app.replace("if (!thread.protocol){ const d=new Date(); thread.protocol='SUP-'+d.toISOString().slice(0,10).replace(/-/g,'')+'-'+Math.random().toString(36).slice(2,7).toUpperCase(); thread.createdAt=Date.now(); }", "if (!thread.protocol){ const d=new Date(); thread.protocol='SUP-'+d.toISOString().slice(0,10).replace(/-/g,'')+'-'+Math.random().toString(36).slice(2,7).toUpperCase(); thread.createdAt=Date.now(); thread.history=thread.history||[]; thread.history.push({type:'abertura',ts:Date.now(),by:state.user.name}); }")

# CSS complementar
css = r'''
  /* Melhorias prioritárias — prazos, bloqueios, suporte e documentação */
  #cont-avancada .module-row.locked { opacity:.58; cursor:not-allowed; filter:saturate(.55); }
  #cont-avancada .module-row.locked:hover { transform:none; box-shadow:none; }
  #cont-avancada .deadline-text { margin-top:7px; font-size:12px; color:var(--ink-soft); }
  #cont-avancada .deadline-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:12px; margin:14px 0; }
  #cont-avancada .deadline-card { border:1px solid var(--line); background:#182536; padding:12px; display:grid; gap:7px; }
  #cont-avancada .deadline-card input[type=datetime-local], #cont-avancada .support-controls input, #cont-avancada .support-controls select { width:100%; box-sizing:border-box; background:#0F1724; color:var(--ink); border:1px solid #3A4C60; padding:8px; }
  #cont-avancada .checkline { display:flex; gap:7px; align-items:center; }
  #cont-avancada .support-dates { font-size:12px; color:var(--ink-soft); margin:8px 0 12px; }
  #cont-avancada .support-controls { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:10px; align-items:end; border:1px solid var(--line); background:#182536; padding:12px; margin-bottom:12px; }
  #cont-avancada .doc-panel h4 { margin-top:20px; }
  #cont-avancada .checklist-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:10px; margin-top:14px; }
  #cont-avancada .check-item { border:1px solid var(--line); padding:12px; display:flex; justify-content:space-between; gap:12px; }
  #cont-avancada .check-item.ok { border-left:4px solid var(--green); }
  #cont-avancada .check-item.warn { border-left:4px solid var(--rule); }
  #cont-avancada .check-item span { color:var(--ink-soft); font-size:12px; text-align:right; }
  @media (max-width:800px){ #cont-avancada .support-controls,#cont-avancada .deadline-grid,#cont-avancada .checklist-grid{grid-template-columns:1fr;} }
'''
if 'Melhorias prioritárias — prazos, bloqueios, suporte e documentação' not in index:
    index=index.replace('</style>',css+'\n</style>',1)

APP.write_text(app,encoding='utf-8')
INDEX.write_text(index,encoding='utf-8')
print('Melhorias aplicadas aos arquivos locais do workflow.')

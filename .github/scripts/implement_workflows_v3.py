from pathlib import Path
p=Path('public/app.js')
s=p.read_text(encoding='utf-8')

# Firestore delete support
s=s.replace("  getFirestore, doc, getDoc, setDoc, updateDoc, collection, getDocs, query,\n  where, documentId\n", "  getFirestore, doc, getDoc, setDoc, updateDoc, deleteDoc, collection, getDocs, query,\n  where, documentId\n")
s=s.replace("async function kvSet(key, value){\n  await setDoc(doc(db, 'kv_store', key), { value, updatedAt: Date.now() });\n  return { key, value };\n}\n", "async function kvSet(key, value){\n  await setDoc(doc(db, 'kv_store', key), { value, updatedAt: Date.now() });\n  return { key, value };\n}\nasync function kvDelete(key){ await deleteDoc(doc(db,'kv_store',key)); }\n")

# state for selected support reports / backup filters
s=s.replace("    accessAuditOnly: false,\n", "    accessAuditOnly: false,\n    suporteSelected: [],\n    backupTurmaId: '',\n    backupSemester: '',\n")

# richer support normalization and status presentation
s=s.replace("  function supportStatusLabel(status){ const x=SUPPORT_STATUSES.find(i=>i[0]===status); return x?x[1]:'Aberto'; }\n", "  function supportStatusLabel(status){ const x=SUPPORT_STATUSES.find(i=>i[0]===status); return x?x[1]:'Aberto'; }\n  function supportStatusClass(status){ return ({aberto:'info',em_analise:'warn',aguardando_resposta:'warn',encaminhado_desenvolvimento:'info',aprovado_desenvolvimento:'info',resolvido:'ok',encerrado:'neutral'})[status]||'info'; }\n")
s=s.replace("    t.history=Array.isArray(t.history)?t.history:[]; return t;\n", "    t.history=Array.isArray(t.history)?t.history:[]; t.cycle=Number(t.cycle||1); return t;\n",1)

# selected support inbox rows
old="""      html += `<div class=\"thread-row\" data-thread=\"${esc(t.participantName)}\">\n        <div>\n          <b>${esc(t.participantName)}</b> <span class=\"status-badge ${t.status==='encerrado'?'neutral':t.status==='resolvido'?'ok':'info'}\">${esc(supportStatusLabel(t.status))}</span>\n          <div class=\"thread-preview\">${t.protocol?esc(t.protocol)+' · ':''}${last ? esc(last.text.slice(0,70)) : 'Sem mensagens ainda'}</div>\n        </div>\n        <span class=\"back-link\">Abrir →</span>\n      </div>`;\n"""
new="""      const selected=(state.suporteSelected||[]).includes(t.participantName);\n      html += `<div class=\"thread-row\"><label class=\"checkline\" style=\"margin-right:10px\"><input type=\"checkbox\" data-support-select=\"${esc(t.participantName)}\" ${selected?'checked':''}></label><div class=\"thread-open\" data-thread=\"${esc(t.participantName)}\" style=\"display:flex;justify-content:space-between;align-items:center;gap:12px;flex:1;cursor:pointer\"><div><b>${esc(t.participantName)}</b> <span class=\"status-badge ${supportStatusClass(t.status)}\">${esc(supportStatusLabel(t.status))}</span><div class=\"thread-preview\">${t.protocol?esc(t.protocol)+' · ':''}${last?esc(last.text.slice(0,70)):'Sem mensagens ainda'}${t.responseDueAt?' · Prazo: '+new Date(Number(t.responseDueAt)).toLocaleString('pt-BR'):''}</div></div><span class=\"back-link\">Abrir →</span></div></div>`;\n"""
if old not in s: raise SystemExit('inbox block not found')
s=s.replace(old,new)

s=s.replace("html += `<div class=\"toolbar\"><button class=\"btn-outline\" id=\"btn-print-support-list\">Relatório / Salvar PDF</button></div>` + renderInboxList(state.suporteInbox);", "html += `<div class=\"toolbar\"><button class=\"btn-outline\" id=\"btn-print-support-list\">Relatório geral / PDF</button><button class=\"btn-brass\" id=\"btn-print-support-selected\">Imprimir selecionados / PDF</button><button class=\"btn-outline\" id=\"btn-select-all-support\">Selecionar todos</button></div>` + renderInboxList(state.suporteInbox);")

# support conversation history
needle="    html+=`<div class=\"chat-box\">`;"
insert="    if(thread.history.length){ html+=`<details class=\"card-box\" style=\"margin:12px 0\"><summary><b>Histórico administrativo (${thread.history.length})</b></summary><div style=\"margin-top:10px\">${thread.history.slice().reverse().map(h=>`<div class=\"thread-preview\">${new Date(Number(h.ts||Date.now())).toLocaleString('pt-BR')} · ${esc(h.by||'Sistema')} · ${esc(h.type||'evento')}${h.from||h.to?' · '+esc(supportStatusLabel(h.from||''))+' → '+esc(supportStatusLabel(h.to||'')):''}</div>`).join('')}</div></details>`; }\n"
s=s.replace(needle,insert+needle)

# backup UI by turma / semester + delete
old="  function renderBackup(){\n    return `<div class=\"section-title\">Backup</div><div class=\"note\">Gera um arquivo JSON com as turmas deste professor e os registros pedagógicos dos alunos que constam nessas turmas. O arquivo não altera nem apaga dados do Firestore.</div><div class=\"card-box\"><h4>Backup pedagógico</h4><p class=\"desc\">Inclui turmas, alunos cadastrados, progresso/notas e os Planejamentos Semestrais e Planos de Aula do professor.</p><button class=\"btn-brass\" id=\"btn-export-backup\">Gerar backup JSON</button></div>`;\n  }"
new="""  function renderBackup(){
    const semesters=[...new Set((state.turmas||[]).map(t=>t.semester||'').filter(Boolean))].sort().reverse();
    return `<div class="section-title">Backup por Turma e Semestre</div><div class="note">Exporte toda a base pedagógica ou filtre por turma e semestre. A exclusão de turma remove de forma encadeada o cadastro da turma e os registros pedagógicos vinculados aos alunos daquela turma, mediante confirmação explícita.</div><div class="card-box"><h4>Selecionar escopo</h4><div class="inline-form"><div class="field"><label>Turma</label><select id="backup-turma"><option value="">Todas as turmas</option>${(state.turmas||[]).map(t=>`<option value="${esc(t.id)}" ${state.backupTurmaId===t.id?'selected':''}>${esc(t.name)}</option>`).join('')}</select></div><div class="field"><label>Semestre</label><select id="backup-semester"><option value="">Todos os semestres</option>${semesters.map(v=>`<option ${state.backupSemester===v?'selected':''}>${esc(v)}</option>`).join('')}</select></div></div><div class="toolbar"><button class="btn-brass" id="btn-export-backup">Gerar backup JSON</button></div></div><div class="card-box"><h4>Exclusão completa de turma</h4><p class="desc">Selecione uma turma acima. Antes de excluir, gere o backup. A operação remove turma, progresso dos alunos vinculados e chamados de suporte desses alunos. Planejamentos gerais do professor são preservados.</p><button class="btn-outline" id="btn-delete-turma-complete" ${state.backupTurmaId?'':'disabled'}>Excluir turma e registros vinculados</button></div>`;
  }"""
if old not in s: raise SystemExit('backup render not found')
s=s.replace(old,new)

# turma semester field + create default
s=s.replace("const turma = { id: newTurmaId(), name, professor: state.user.name, students: [], createdAt: Date.now() };", "const turma = { id: newTurmaId(), name, professor: state.user.name, semester: (new Date().getMonth()<6?'1º':'2º')+' semestre/'+new Date().getFullYear(), students: [], createdAt: Date.now() };")
s=s.replace("<div class=\"subtitle\">${turma.students.length} aluno${turma.students.length===1?'':'s'} matriculado${turma.students.length===1?'':'s'}</div>", "<div class=\"subtitle\">${turma.students.length} aluno${turma.students.length===1?'':'s'} matriculado${turma.students.length===1?'':'s'} · ${esc(turma.semester||'Semestre não informado')}</div>")

# correction cycle formalization
s=s.replace("if(c.latePenalty===undefined)c.latePenalty=0;", "if(c.latePenalty===undefined)c.latePenalty=0; if(c.cycle===undefined)c.cycle=1;")
s=s.replace("c.history.push({type:'ciclo_avaliativo_concluido',ts:now,late:c.late,latePenalty:c.latePenalty});", "c.history.push({type:c.cycle>1?'reenvio':'envio',cycle:c.cycle,ts:now,late:c.late,latePenalty:c.latePenalty});")
s=s.replace("c.history.push({type:'liberacao_pedagogica',ts:now,by:state.user.name,grade:c.finalGrade});", "c.history.push({type:'aprovacao',cycle:c.cycle,ts:now,by:state.user.name,grade:c.finalGrade});")
s=s.replace("c.history.push({type:'devolucao',ts:Date.now(),feedback}); it.mp.exerciseScores", "c.history.push({type:'devolucao',cycle:c.cycle,ts:Date.now(),by:state.user.name,feedback}); c.cycle=Number(c.cycle||1)+1; it.mp.exerciseScores")

# handlers: support row selector class changed
s=s.replace("document.querySelectorAll('.thread-row[data-thread]').forEach(row => {", "document.querySelectorAll('[data-thread]').forEach(row => {")

# insert support selection handlers before release modules
anchor="    document.querySelectorAll('[data-release-module]').forEach(btn=>{"
handlers="""    document.querySelectorAll('[data-support-select]').forEach(cb=>cb.addEventListener('click',e=>e.stopPropagation()));
    document.querySelectorAll('[data-support-select]').forEach(cb=>cb.addEventListener('change',()=>{const k=cb.getAttribute('data-support-select');const set=new Set(state.suporteSelected||[]);cb.checked?set.add(k):set.delete(k);state.suporteSelected=[...set];}));
    const selectAllSupport=document.getElementById('btn-select-all-support'); if(selectAllSupport) selectAllSupport.addEventListener('click',()=>{state.suporteSelected=(state.suporteInbox||[]).map(t=>t.participantName);render();});
    const printSelectedSupport=document.getElementById('btn-print-support-selected'); if(printSelectedSupport) printSelectedSupport.addEventListener('click',()=>{const selected=(state.suporteInbox||[]).filter(t=>(state.suporteSelected||[]).includes(t.participantName));if(!selected.length){alert('Selecione ao menos um chamado.');return;}const w=window.open('','_blank');if(!w)return;const rows=selected.map(t=>`<tr><td>${esc(t.protocol||'—')}</td><td>${esc(t.participantName)}</td><td>${esc(supportStatusLabel(t.status))}</td><td>${t.createdAt?new Date(Number(t.createdAt)).toLocaleString('pt-BR'):'—'}</td><td>${t.responseDueAt?new Date(Number(t.responseDueAt)).toLocaleString('pt-BR'):'—'}</td><td>${esc((t.messages&&t.messages.length?t.messages[t.messages.length-1].text:'').slice(0,160))}</td></tr>`).join('');w.document.write(`<html><head><title>Relatório de chamados selecionados</title><style>body{font-family:Arial;padding:24px}table{width:100%;border-collapse:collapse}th,td{border:1px solid #bbb;padding:7px;text-align:left;font-size:12px}h2{margin-bottom:6px}</style></head><body><h2>Relatório de Chamados Selecionados</h2><p>Contabilidade Avançada · ${new Date().toLocaleString('pt-BR')}</p><table><tr><th>Protocolo</th><th>Usuário</th><th>Status</th><th>Abertura</th><th>Prazo</th><th>Última mensagem</th></tr>${rows}</table><script>window.onload=()=>window.print()<\/script></body></html>`);w.document.close();});

"""
s=s.replace(anchor,handlers+anchor)

# replace backup handler with scoped backup + deletion handlers
oldline="    const exportBackup=document.getElementById('btn-export-backup'); if(exportBackup) exportBackup.addEventListener('click',async()=>{await loadPlanningAll(); const names=new Set(); (state.turmas||[]).forEach(t=>(t.students||[]).forEach(a=>names.add((a.nome||'').trim()))); const alunos=(state.roster||[]).filter(r=>names.has((r.name||'').trim())); const payload={plataforma:'Contabilidade Avançada',geradoEm:new Date().toISOString(),professor:state.user.name,turmas:state.turmas,alunos,planejamentos:state.planningRecords,cadastrosPlanejamento:state.planningCatalog}; downloadText(`backup_contabilidade_avancada_${new Date().toISOString().slice(0,10)}.json`,JSON.stringify(payload,null,2),'application/json;charset=utf-8'); logAudit('backup_exportado',`${state.user.name} gerou backup pedagógico incluindo planejamentos.`);});"
newline="""    const backupTurma=document.getElementById('backup-turma');if(backupTurma)backupTurma.addEventListener('change',()=>{state.backupTurmaId=backupTurma.value;render();});
    const backupSemester=document.getElementById('backup-semester');if(backupSemester)backupSemester.addEventListener('change',()=>{state.backupSemester=backupSemester.value;render();});
    const exportBackup=document.getElementById('btn-export-backup'); if(exportBackup) exportBackup.addEventListener('click',async()=>{await loadPlanningAll();let turmas=(state.turmas||[]).filter(t=>(!state.backupTurmaId||t.id===state.backupTurmaId)&&(!state.backupSemester||(t.semester||'')===state.backupSemester));const names=new Set();turmas.forEach(t=>(t.students||[]).forEach(a=>names.add((a.nome||'').trim())));const alunos=(state.roster||[]).filter(r=>names.has((r.name||'').trim()));const payload={plataforma:'Contabilidade Avançada',geradoEm:new Date().toISOString(),professor:state.user.name,filtro:{turmaId:state.backupTurmaId||null,semestre:state.backupSemester||null},turmas,alunos,planejamentos:state.planningRecords,cadastrosPlanejamento:state.planningCatalog};downloadText(`backup_contabilidade_avancada_${new Date().toISOString().slice(0,10)}.json`,JSON.stringify(payload,null,2),'application/json;charset=utf-8');await logAudit('backup_exportado',`${state.user.name} gerou backup pedagógico por turma/semestre.`);});
    const deleteTurmaComplete=document.getElementById('btn-delete-turma-complete');if(deleteTurmaComplete)deleteTurmaComplete.addEventListener('click',async()=>{const turma=(state.turmas||[]).find(t=>t.id===state.backupTurmaId);if(!turma)return;const typed=prompt(`EXCLUSÃO COMPLETA: esta operação removerá a turma e os registros pedagógicos vinculados.\\n\\nDigite EXCLUIR para confirmar a turma ${turma.name}.`);if(typed!=='EXCLUIR')return;deleteTurmaComplete.disabled=true;for(const a of (turma.students||[])){const n=(a.nome||'').trim();if(!n)continue;await kvDelete('student:'+n);for(const kind of ['aluno-professor','aluno-admin']){try{await kvDelete('support:'+kind+':'+n);}catch(e){}}}await kvDelete('turma:'+turma.id);await logAudit('turma_excluida_completa',`${state.user.name} excluiu completamente a turma "${turma.name}" e registros pedagógicos vinculados.`);state.turmas=(state.turmas||[]).filter(t=>t.id!==turma.id);state.backupTurmaId='';state.roster=await loadRoster();alert('Turma e registros vinculados excluídos.');render();});"""
if oldline not in s: raise SystemExit('backup handler not found')
s=s.replace(oldline,newline)

# support status history only when changed; preserve deadline events
oldfrag="t.history.push({type:'status',from:old,to:t.status,ts:Date.now(),by:state.user.name});"
newfrag="if(old!==t.status)t.history.push({type:'status',from:old,to:t.status,ts:Date.now(),by:state.user.name});t.history.push({type:'controle_administrativo',ts:Date.now(),by:state.user.name,responseDueAt:t.responseDueAt,reopenUntil:t.reopenUntil});"
s=s.replace(oldfrag,newfrag)

# manual updates
s=s.replace('"Backup" gera arquivo JSON das turmas e dados pedagógicos vinculados.', '"Backup" permite exportação por turma e semestre e, mediante confirmação, exclusão completa da turma e registros pedagógicos vinculados.')
s=s.replace('com chamados identificados por protocolo e status, onde você pode responder, encerrar ou reabrir cada atendimento;', 'com chamados identificados por protocolo, os sete estados administrativos, prazo de resposta, reabertura, histórico permanente e relatório selecionável para impressão/PDF;')

p.write_text(s,encoding='utf-8')

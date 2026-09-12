from pathlib import Path
import re

p = Path('public/app.js')
s = p.read_text(encoding='utf-8')


def sub_once(pattern, repl, label, flags=re.S):
    global s
    new, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'Falha ao atualizar {label}: ocorrências={n}')
    s = new

# 1. Menu do professor
s = s.replace("['professor:correcoes','Correções Pendentes']", "['professor:correcoes','Pendências']", 1)

# 2. Helpers de conclusão automática e status
old_helpers = '''  function moduleReadyForSubmission(mp, m){
    return !!(mp && mp.contentRead && Array.isArray(mp.exerciseScores) && mp.exerciseScores.length >= m.exerciseLists.length && mp.exerciseScores.slice(0,m.exerciseLists.length).every(v => v !== null && v !== undefined) && mp.quizScore !== null && mp.quizScore !== undefined);
  }
  function fmtGrade(v){ return (v === null || v === undefined || Number.isNaN(Number(v))) ? '—' : Number(v).toFixed(1).replace('.',','); }
  function correctionBadge(mp){
    const c = correctionState(mp);
    const cls = c.status === 'corrigido' ? 'ok' : (c.status === 'ajustes' ? 'warn' : (c.status === 'em_correcao' ? 'info' : 'neutral'));
    return `<span class="status-badge ${cls}">${esc(statusLabel(c.status))}</span>`;
  }
'''
new_helpers = '''  function moduleReadyForSubmission(mp, m){
    return !!(mp && mp.contentRead && Array.isArray(mp.exerciseScores) && mp.exerciseScores.length >= m.exerciseLists.length && mp.exerciseScores.slice(0,m.exerciseLists.length).every(v => v !== null && v !== undefined) && mp.quizScore !== null && mp.quizScore !== undefined);
  }
  function moduleCompleted(mp){
    return !!(mp && mp.contentRead && Array.isArray(mp.exerciseScores) && mp.exerciseScores.slice(0,5).length === 5 && mp.exerciseScores.slice(0,5).every(v => v !== null && v !== undefined) && mp.quizScore !== null && mp.quizScore !== undefined);
  }
  function fmtGrade(v){ return (v === null || v === undefined || Number.isNaN(Number(v))) ? '—' : Number(v).toFixed(1).replace('.',','); }
  function moduleStatusLabel(mp){ return moduleCompleted(mp) ? 'Concluído' : 'Em andamento'; }
  function correctionBadge(mp){
    const done = moduleCompleted(mp);
    return `<span class="status-badge ${done?'ok':'neutral'}">${done?'Concluído':'Em andamento'}</span>`;
  }
'''
if old_helpers not in s:
    raise SystemExit('Bloco de helpers não encontrado')
s = s.replace(old_helpers, new_helpers, 1)

# 3. Liberação sequencial sem revisão manual
old_access = "if(idx>0){ const prev=state.progress&&state.progress.modules[MODULES[idx-1].id]; const pc=correctionState(prev); if(!(pc.status==='corrigido'&&pc.released)) return {locked:true,reason:'Conclua e tenha a correção do módulo anterior liberada pelo professor.'}; }"
new_access = "if(idx>0){ const prevModule=MODULES[idx-1], prev=state.progress&&state.progress.modules[prevModule.id]; if(!moduleReadyForSubmission(prev,prevModule)) return {locked:true,reason:'Conclua o conteúdo, as 5 listas e o Quiz do módulo anterior para avançar.'}; }"
if old_access not in s:
    raise SystemExit('Regra de liberação sequencial não encontrada')
s = s.replace(old_access, new_access, 1)

# 4. Tela Minhas Notas
new_mynotes = r'''  function renderMinhasNotas(){
    let html = `<div class="section-title">Minhas notas</div>`;
    html += `<div class="note">Os <b>5 exercícios e o Quiz valem 10,0 pontos cada</b> e têm o mesmo peso. A <b>Recuperação não é uma 7ª nota</b>: sua nota é comparada individualmente com cada exercício e com o Quiz e substitui toda nota inferior. Quando houver substituição, aparece <b>nota original → nota considerada</b>. A <b>Nota do Módulo</b> é calculada automaticamente pelo sistema.</div>`;
    html += `<div class="table-scroll"><table class="roster"><tr><th>Módulo</th><th class="num">Ex. 1</th><th class="num">Ex. 2</th><th class="num">Ex. 3</th><th class="num">Ex. 4</th><th class="num">Ex. 5</th><th class="num">Quiz</th><th class="num">Recuperação</th><th class="num">Nota do Módulo</th><th>Situação</th></tr>`;
    MODULES.forEach(m => {
      const mp = state.progress.modules[m.id]; const c=correctionState(mp);
      const quizTxt = score10(mp.quizScore,mp.quizTotal); const recTxt=score10(mp.recoveryScore,mp.recoveryTotal);
      const adjusted = effectiveAssessmentScores10(mp);
      const exerciseCells = Array.from({length:5}, (_,i) => {
        const original = Array.isArray(mp.exerciseScores) ? mp.exerciseScores[i] : null;
        const effective = adjusted.exercises[i]; const replaced = !!(adjusted.replaced && adjusted.replaced[i]);
        if (effective === null || effective === undefined) return `<td class="num">—</td>`;
        const shown = replaced ? `${fmtGrade(Number(original))} → <b>${fmtGrade(effective)}</b>` : fmtGrade(effective);
        return `<td class="num">${shown}</td>`;
      }).join('');
      const quizReplaced = !!(adjusted.replaced && adjusted.replaced[5]);
      const quizCell = adjusted.quiz === null || adjusted.quiz === undefined ? '—' : (quizReplaced ? `${fmtGrade(quizTxt)} → <b>${fmtGrade(adjusted.quiz)}</b>` : fmtGrade(adjusted.quiz));
      const grade = moduleReadyForSubmission(mp,m) ? effectiveModuleGrade(mp) : null;
      html += `<tr><td>${esc(m.num+'. '+m.title)}</td>${exerciseCells}<td class="num">${quizCell}</td><td class="num">${fmtGrade(recTxt)}</td><td class="num"><b>${fmtGrade(grade)}</b></td><td>${moduleStatusLabel(mp)}</td></tr>`;
      if (c.feedback) html += `<tr><td colspan="10"><div class="feedback-box"><b>Registro anterior do professor:</b> ${esc(c.feedback)}</div></td></tr>`;
    });
    html += `</table></div>`;
    return html;
  }

  // ---- Manual ----'''
sub_once(r"  function renderMinhasNotas\(\)\{.*?\n  // ---- Manual ----", new_mynotes, 'Minhas Notas')

# 5. Fluxo no detalhe do módulo: retirar envio manual
old_module_flow = '''    const corr = correctionState(mp);
    html += `<div class="module-correction"><h4>Fluxo de correção do módulo</h4><div style="margin-bottom:8px">${correctionBadge(mp)}</div>`;
    if (corr.feedback) html += `<div class="feedback-box"><b>Feedback do professor:</b> ${esc(corr.feedback)}</div>`;
    if (corr.status === 'corrigido' && corr.released) html += `<div class="quiz-score">Nota Final liberada: <b>${fmtGrade(corr.finalGrade)} / 10,0</b></div>`;
    else if (corr.status === 'em_correcao') html += `<p class="thread-preview">Enviado em ${corr.submittedAt?new Date(corr.submittedAt).toLocaleString('pt-BR'):'—'}. Aguarde a revisão do professor.</p>`;
    else if (moduleReadyForSubmission(mp,m)) html += `<p class="thread-preview">Nota automática atual: <b>${fmtGrade(effectiveModuleGrade(mp))}</b>. Envie o módulo para o professor revisar e liberar a Nota Final.</p><button class="btn-brass" id="btn-submit-module">Enviar módulo para correção</button>`;
    else html += `<p class="thread-preview">Conclua o conteúdo, as 5 listas autocorrigidas e o quiz para poder enviar o módulo à correção.</p>`;
    html += `</div>`;
'''
new_module_flow = '''    const corr = correctionState(mp);
    html += `<div class="module-correction"><h4>Situação do módulo</h4><div style="margin-bottom:8px">${correctionBadge(mp)}</div>`;
    if (corr.feedback) html += `<div class="feedback-box"><b>Registro anterior do professor:</b> ${esc(corr.feedback)}</div>`;
    if (moduleReadyForSubmission(mp,m)) html += `<div class="quiz-score">Módulo concluído. Nota do Módulo: <b>${fmtGrade(effectiveModuleGrade(mp))} / 10,0</b></div><p class="thread-preview">O próximo módulo é liberado automaticamente. A Recuperação, quando realizada, atualiza a nota se substituir resultados inferiores.</p>`;
    else html += `<p class="thread-preview">Conclua o conteúdo, as 5 listas autocorrigidas e o Quiz. A nota e a liberação do próximo módulo serão processadas automaticamente.</p>`;
    html += `</div>`;
'''
if old_module_flow not in s:
    raise SystemExit('Fluxo manual no módulo não encontrado')
s = s.replace(old_module_flow, new_module_flow, 1)

# 6. Remover listener do botão de envio manual
s, n = re.subn(r"\n    const btnSubmitModule=document\.getElementById\('btn-submit-module'\);\n    if\(btnSubmitModule\).*?render\(\);\}\);\n", "\n", s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'Listener de envio manual não removido: {n}')

# 7. Ao finalizar Quiz/Recuperação, registrar conclusão e penalidade automaticamente
old_score_save = '''      if (kind === 'quiz') state.progress.modules[state.activeModuleId].quizScore = score;
      else state.progress.modules[state.activeModuleId].recoveryScore = score;
      await saveProgress(state.progress);
'''
new_score_save = '''      const activeMp = state.progress.modules[state.activeModuleId];
      if (kind === 'quiz') activeMp.quizScore = score;
      else activeMp.recoveryScore = score;
      if (moduleReadyForSubmission(activeMp,m)){
        const c = correctionState(activeMp); const now = Date.now();
        if (kind === 'quiz' && !c.firstSubmittedAt){
          const access = moduleAccess(m); c.firstSubmittedAt = now; c.late = !!access.late; c.latePenalty = access.late ? 2 : 0;
          c.history.push({type:'conclusao_automatica',ts:now,late:c.late,latePenalty:c.latePenalty});
        }
        c.status='corrigido'; c.reviewedAt=now; c.released=true; c.finalGrade=effectiveModuleGrade(activeMp); activeMp.correction=c;
      }
      await saveProgress(state.progress);
'''
if old_score_save not in s:
    raise SystemExit('Salvamento de Quiz/Recuperação não encontrado')
s = s.replace(old_score_save, new_score_save, 1)

# 8. Atualizar texto da Recuperação dentro do módulo
s = s.replace('A recuperação é uma avaliação paralela e não é uma 7ª nota da média. Os 5 exercícios e o Quiz valem 10,0 pontos cada e têm o mesmo peso. Se a nota da Recuperação for maior que a menor nota entre essas 6 atividades, ela substitui somente essa menor nota — inclusive se a menor nota for a do Quiz.', 'A recuperação é uma avaliação paralela e não é uma 7ª nota da média. Os 5 exercícios e o Quiz valem 10,0 pontos cada e têm o mesmo peso. A nota da Recuperação é comparada individualmente com as 6 atividades e substitui todas as notas inferiores, inclusive a do Quiz.', 1)

# 9. Pendências: retirar módulos para revisão
new_pending = r'''  function renderCorrecoesPendentes(){
    const data = state.correcoesPendentes || { incompletos: [], mensagensPendentes: [], modulosPendentes: [] };
    let html = `<div class="section-title">Pendências</div>`;
    html += `<div class="note">Esta área reúne apenas situações que necessitam da atuação do professor. Exercícios, Quiz, Recuperação e Nota do Módulo são processados automaticamente pelo sistema.</div>`;
    html += `<h4 style="margin:18px 0 8px">Cadastros a regularizar (${data.incompletos.length})</h4>`;
    if (!data.incompletos.length) html += `<div class="empty-state">Nenhum cadastro pendente no momento.</div>`;
    else data.incompletos.forEach(it=>{ html += `<div class="thread-row" data-fix-turma="${esc(it.turmaId)}"><div><b>${esc(it.nome||'(nome não identificado)')}</b><div class="thread-preview">Turma: ${esc(it.turmaNome)} · ${!it.nome?'Nome ausente · ':''}${!it.matricula?'Matrícula ausente':''}</div></div><span class="back-link">Regularizar →</span></div>`; });
    html += `<h4 style="margin:24px 0 8px">Mensagens aguardando resposta (${data.mensagensPendentes.length})</h4>`;
    if (!data.mensagensPendentes.length) html += `<div class="empty-state">Nenhuma mensagem pendente.</div>`;
    else data.mensagensPendentes.forEach(t=>{const last=t.messages[t.messages.length-1]; html += `<div class="thread-row" data-goto-thread="${esc(t.participantName)}"><div><b>${esc(t.participantName)}</b><div class="thread-preview">${esc(last.text.slice(0,70))}</div></div><span class="back-link">Responder →</span></div>`;});
    return html;
  }

  function renderAcompanhamento(){'''
sub_once(r"  function renderCorrecoesPendentes\(\)\{.*?\n  function renderAcompanhamento\(\)\{", new_pending, 'Pendências')

# 10. Notas da Turma: resumo + detalhes expansíveis
new_acomp = r'''  function renderAcompanhamento(){
    const roster = professorRoster(state.roster || []).slice().sort((a,b)=>(a.name||'').localeCompare(b.name||''));
    let html = `<div class="note">As notas são calculadas automaticamente pelo sistema. Clique em <b>Ver detalhes</b> para visualizar as notas originais, substituições pela Recuperação e a Nota do Módulo.</div>`;
    html += `<div class="section-title">Notas da Turma (${roster.length} aluno${roster.length===1?'':'s'})</div>`;
    html += `<div class="toolbar"><button class="btn-outline" id="btn-print-report">Imprimir / Salvar PDF</button><button class="btn-brass" id="btn-export-grades">Exportar CSV</button></div>`;
    if (!roster.length) return html + `<div class="empty-state">Nenhum aluno entrou na plataforma ainda.</div>`;
    html += `<div class="table-scroll"><table class="roster"><tr><th>Aluno</th>${MODULES.map(m=>`<th class="num">M${m.num}</th>`).join('')}<th class="num">Média</th><th class="num">Ação</th></tr>`;
    roster.forEach((st,idx)=>{
      const grades=[]; html += `<tr><td><b>${esc(st.name)}</b></td>`;
      MODULES.forEach(m=>{const mp=st.modules[m.id]; const v=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null; if(v!==null) grades.push(Number(v)); html += `<td class="num"><b>${fmtGrade(v)}</b><div class="cell-status">${moduleStatusLabel(mp)}</div></td>`;});
      const avg=grades.length?grades.reduce((a,b)=>a+b,0)/grades.length:null;
      html += `<td class="num"><b>${fmtGrade(avg)}</b></td><td class="num"><button class="btn-brass" data-toggle-student-details="${idx}">Ver detalhes</button></td></tr>`;
      html += `<tr data-student-detail="${idx}" style="display:none"><td colspan="8"><div class="card-box"><h4>${esc(st.name)} — Detalhamento das avaliações</h4><div class="table-scroll"><table class="roster"><tr><th>Módulo</th><th class="num">Ex. 1</th><th class="num">Ex. 2</th><th class="num">Ex. 3</th><th class="num">Ex. 4</th><th class="num">Ex. 5</th><th class="num">Quiz</th><th class="num">Recuperação</th><th class="num">Nota do Módulo</th><th>Situação</th></tr>`;
      MODULES.forEach(m=>{
        const mp=st.modules[m.id], adjusted=effectiveAssessmentScores10(mp), rec=score10(mp.recoveryScore,mp.recoveryTotal), quizOrig=score10(mp.quizScore,mp.quizTotal);
        const exCells=Array.from({length:5},(_,i)=>{const orig=Array.isArray(mp.exerciseScores)?mp.exerciseScores[i]:null, eff=adjusted.exercises[i], rep=!!(adjusted.replaced&&adjusted.replaced[i]); if(eff===null||eff===undefined)return '<td class="num">—</td>'; return `<td class="num">${rep?`${fmtGrade(orig)} → <b>${fmtGrade(eff)}</b>`:fmtGrade(eff)}</td>`;}).join('');
        const qRep=!!(adjusted.replaced&&adjusted.replaced[5]); const qCell=adjusted.quiz===null||adjusted.quiz===undefined?'—':(qRep?`${fmtGrade(quizOrig)} → <b>${fmtGrade(adjusted.quiz)}</b>`:fmtGrade(adjusted.quiz));
        const grade=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null;
        html += `<tr><td><b>M${m.num}</b></td>${exCells}<td class="num">${qCell}</td><td class="num">${fmtGrade(rec)}</td><td class="num"><b>${fmtGrade(grade)}</b></td><td>${moduleStatusLabel(mp)}</td></tr>`;
      });
      html += `</table></div><div class="note" style="margin-top:12px"><b>Legenda:</b> quando a Recuperação substitui uma nota inferior, é exibido <b>original → considerada</b>. A Recuperação não é uma 7ª nota.</div></div></td></tr>`;
    });
    html += `</table></div>`; return html;
  }

  function csvEscape'''
sub_once(r"  function renderAcompanhamento\(\)\{.*?\n  function csvEscape", new_acomp, 'Notas da Turma')

# 11. CSV detalhado
new_csv = r'''function gradesCsv(){
    const rows=[['Aluno','Módulo','Ex1 Original','Ex1 Considerada','Ex2 Original','Ex2 Considerada','Ex3 Original','Ex3 Considerada','Ex4 Original','Ex4 Considerada','Ex5 Original','Ex5 Considerada','Quiz Original','Quiz Considerado','Recuperação','Nota do Módulo','Situação','Progresso Geral']];
    professorRoster(state.roster||[]).slice().sort((a,b)=>(a.name||'').localeCompare(b.name||'')).forEach(st=>{
      MODULES.forEach(m=>{
        const mp=st.modules[m.id], a=effectiveAssessmentScores10(mp), ex=[];
        for(let i=0;i<5;i++){const orig=Array.isArray(mp.exerciseScores)?mp.exerciseScores[i]:null; ex.push(fmtGrade(orig),fmtGrade(a.exercises[i]));}
        const qOrig=score10(mp.quizScore,mp.quizTotal), rec=score10(mp.recoveryScore,mp.recoveryTotal), grade=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null;
        rows.push([st.name,'M'+m.num,...ex,fmtGrade(qOrig),fmtGrade(a.quiz),fmtGrade(rec),fmtGrade(grade),moduleStatusLabel(mp),overallPct(st)+'%']);
      });
    });
    return '\ufeff'+rows.map(r=>r.map(csvEscape).join(';')).join('\n');
  }'''
sub_once(r"function gradesCsv\(\)\{.*?\n  \}", new_csv, 'CSV detalhado')

# 12. Relatório de Desempenho
new_report = r'''  function renderRelatorios(){
    const roster=professorRoster(state.roster||[]).slice().sort((a,b)=>(a.name||'').localeCompare(b.name||''));
    let html=`<div class="section-title">Relatório de Desempenho</div><div class="note">Visão geral e detalhada das notas e do progresso da turma. As notas são calculadas automaticamente e as substituições pela Recuperação permanecem identificadas.</div><div class="toolbar"><button class="btn-outline" id="btn-print-report">Imprimir / Salvar PDF</button><button class="btn-brass" id="btn-export-grades">Exportar CSV</button></div>`;
    if(!roster.length) return html+`<div class="empty-state">Nenhum aluno entrou na plataforma ainda.</div>`;
    html+=`<h4 style="margin:18px 0 8px">Resumo da Turma</h4><div class="table-scroll"><table class="roster"><tr><th>Aluno</th>${MODULES.map(m=>`<th class="num">M${m.num}</th>`).join('')}<th class="num">Média Geral</th><th class="num">Progresso</th></tr>`;
    roster.forEach(st=>{const vals=[]; html+=`<tr><td><b>${esc(st.name)}</b></td>`; MODULES.forEach(m=>{const mp=st.modules[m.id],v=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null;if(v!==null)vals.push(Number(v));html+=`<td class="num">${fmtGrade(v)}</td>`;}); const avg=vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null; html+=`<td class="num"><b>${fmtGrade(avg)}</b></td><td class="num">${overallPct(st)}%</td></tr>`;});
    html+=`</table></div><h4 style="margin:24px 0 8px">Detalhamento por Atividade</h4><div class="table-scroll"><table class="roster"><tr><th>Aluno</th><th>Módulo</th><th class="num">Ex. 1</th><th class="num">Ex. 2</th><th class="num">Ex. 3</th><th class="num">Ex. 4</th><th class="num">Ex. 5</th><th class="num">Quiz</th><th class="num">Recuperação</th><th class="num">Nota do Módulo</th><th>Situação</th></tr>`;
    roster.forEach(st=>MODULES.forEach(m=>{const mp=st.modules[m.id],a=effectiveAssessmentScores10(mp),rec=score10(mp.recoveryScore,mp.recoveryTotal),qOrig=score10(mp.quizScore,mp.quizTotal),grade=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null; const fmt=(orig,eff,rep)=>eff===null||eff===undefined?'—':(rep?`${fmtGrade(orig)} → <b>${fmtGrade(eff)}</b>`:fmtGrade(eff)); html+=`<tr><td>${esc(st.name)}</td><td><b>M${m.num}</b></td>${Array.from({length:5},(_,i)=>`<td class="num">${fmt(Array.isArray(mp.exerciseScores)?mp.exerciseScores[i]:null,a.exercises[i],!!(a.replaced&&a.replaced[i]))}</td>`).join('')}<td class="num">${fmt(qOrig,a.quiz,!!(a.replaced&&a.replaced[5]))}</td><td class="num">${fmtGrade(rec)}</td><td class="num"><b>${fmtGrade(grade)}</b></td><td>${moduleStatusLabel(mp)}</td></tr>`;}));
    html+=`</table></div>`; return html;
  }'''
sub_once(r"  function renderRelatorios\(\)\{.*?\n  \}", new_report, 'Relatório de Desempenho')

# 13. Checklist e documentos internos
old_check = "const turmas=state.turmas||[], deadlines=turmas.reduce((n,t)=>n+MODULES.filter(m=>t.moduleSettings&&t.moduleSettings[m.id]&&t.moduleSettings[m.id].deadline).length,0), cad=turmas.reduce((n,t)=>n+(t.students||[]).filter(s=>s.nome&&s.matricula).length,0), total=turmas.reduce((n,t)=>n+(t.students||[]).length,0), pending=(state.correcoesPendentes&&state.correcoesPendentes.modulosPendentes||[]).length;"
new_check = "const turmas=state.turmas||[], deadlines=turmas.reduce((n,t)=>n+MODULES.filter(m=>t.moduleSettings&&t.moduleSettings[m.id]&&t.moduleSettings[m.id].deadline).length,0), cad=turmas.reduce((n,t)=>n+(t.students||[]).filter(s=>s.nome&&s.matricula).length,0), total=turmas.reduce((n,t)=>n+(t.students||[]).length,0), pending=((state.correcoesPendentes&&state.correcoesPendentes.incompletos)||[]).length+((state.correcoesPendentes&&state.correcoesPendentes.mensagensPendentes)||[]).length;"
s = s.replace(old_check,new_check,1)
s = s.replace("['Correções pendentes revisadas',pending===0,`${pending} pendente(s)`]", "['Pendências operacionais tratadas',pending===0,`${pending} pendente(s)`]", 1)

sub_once(r"  function renderManualOperacional\(\)\{.*?\n  \}", '''  function renderManualOperacional(){ return docShell('Manual Operacional',`<h4>1. Acesso e perfis</h4><p>O acesso é realizado exclusivamente com conta Google. Alunos entram como Aluno(a); Professores novos aguardam aprovação do Usuário Mestre.</p><h4>2. Turmas e alunos</h4><p>Crie a turma, cadastre alunos individualmente ou importe PDF, confira nome e matrícula e salve os prazos dos cinco módulos.</p><h4>3. Prazos e módulos</h4><p>O Módulo 1 inicia liberado. Os demais são liberados automaticamente após a conclusão do conteúdo, das 5 listas e do Quiz do módulo anterior. Após o prazo, o módulo bloqueia; quando o professor autoriza entrega em atraso, aplica-se desconto automático de 2,0 pontos na primeira conclusão fora do prazo original.</p><h4>4. Avaliação e notas</h4><p>Listas, Quiz e Recuperação são autocorrigidos. A Recuperação substitui todas as notas inferiores entre as 6 atividades avaliativas. A Nota do Módulo é calculada automaticamente, sem etapa de aprovação manual.</p><h4>5. Pendências, relatórios e suporte</h4><p>Pendências reúne apenas cadastros a regularizar e mensagens aguardando resposta. Relatórios apresentam resumo e detalhamento por atividade; Auditoria, Backup e Suporte permanecem disponíveis no painel do Professor.</p>`); }''', 'Manual Operacional')

sub_once(r"  function renderGuiaPedagogico\(\)\{.*?\n  \}", '''  function renderGuiaPedagogico(){ return docShell('Guia Pedagógico do Professor',`<h4>Organização didática</h4><p>A disciplina está estruturada em cinco módulos progressivos. O estudante avança automaticamente após concluir o conteúdo, as cinco listas e o Quiz do módulo anterior.</p><h4>Estrutura de cada módulo</h4><ul><li>Conteúdo teórico e exemplos;</li><li>5 listas autocorrigidas de 10 questões;</li><li>Quiz avaliativo autocorrigido;</li><li>Recuperação paralela autocorrigida;</li><li>Nota do Módulo calculada automaticamente.</li></ul><h4>Avaliação</h4><p>Os 5 exercícios e o Quiz têm o mesmo peso. A Recuperação não é uma 7ª nota: substitui individualmente todas as notas inferiores entre essas 6 atividades. Entrega após o prazo original, quando autorizada, recebe desconto automático de 2,0 pontos.</p><h4>Intervenção pedagógica</h4><p>Use Notas da Turma e Relatórios para acompanhar o desempenho detalhado; Pendências para cadastros e mensagens que exigem atuação; Auditoria para rastreabilidade e Suporte para dúvidas e ocorrências.</p><h4>Boas práticas</h4><p>Defina os prazos antes da abertura da turma, acompanhe o progresso e as notas por atividade, trate as pendências operacionais e gere backup periódico.</p>`); }''', 'Guia Pedagógico')

# 14. Manuais Aluno/Professor: ajustes textuais principais
s = s.replace('<p>No menu superior, "Minhas Notas" mostra as notas dos 5 exercícios, Quiz, Recuperação, média automática, situação da correção e Nota Final. Os 5 exercícios e o Quiz possuem o mesmo peso. A Recuperação substitui individualmente todas as notas dessas 6 atividades que forem inferiores à nota obtida na Recuperação. Quando houver substituição, a tela apresenta a nota original → nota considerada, inclusive no Quiz.</p><h4>Fluxo de correção por módulo</h4><p>Depois de concluir conteúdo, 5 listas e quiz, use <b>Enviar módulo para correção</b>. O professor poderá aprovar e liberar a nota ou devolver para ajustes com feedback. Em caso de ajustes, as atividades avaliativas do módulo ficam disponíveis novamente para novo envio.</p>', '<p>No menu superior, "Minhas Notas" mostra as notas dos 5 exercícios, Quiz, Recuperação, Nota do Módulo e situação. Os 5 exercícios e o Quiz possuem o mesmo peso. A Recuperação substitui individualmente todas as notas dessas 6 atividades que forem inferiores à nota obtida na Recuperação. Quando houver substituição, a tela apresenta a nota original → nota considerada, inclusive no Quiz.</p><h4>Conclusão do módulo</h4><p>Depois de concluir o conteúdo, as 5 listas e o Quiz, o sistema calcula automaticamente a Nota do Módulo e libera o módulo seguinte. Não há envio para correção manual. A Recuperação pode melhorar a nota ao substituir resultados inferiores.</p>', 1)

s = s.replace('<h4>Notas da Turma</h4>\n    <p>O menu "Notas da Turma" mostra, por aluno e módulo, a média automática, a Nota Final liberada e a situação da correção, com exportação em CSV e impressão/PDF. A média automática é a média aritmética simples dos 5 exercícios e do Quiz, todos com o mesmo peso. A Recuperação substitui somente a menor nota entre essas 6 atividades quando sua nota for superior.</p><h4>Correções Pendentes</h4><p>Defina os prazos dos módulos dentro de cada turma. O vencimento bloqueia automaticamente o módulo; a entrega tardia autorizada recebe desconto de 2,0 pontos. Os módulos enviados pelos alunos aparecem em "Correções Pendentes". A nota automática já vem calculada; o professor pode manter ou ajustar a Nota Final, registrar feedback, aprovar/liberar ou devolver o módulo para ajustes.</p><h4>Relatórios e Backup</h4><p>Os menus "Relatórios" e "Backup" permitem exportar acompanhamento em CSV, imprimir/salvar em PDF e gerar backup JSON das turmas e dados pedagógicos vinculados.</p>', '<h4>Notas da Turma</h4>\n    <p>O menu "Notas da Turma" mostra a Nota do Módulo e permite abrir o detalhamento de cada aluno, com Ex. 1 a Ex. 5, Quiz, Recuperação e identificação de toda substituição no formato nota original → nota considerada. As notas são calculadas automaticamente.</p><h4>Pendências</h4><p>A área "Pendências" reúne apenas situações que exigem atuação do professor, como cadastros incompletos e mensagens aguardando resposta. Exercícios, Quiz, Recuperação e notas não geram pendência de correção.</p><h4>Relatórios e Backup</h4><p>"Relatórios" apresenta o Relatório de Desempenho com resumo da turma, progresso e detalhamento por atividade, com CSV e impressão/PDF. "Backup" gera arquivo JSON das turmas e dados pedagógicos vinculados.</p>', 1)

# 15. Eventos para expandir detalhes do aluno
anchor = "    const exportGrades=document.getElementById('btn-export-grades'); if(exportGrades) exportGrades.addEventListener('click',()=>downloadText('notas_contabilidade_avancada.csv',gradesCsv(),'text/csv;charset=utf-8'));"
insert = """    document.querySelectorAll('[data-toggle-student-details]').forEach(btn=>btn.addEventListener('click',()=>{const idx=btn.getAttribute('data-toggle-student-details'), row=document.querySelector(`[data-student-detail=\"${idx}\"]`); if(!row)return; const open=row.style.display!=='none'; row.style.display=open?'none':'table-row'; btn.textContent=open?'Ver detalhes':'Ocultar detalhes';}));\n""" + anchor
if anchor not in s:
    raise SystemExit('Âncora de eventos de notas não encontrada')
s = s.replace(anchor, insert, 1)

p.write_text(s, encoding='utf-8')

# README: registrar novo fluxo sem depender de texto antigo
readme = Path('README.md')
r = readme.read_text(encoding='utf-8')
marker = '## Fluxo pedagógico automatizado'
if marker not in r:
    r += '''\n\n## Fluxo pedagógico automatizado\n\n- As 5 listas de exercícios, o Quiz e a Recuperação são autocorrigidos.\n- A Recuperação substitui individualmente todas as notas inferiores entre Ex. 1 a Ex. 5 e Quiz.\n- A Nota do Módulo é calculada automaticamente, sem envio ou aprovação manual pelo professor.\n- O módulo seguinte é liberado após a conclusão do conteúdo, das 5 listas e do Quiz do módulo anterior.\n- O painel do Professor apresenta Notas da Turma com detalhamento por atividade, Pendências operacionais e Relatório de Desempenho com resumo e detalhamento.\n- Exportação CSV e impressão/PDF utilizam o detalhamento das avaliações.\n'''
readme.write_text(r, encoding='utf-8')

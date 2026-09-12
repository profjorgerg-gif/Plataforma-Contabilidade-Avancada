from pathlib import Path
import re

p=Path('public/app.js')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s: raise SystemExit(f'Não encontrado: {label}')
    s=s.replace(old,new,1)

def sub(pattern,repl,label):
    global s
    new,n=re.subn(pattern,lambda m: repl,s,count=1,flags=re.S)
    if n!=1: raise SystemExit(f'Falha {label}: {n}')
    s=new

# Helpers: ciclo obrigatório = 5 listas + Quiz + Recuperação; leitura não bloqueia nota
sub(r"  function moduleReadyForSubmission\(mp, m\)\{.*?  function correctionBadge\(mp\)\{.*?\n  \}", r'''  function moduleReadyForSubmission(mp, m){
    return !!(mp && Array.isArray(mp.exerciseScores) && mp.exerciseScores.length >= m.exerciseLists.length && mp.exerciseScores.slice(0,m.exerciseLists.length).every(v => v !== null && v !== undefined) && mp.quizScore !== null && mp.quizScore !== undefined && mp.recoveryScore !== null && mp.recoveryScore !== undefined);
  }
  function moduleCompleted(mp){
    return !!(mp && Array.isArray(mp.exerciseScores) && mp.exerciseScores.slice(0,5).length === 5 && mp.exerciseScores.slice(0,5).every(v => v !== null && v !== undefined) && mp.quizScore !== null && mp.quizScore !== undefined && mp.recoveryScore !== null && mp.recoveryScore !== undefined);
  }
  function fmtGrade(v){ return (v === null || v === undefined || Number.isNaN(Number(v))) ? '—' : Number(v).toFixed(1).replace('.',','); }
  function moduleStatusLabel(mp){
    if (!moduleCompleted(mp)) return 'Em andamento';
    return correctionState(mp).released ? 'Concluído / Liberado' : 'Aguardando liberação';
  }
  function correctionBadge(mp){
    const done = moduleCompleted(mp), released = done && correctionState(mp).released;
    const cls = released ? 'ok' : (done ? 'info' : 'neutral');
    const label = released ? 'Concluído / Liberado' : (done ? 'Aguardando liberação' : 'Em andamento');
    return `<span class="status-badge ${cls}">${label}</span>`;
  }''','helpers')

# Progresso inclui recuperação
rep("const totalWeight = 1 /*content*/ + listsTotal + 1 /*quiz*/;","const totalWeight = 1 /*content*/ + listsTotal + 1 /*quiz*/ + 1 /*recuperação*/;",'peso progresso')
rep("if (mp.quizScore !== null && mp.quizScore !== undefined) score += 1;","if (mp.quizScore !== null && mp.quizScore !== undefined) score += 1;\n    if (mp.recoveryScore !== null && mp.recoveryScore !== undefined) score += 1;",'recuperação progresso')

# Liberação do próximo módulo depende de conclusão + decisão do professor
sub(r"    if\(idx>0\)\{ const prevModule=MODULES\[idx-1\], prev=state\.progress&&state\.progress\.modules\[prevModule\.id\]; if\(!moduleReadyForSubmission\(prev,prevModule\)\) return \{locked:true,reason:'[^']*'\}; \}","    if(idx>0){ const prevModule=MODULES[idx-1], prev=state.progress&&state.progress.modules[prevModule.id], pc=correctionState(prev); if(!moduleReadyForSubmission(prev,prevModule)) return {locked:true,reason:'Conclua as 5 listas, o Quiz e a Recuperação do módulo anterior.'}; if(!pc.released) return {locked:true,reason:'Aguarde a liberação do professor para avançar ao próximo módulo.'}; }",'liberação sequencial')

# Pendências: módulos completos e ainda não liberados
sub(r"    roster\.forEach\(st => MODULES\.forEach\(m => \{\n      const mp = st\.modules && st\.modules\[m\.id\]; const c = correctionState\(mp\);\n      if \(c\.status === 'em_correcao'\) modulosPendentes\.push\(\{ student:st, module:m, mp, correction:c \}\);\n    \}\)\);", "    roster.forEach(st => MODULES.forEach(m => {\n      const mp = st.modules && st.modules[m.id]; const c = correctionState(mp);\n      if (moduleReadyForSubmission(mp,m) && !c.released) modulosPendentes.push({ student:st, module:m, mp, correction:c });\n    }));",'carga pendências')

# Tela Pendências com liberação
sub(r"  function renderCorrecoesPendentes\(\)\{.*?\n    return html;\n  \}\n\n  function renderAcompanhamento", r'''  function renderCorrecoesPendentes(){
    const data = state.correcoesPendentes || { incompletos: [], mensagensPendentes: [], modulosPendentes: [] };
    let html = `<div class="section-title">Pendências</div>`;
    html += `<div class="note">Esta área reúne situações que exigem atuação do professor. As notas são calculadas automaticamente; a liberação do próximo módulo é uma decisão pedagógica individual do professor.</div>`;
    html += `<h4 style="margin:18px 0 8px">Alunos aguardando liberação de módulo (${data.modulosPendentes.length})</h4>`;
    if (!data.modulosPendentes.length) html += `<div class="empty-state">Nenhum aluno aguardando liberação no momento.</div>`;
    else data.modulosPendentes.forEach((it,idx)=>{ const next=MODULES.find(m=>m.num===it.module.num+1); html += `<div class="review-card"><div class="review-head"><div><b>${esc(it.student.name)}</b><div class="thread-preview">M${it.module.num} — ${esc(it.module.title)}</div></div><span class="status-badge info">Aguardando liberação</span></div><div class="review-grid"><div><span>Nota do Módulo</span><b>${fmtGrade(effectiveModuleGrade(it.mp))}</b></div><div><span>Próxima etapa</span><b>${next?'M'+next.num:'Conclusão da disciplina'}</b></div></div><div class="review-actions"><button class="btn-brass" data-release-module="${idx}">${next?'Liberar M'+next.num:'Concluir disciplina'}</button></div></div>`; });
    html += `<h4 style="margin:24px 0 8px">Cadastros a regularizar (${data.incompletos.length})</h4>`;
    if (!data.incompletos.length) html += `<div class="empty-state">Nenhum cadastro pendente no momento.</div>`;
    else data.incompletos.forEach(it=>{ html += `<div class="thread-row" data-fix-turma="${esc(it.turmaId)}"><div><b>${esc(it.nome||'(nome não identificado)')}</b><div class="thread-preview">Turma: ${esc(it.turmaNome||it.turmaName||'—')} · ${!it.nome?'Nome ausente · ':''}${!it.matricula?'Matrícula ausente':''}</div></div><span class="back-link">Regularizar →</span></div>`; });
    html += `<h4 style="margin:24px 0 8px">Mensagens aguardando resposta (${data.mensagensPendentes.length})</h4>`;
    if (!data.mensagensPendentes.length) html += `<div class="empty-state">Nenhuma mensagem pendente.</div>`;
    else data.mensagensPendentes.forEach(t=>{const last=t.messages[t.messages.length-1]; html += `<div class="thread-row" data-goto-thread="${esc(t.participantName)}"><div><b>${esc(t.participantName)}</b><div class="thread-preview">${esc(last.text.slice(0,70))}</div></div><span class="back-link">Responder →</span></div>`;});
    return html;
  }

  function renderAcompanhamento''','render pendências')

# Quiz/Recuperação: ao completar 7 etapas, aguarda liberação (não libera automaticamente)
sub(r"      if \(moduleReadyForSubmission\(activeMp,m\)\)\{.*?activeMp\.correction=c;\n      \}", r'''      if (moduleReadyForSubmission(activeMp,m)){
        const c = correctionState(activeMp); const now = Date.now();
        if (!c.firstSubmittedAt){
          const access = moduleAccess(m); c.firstSubmittedAt = now; c.late = !!access.late; c.latePenalty = access.late ? 2 : 0;
          c.history.push({type:'ciclo_avaliativo_concluido',ts:now,late:c.late,latePenalty:c.latePenalty});
        }
        c.status='aguardando_liberacao'; c.reviewedAt=null; c.released=false; c.finalGrade=effectiveModuleGrade(activeMp); activeMp.correction=c;
      }''','conclusão ciclo')

# Situação dentro do módulo
sub(r"    const corr = correctionState\(mp\);\n    html \+= `<div class=\"module-correction\"><h4>Situação do módulo</h4>.*?    html \+= `</div>`;\n", r'''    const corr = correctionState(mp);
    html += `<div class="module-correction"><h4>Situação do módulo</h4><div style="margin-bottom:8px">${correctionBadge(mp)}</div>`;
    if (corr.feedback) html += `<div class="feedback-box"><b>Registro anterior do professor:</b> ${esc(corr.feedback)}</div>`;
    if (moduleReadyForSubmission(mp,m) && corr.released) html += `<div class="quiz-score">Módulo concluído e liberado. Nota do Módulo: <b>${fmtGrade(effectiveModuleGrade(mp))} / 10,0</b></div><p class="thread-preview">O próximo módulo está liberado, respeitando o prazo definido pelo professor.</p>`;
    else if (moduleReadyForSubmission(mp,m)) html += `<div class="quiz-score">Ciclo avaliativo concluído. Nota do Módulo: <b>${fmtGrade(effectiveModuleGrade(mp))} / 10,0</b></div><p class="thread-preview">Aguarde a liberação individual do professor para avançar ao próximo módulo.</p>`;
    else html += `<p class="thread-preview">Para concluir o ciclo avaliativo, realize obrigatoriamente as 5 listas, o Quiz e a Recuperação. A leitura do conteúdo compõe o progresso de estudo, mas não bloqueia o cálculo da nota.</p>`;
    html += `</div>`;
''','situação módulo')

# Textos da recuperação e manuais principais
s=s.replace('A recuperação é uma avaliação paralela e não é uma 7ª nota da média.', 'A recuperação é obrigatória em todos os módulos e não é uma 7ª nota da média.', 1)
s=s.replace('Depois de concluir o conteúdo, as 5 listas e o Quiz, o sistema calcula automaticamente a Nota do Módulo e libera o módulo seguinte. Não há envio para correção manual. A Recuperação pode melhorar a nota ao substituir resultados inferiores.', 'Depois de realizar obrigatoriamente as 5 listas, o Quiz e a Recuperação, o sistema calcula automaticamente a Nota do Módulo. O próximo módulo permanece bloqueado até a liberação individual do professor. A leitura do conteúdo compõe o progresso de estudo, mas não impede o fechamento da nota.', 1)
s=s.replace('A área "Pendências" reúne apenas situações que exigem atuação do professor, como cadastros incompletos e mensagens aguardando resposta. Exercícios, Quiz, Recuperação e notas não geram pendência de correção.', 'A área "Pendências" reúne alunos que concluíram o ciclo avaliativo e aguardam liberação individual do próximo módulo, além de cadastros incompletos e mensagens aguardando resposta. As notas permanecem automáticas; o professor controla apenas a progressão pedagógica.', 1)
s=s.replace('Os demais são liberados automaticamente após a conclusão do conteúdo, das 5 listas e do Quiz do módulo anterior.', 'Os demais são liberados somente após a realização obrigatória das 5 listas, do Quiz e da Recuperação do módulo anterior e a liberação individual do professor.', 1)
s=s.replace('Listas, Quiz e Recuperação são autocorrigidos. A Recuperação substitui todas as notas inferiores entre as 6 atividades avaliativas. A Nota do Módulo é calculada automaticamente, sem etapa de aprovação manual.', 'Listas, Quiz e Recuperação são autocorrigidos e a Recuperação é obrigatória. Ela substitui todas as notas inferiores entre as 6 atividades avaliativas. A Nota do Módulo é calculada automaticamente; o professor não corrige a nota, mas libera individualmente a progressão para o módulo seguinte.', 1)
s=s.replace('Pendências reúne apenas cadastros a regularizar e mensagens aguardando resposta.', 'Pendências reúne alunos aguardando liberação de módulo, cadastros a regularizar e mensagens aguardando resposta.', 1)
s=s.replace('O estudante avança automaticamente após concluir o conteúdo, as cinco listas e o Quiz do módulo anterior.', 'O estudante conclui o ciclo avaliativo após realizar as cinco listas, o Quiz e a Recuperação obrigatória; o avanço ocorre somente após a liberação individual do professor.', 1)
s=s.replace('<li>Recuperação paralela autocorrigida;</li>', '<li>Recuperação obrigatória e autocorrigida;</li>', 1)
s=s.replace('Use Notas da Turma e Relatórios para acompanhar o desempenho detalhado; Pendências para cadastros e mensagens que exigem atuação;', 'Use Notas da Turma e Relatórios para acompanhar o desempenho detalhado; Pendências para liberar individualmente o avanço dos alunos, regularizar cadastros e responder mensagens;', 1)

# Minhas Notas: nota disponível só com ciclo completo; texto sobre liberação
s=s.replace('A <b>Nota do Módulo</b> é calculada automaticamente pelo sistema.', 'A <b>Nota do Módulo</b> é calculada automaticamente após as 5 listas, o Quiz e a Recuperação obrigatória; o avanço ao próximo módulo depende da liberação do professor.', 1)

# Handler de liberação individual antes dos links de pendências
marker="    // ---- Correções pendentes: jump to a turma or a pending support thread ----\n"
handler=r'''    document.querySelectorAll('[data-release-module]').forEach(btn=>{
      btn.addEventListener('click', async()=>{
        const idx=parseInt(btn.getAttribute('data-release-module'),10), it=(state.correcoesPendentes.modulosPendentes||[])[idx];
        if(!it) return;
        const c=correctionState(it.mp); const now=Date.now();
        c.status='corrigido'; c.released=true; c.reviewedAt=now; c.finalGrade=effectiveModuleGrade(it.mp);
        c.history.push({type:'liberacao_pedagogica',ts:now,by:state.user.name,grade:c.finalGrade});
        it.mp.correction=c;
        await saveProgress(it.student);
        await logAudit('modulo_liberado',`${state.user.name} liberou o avanço após o módulo "${it.module.title}" de ${it.student.name}. Nota do Módulo ${fmtGrade(c.finalGrade)}.`);
        await loadCorrecoesPendentes();
        render();
      });
    });

'''
if marker not in s: raise SystemExit('Marcador handlers não encontrado')
s=s.replace(marker,handler+marker,1)

# Status legado aceita aguardando liberação
s=s.replace("return ({ liberado:'Em desenvolvimento', em_correcao:'Enviado para correção', ajustes:'Ajustes solicitados', corrigido:'Corrigido' })[status] || 'Em desenvolvimento';","return ({ liberado:'Em desenvolvimento', em_correcao:'Enviado para correção', ajustes:'Ajustes solicitados', aguardando_liberacao:'Aguardando liberação', corrigido:'Concluído / Liberado' })[status] || 'Em desenvolvimento';",1)

p.write_text(s,encoding='utf-8')

# README
r=Path('README.md')
text=r.read_text(encoding='utf-8')
append='''\n\n## Fluxo de progressão pedagógica\n- Cada módulo exige obrigatoriamente 5 listas de exercícios, Quiz e Recuperação.\n- A Recuperação não é uma 7ª nota: substitui cada nota inferior entre os 5 exercícios e o Quiz.\n- A Nota do Módulo é calculada automaticamente após o ciclo avaliativo completo.\n- O próximo módulo permanece bloqueado até a liberação individual do professor.\n- A aba Pendências mostra os alunos que aguardam essa liberação, além de cadastros e mensagens pendentes.\n'''
if '## Fluxo de progressão pedagógica' not in text: text+=append
r.write_text(text,encoding='utf-8')

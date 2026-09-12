from pathlib import Path

path = Path('public/app.js')
s = path.read_text(encoding='utf-8')

old_helper = """  function exerciseAverage10(mp){
    if (!mp || !Array.isArray(mp.exerciseScores)) return null;
    const vals = mp.exerciseScores.filter(v => v !== null && v !== undefined).map(v => Number(v));
    if (!vals.length) return null;
    return Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*10)/10;
  }
"""
new_helper = """  function effectiveExerciseScores10(mp){
    if (!mp || !Array.isArray(mp.exerciseScores)) return [];
    const recovery = score10(mp.recoveryScore, mp.recoveryTotal || 10);
    return mp.exerciseScores.map(v => {
      if (v === null || v === undefined) return null;
      const original = Number(v);
      return recovery !== null && original < recovery ? recovery : original;
    });
  }
  function exerciseAverage10(mp){
    const vals = effectiveExerciseScores10(mp).filter(v => v !== null && v !== undefined);
    if (!vals.length) return null;
    return Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*10)/10;
  }
"""
if old_helper not in s:
    raise SystemExit('Bloco exerciseAverage10 não encontrado; atualização cancelada para evitar alteração incorreta.')
s = s.replace(old_helper, new_helper, 1)

marker_start = '  // ---- Minhas Notas (aluno) ----\n'
marker_end = '\n  // ---- Manual ----\n'
start = s.find(marker_start)
end = s.find(marker_end, start)
if start < 0 or end < 0:
    raise SystemExit('Bloco Minhas Notas não encontrado; atualização cancelada.')

new_notes = r'''  // ---- Minhas Notas (aluno) ----
  function renderMinhasNotas(){
    let html = `<div class="section-title">Minhas notas</div>`;
    html += `<div class="note">As 5 listas aparecem individualmente. Quando a <b>nota da Recuperação</b> for superior à nota de uma lista, ela <b>substitui a nota inferior</b> para efeito da média e da nota automática. As notas substituídas aparecem com <b>*</b>. A nota automática do módulo considera 50% da média das 5 listas já ajustadas e 50% do melhor resultado entre Quiz e Recuperação. A <b>Nota Final</b> só aparece como liberada após a revisão do professor.</div>`;
    html += `<div class="table-scroll"><table class="roster"><tr><th>Módulo</th><th class="num">Ex. 1</th><th class="num">Ex. 2</th><th class="num">Ex. 3</th><th class="num">Ex. 4</th><th class="num">Ex. 5</th><th class="num">Quiz</th><th class="num">Recup.</th><th class="num">Automática</th><th>Status</th><th class="num">Nota Final</th></tr>`;
    MODULES.forEach(m => {
      const mp = state.progress.modules[m.id]; const c=correctionState(mp);
      const quizTxt = score10(mp.quizScore,mp.quizTotal); const recTxt=score10(mp.recoveryScore,mp.recoveryTotal);
      const effectiveExercises = effectiveExerciseScores10(mp);
      const exerciseCells = Array.from({length:5}, (_,i) => {
        const original = Array.isArray(mp.exerciseScores) ? mp.exerciseScores[i] : null;
        const effective = effectiveExercises[i];
        const replaced = recTxt !== null && original !== null && original !== undefined && Number(original) < recTxt;
        if (effective === null || effective === undefined) return `<td class="num">—</td>`;
        const title = replaced ? ` title="Nota original ${fmtGrade(Number(original))} substituída pela recuperação ${fmtGrade(recTxt)}"` : '';
        return `<td class="num"><span${title}>${fmtGrade(effective)}${replaced?'*':''}</span></td>`;
      }).join('');
      html += `<tr><td>${esc(m.num+'. '+m.title)}</td>${exerciseCells}<td class="num">${fmtGrade(quizTxt)}</td><td class="num">${fmtGrade(recTxt)}</td><td class="num"><b>${fmtGrade(effectiveModuleGrade(mp))}</b></td><td>${correctionBadge(mp)}</td><td class="num"><b>${c.released?fmtGrade(c.finalGrade):'—'}</b></td></tr>`;
      if (c.feedback) html += `<tr><td colspan="11"><div class="feedback-box"><b>Feedback do professor:</b> ${esc(c.feedback)}</div></td></tr>`;
    });
    html += `</table></div>`;
    return html;
  }
'''
s = s[:start] + new_notes + s[end:]

old_student_manual = '<p>No menu superior, "Minhas Notas" mostra média das listas, quiz, recuperação, nota automática, situação da correção e Nota Final quando liberada pelo professor.</p>'
new_student_manual = '<p>No menu superior, "Minhas Notas" mostra a nota de cada uma das 5 listas, Quiz, Recuperação, nota automática, situação da correção e Nota Final quando liberada pelo professor. Quando a nota da Recuperação for superior à nota de uma lista, a Recuperação substitui aquela nota inferior para o cálculo da média e da nota automática; a substituição é identificada com *.</p>'
if old_student_manual in s:
    s = s.replace(old_student_manual, new_student_manual, 1)

old_prof_manual = '<p>O menu "Notas da Turma" mostra, por aluno e módulo, a nota automática, a Nota Final liberada e a situação da correção, com exportação em CSV e impressão/PDF.</p>'
new_prof_manual = '<p>O menu "Notas da Turma" mostra, por aluno e módulo, a nota automática, a Nota Final liberada e a situação da correção, com exportação em CSV e impressão/PDF. Na composição da nota automática, a Recuperação substitui individualmente toda nota de lista que seja inferior à nota obtida na Recuperação.</p>'
if old_prof_manual in s:
    s = s.replace(old_prof_manual, new_prof_manual, 1)

path.write_text(s, encoding='utf-8')

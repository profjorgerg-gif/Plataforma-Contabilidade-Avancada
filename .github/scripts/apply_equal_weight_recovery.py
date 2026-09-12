from pathlib import Path
import re

p = Path('public/app.js')
s = p.read_text(encoding='utf-8')

# 1) Regra de cálculo: 5 exercícios + quiz, todos com mesmo peso.
# A recuperação substitui somente a menor nota entre as 6, se for maior.
pattern = re.compile(r"  function effectiveExerciseScores10\(mp\)\{.*?(?=  function effectiveModuleGrade\(mp\)\{)", re.S)
new_block = """  function effectiveAssessmentScores10(mp){
    const exercises = Array.from({length:5}, (_,i) => {
      if (!mp || !Array.isArray(mp.exerciseScores)) return null;
      const v = mp.exerciseScores[i];
      return (v === null || v === undefined) ? null : Number(v);
    });
    const quiz = mp ? score10(mp.quizScore, mp.quizTotal || 10) : null;
    const values = [...exercises, quiz];
    const recovery = mp ? score10(mp.recoveryScore, mp.recoveryTotal || 10) : null;
    let replacedIndex = -1;

    if (recovery !== null){
      let lowest = Infinity;
      values.forEach((v,i) => {
        if (v !== null && v !== undefined && Number(v) < lowest){
          lowest = Number(v);
          replacedIndex = i;
        }
      });
      if (replacedIndex >= 0 && recovery > lowest) values[replacedIndex] = recovery;
      else replacedIndex = -1;
    }

    return { values, exercises: values.slice(0,5), quiz: values[5], recovery, replacedIndex };
  }
  function effectiveExerciseScores10(mp){
    return effectiveAssessmentScores10(mp).exercises;
  }
  function exerciseAverage10(mp){
    if (!mp || !Array.isArray(mp.exerciseScores)) return null;
    const vals = mp.exerciseScores.slice(0,5).filter(v => v !== null && v !== undefined).map(Number);
    if (!vals.length) return null;
    return Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*10)/10;
  }
  function baseAutomaticModuleGrade(mp){
    if (!mp) return null;
    const adjusted = effectiveAssessmentScores10(mp).values.filter(v => v !== null && v !== undefined).map(Number);
    if (!adjusted.length) return null;
    return Math.round((adjusted.reduce((a,b)=>a+b,0)/adjusted.length)*10)/10;
  }
"""
if not pattern.search(s):
    raise SystemExit('Bloco de cálculo não encontrado')
s = pattern.sub(new_block, s, count=1)

# 2) Tela Minhas Notas: marca somente a atividade efetivamente substituída, inclusive o Quiz.
old = """      const quizTxt = score10(mp.quizScore,mp.quizTotal); const recTxt=score10(mp.recoveryScore,mp.recoveryTotal);
      const effectiveExercises = effectiveExerciseScores10(mp);
      const exerciseCells = Array.from({length:5}, (_,i) => {
        const original = Array.isArray(mp.exerciseScores) ? mp.exerciseScores[i] : null;
        const effective = effectiveExercises[i];
        const replaced = recTxt !== null && original !== null && original !== undefined && Number(original) < recTxt;
        if (effective === null || effective === undefined) return `<td class=\"num\">—</td>`;
        const title = replaced ? ` title=\"Nota original ${fmtGrade(Number(original))} substituída pela recuperação ${fmtGrade(recTxt)}\"` : '';
        return `<td class=\"num\"><span${title}>${fmtGrade(effective)}${replaced?'*':''}</span></td>`;
      }).join('');
      html += `<tr><td>${esc(m.num+'. '+m.title)}</td>${exerciseCells}<td class=\"num\">${fmtGrade(quizTxt)}</td><td class=\"num\">${fmtGrade(recTxt)}</td><td class=\"num\"><b>${fmtGrade(effectiveModuleGrade(mp))}</b></td><td>${correctionBadge(mp)}</td><td class=\"num\"><b>${c.released?fmtGrade(c.finalGrade):'—'}</b></td></tr>`;
"""
new = """      const quizTxt = score10(mp.quizScore,mp.quizTotal); const recTxt=score10(mp.recoveryScore,mp.recoveryTotal);
      const adjusted = effectiveAssessmentScores10(mp);
      const exerciseCells = Array.from({length:5}, (_,i) => {
        const original = Array.isArray(mp.exerciseScores) ? mp.exerciseScores[i] : null;
        const effective = adjusted.exercises[i];
        const replaced = adjusted.replacedIndex === i;
        if (effective === null || effective === undefined) return `<td class=\"num\">—</td>`;
        const title = replaced ? ` title=\"Nota original ${fmtGrade(Number(original))} substituída pela recuperação ${fmtGrade(recTxt)}\"` : '';
        return `<td class=\"num\"><span${title}>${fmtGrade(effective)}${replaced?'*':''}</span></td>`;
      }).join('');
      const quizReplaced = adjusted.replacedIndex === 5;
      const quizTitle = quizReplaced ? ` title=\"Nota original ${fmtGrade(quizTxt)} substituída pela recuperação ${fmtGrade(recTxt)}\"` : '';
      const quizCell = adjusted.quiz === null || adjusted.quiz === undefined ? '—' : `<span${quizTitle}>${fmtGrade(adjusted.quiz)}${quizReplaced?'*':''}</span>`;
      html += `<tr><td>${esc(m.num+'. '+m.title)}</td>${exerciseCells}<td class=\"num\">${quizCell}</td><td class=\"num\">${fmtGrade(recTxt)}</td><td class=\"num\"><b>${fmtGrade(effectiveModuleGrade(mp))}</b></td><td>${correctionBadge(mp)}</td><td class=\"num\"><b>${c.released?fmtGrade(c.finalGrade):'—'}</b></td></tr>`;
"""
if old not in s:
    raise SystemExit('Bloco de Minhas Notas não encontrado')
s = s.replace(old, new, 1)

# 3) Textos de orientação e manuais.
repls = [
    (
      'As 5 listas aparecem individualmente. Quando a <b>nota da Recuperação</b> for superior à nota de uma lista, ela <b>substitui a nota inferior</b> para efeito da média e da nota automática. As notas substituídas aparecem com <b>*</b>. A nota automática do módulo considera 50% da média das 5 listas já ajustadas e 50% da nota do Quiz. A Recuperação não compõe a média diretamente; ela apenas substitui notas de listas que sejam inferiores à sua nota. A <b>Nota Final</b> só aparece como liberada após a revisão do professor.',
      'Os <b>5 exercícios e o Quiz valem 10,0 pontos cada</b> e têm o mesmo peso, formando uma média aritmética simples de 6 atividades avaliativas. A <b>Recuperação não é uma 7ª nota</b>: se sua nota for maior que a menor nota entre os 5 exercícios e o Quiz, ela substitui somente essa menor nota para compor a média. A atividade substituída aparece com <b>*</b>. A <b>Nota Final</b> só aparece como liberada após a revisão do professor.'
    ),
    (
      'A recuperação é uma avaliação paralela e não entra diretamente na média do módulo. Quando realizada, sua nota substitui, apenas para efeito de cálculo, as notas das listas de exercícios que forem inferiores a ela. O Quiz mantém sua própria nota e não é substituído pela Recuperação.',
      'A recuperação é uma avaliação paralela e não é uma 7ª nota da média. Os 5 exercícios e o Quiz valem 10,0 pontos cada e têm o mesmo peso. Se a nota da Recuperação for maior que a menor nota entre essas 6 atividades, ela substitui somente essa menor nota — inclusive se a menor nota for a do Quiz.'
    ),
    (
      '<li><b>Recuperação</b> — avaliação paralela que não entra diretamente na média. Sua nota substitui, para efeito de cálculo, cada nota das listas de exercícios que seja inferior a ela; o Quiz permanece independente.</li>',
      '<li><b>Recuperação</b> — avaliação paralela que não entra como 7ª nota. Se sua nota for maior que a menor nota entre os 5 exercícios e o Quiz, substitui somente essa menor nota para compor a média das 6 atividades.</li>'
    ),
    (
      '<p>No menu superior, "Minhas Notas" mostra a nota de cada uma das 5 listas, Quiz, Recuperação, nota automática, situação da correção e Nota Final quando liberada pelo professor. Quando a nota da Recuperação for superior à nota de uma lista, a Recuperação substitui aquela nota inferior para o cálculo da média e da nota automática; a substituição é identificada com *.</p>',
      '<p>No menu superior, "Minhas Notas" mostra as notas dos 5 exercícios, Quiz, Recuperação, média automática, situação da correção e Nota Final. Os 5 exercícios e o Quiz possuem o mesmo peso. A Recuperação substitui somente a menor nota entre essas 6 atividades quando for superior a ela; a substituição é identificada com * e pode ocorrer também no Quiz.</p>'
    ),
    (
      '<p>O menu "Notas da Turma" mostra, por aluno e módulo, a nota automática, a Nota Final liberada e a situação da correção, com exportação em CSV e impressão/PDF. Na composição da nota automática, a Recuperação substitui individualmente toda nota de lista que seja inferior à nota obtida na Recuperação.</p>',
      '<p>O menu "Notas da Turma" mostra, por aluno e módulo, a média automática, a Nota Final liberada e a situação da correção, com exportação em CSV e impressão/PDF. A média automática é a média aritmética simples dos 5 exercícios e do Quiz, todos com o mesmo peso. A Recuperação substitui somente a menor nota entre essas 6 atividades quando sua nota for superior.</p>'
    ),
    (
      '<div class="review-grid"><div><span>Média listas</span><b>${fmtGrade(exerciseAverage10(it.mp))}</b></div><div><span>Quiz</span><b>${fmtGrade(score10(it.mp.quizScore,it.mp.quizTotal))}</b></div><div><span>Recuperação</span><b>${fmtGrade(score10(it.mp.recoveryScore,it.mp.recoveryTotal))}</b></div><div><span>Nota automática</span><b>${fmtGrade(auto)}</b></div></div>',
      '<div class="review-grid"><div><span>Média dos 5 exercícios</span><b>${fmtGrade(exerciseAverage10(it.mp))}</b></div><div><span>Quiz</span><b>${fmtGrade(score10(it.mp.quizScore,it.mp.quizTotal))}</b></div><div><span>Recuperação</span><b>${fmtGrade(score10(it.mp.recoveryScore,it.mp.recoveryTotal))}</b></div><div><span>Média automática das 6 atividades</span><b>${fmtGrade(auto)}</b></div></div>'
    )
]
for old_text, new_text in repls:
    if old_text not in s:
        raise SystemExit('Texto esperado não encontrado: ' + old_text[:80])
    s = s.replace(old_text, new_text, 1)

p.write_text(s, encoding='utf-8')

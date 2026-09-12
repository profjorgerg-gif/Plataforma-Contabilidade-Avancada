from pathlib import Path

p = Path('public/app.js')
s = p.read_text(encoding='utf-8')

old_calc = """  function effectiveAssessmentScores10(mp){
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
"""
new_calc = """  function effectiveAssessmentScores10(mp){
    const originalExercises = Array.from({length:5}, (_,i) => {
      if (!mp || !Array.isArray(mp.exerciseScores)) return null;
      const v = mp.exerciseScores[i];
      return (v === null || v === undefined) ? null : Number(v);
    });
    const originalQuiz = mp ? score10(mp.quizScore, mp.quizTotal || 10) : null;
    const originalValues = [...originalExercises, originalQuiz];
    const recovery = mp ? score10(mp.recoveryScore, mp.recoveryTotal || 10) : null;
    const replaced = originalValues.map(v => recovery !== null && v !== null && v !== undefined && recovery > Number(v));
    const values = originalValues.map((v,i) => replaced[i] ? recovery : v);

    return {
      values,
      exercises: values.slice(0,5),
      quiz: values[5],
      recovery,
      replaced,
      originalValues,
      originalExercises,
      originalQuiz
    };
  }
"""
if old_calc not in s:
    raise SystemExit('Bloco de cálculo esperado não encontrado; atualização cancelada.')
s = s.replace(old_calc, new_calc, 1)

old_avg = """  function exerciseAverage10(mp){
    if (!mp || !Array.isArray(mp.exerciseScores)) return null;
    const vals = mp.exerciseScores.slice(0,5).filter(v => v !== null && v !== undefined).map(Number);
    if (!vals.length) return null;
    return Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*10)/10;
  }
"""
new_avg = """  function exerciseAverage10(mp){
    const vals = effectiveAssessmentScores10(mp).exercises.filter(v => v !== null && v !== undefined).map(Number);
    if (!vals.length) return null;
    return Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*10)/10;
  }
"""
if old_avg not in s:
    raise SystemExit('Bloco de média dos exercícios não encontrado; atualização cancelada.')
s = s.replace(old_avg, new_avg, 1)

old_note = 'Os <b>5 exercícios e o Quiz valem 10,0 pontos cada</b> e têm o mesmo peso, formando uma média aritmética simples de 6 atividades avaliativas. A <b>Recuperação não é uma 7ª nota</b>: se sua nota for maior que a menor nota entre os 5 exercícios e o Quiz, ela substitui somente essa menor nota para compor a média. A atividade substituída aparece com <b>*</b>. A <b>Nota Final</b> só aparece como liberada após a revisão do professor.'
new_note = 'Os <b>5 exercícios e o Quiz valem 10,0 pontos cada</b> e têm o mesmo peso, formando uma média aritmética simples de 6 atividades avaliativas. A <b>Recuperação não é uma 7ª nota</b>: sua nota é comparada individualmente com cada exercício e com o Quiz e, quando for superior, <b>substitui a nota inferior</b> para compor a média. Na tela aparece a <b>nota original → nota considerada</b> sempre que houver substituição. A <b>Nota Final</b> só aparece como liberada após a revisão do professor.'
if old_note not in s:
    raise SystemExit('Texto explicativo de Minhas Notas não encontrado.')
s = s.replace(old_note, new_note, 1)

old_ex = '''        const replaced = adjusted.replacedIndex === i;
        if (effective === null || effective === undefined) return `<td class="num">—</td>`;
        const title = replaced ? ` title="Nota original ${fmtGrade(Number(original))} substituída pela recuperação ${fmtGrade(recTxt)}"` : '';
        return `<td class="num"><span${title}>${fmtGrade(effective)}${replaced?'*':''}</span></td>`;
      }).join('');
      const quizReplaced = adjusted.replacedIndex === 5;
      const quizTitle = quizReplaced ? ` title="Nota original ${fmtGrade(quizTxt)} substituída pela recuperação ${fmtGrade(recTxt)}"` : '';
      const quizCell = adjusted.quiz === null || adjusted.quiz === undefined ? '—' : `<span${quizTitle}>${fmtGrade(adjusted.quiz)}${quizReplaced?'*':''}</span>`;
'''
new_ex = '''        const replaced = !!(adjusted.replaced && adjusted.replaced[i]);
        if (effective === null || effective === undefined) return `<td class="num">—</td>`;
        const title = replaced ? ` title="Nota original ${fmtGrade(Number(original))} substituída pela recuperação ${fmtGrade(recTxt)}"` : '';
        const shown = replaced ? `${fmtGrade(Number(original))} → <b>${fmtGrade(effective)}</b>` : fmtGrade(effective);
        return `<td class="num"><span${title}>${shown}</span></td>`;
      }).join('');
      const quizReplaced = !!(adjusted.replaced && adjusted.replaced[5]);
      const quizTitle = quizReplaced ? ` title="Nota original ${fmtGrade(quizTxt)} substituída pela recuperação ${fmtGrade(recTxt)}"` : '';
      const quizCell = adjusted.quiz === null || adjusted.quiz === undefined ? '—' : `<span${quizTitle}>${quizReplaced ? `${fmtGrade(quizTxt)} → <b>${fmtGrade(adjusted.quiz)}</b>` : fmtGrade(adjusted.quiz)}</span>`;
'''
if old_ex not in s:
    raise SystemExit('Bloco de exibição individual das notas não encontrado.')
s = s.replace(old_ex, new_ex, 1)

replacements = {
    '<li><b>Recuperação</b> — avaliação paralela que não entra como 7ª nota. Se sua nota for maior que a menor nota entre os 5 exercícios e o Quiz, substitui somente essa menor nota para compor a média das 6 atividades.</li>': '<li><b>Recuperação</b> — avaliação paralela que não entra como 7ª nota. Sua nota é comparada com cada um dos 5 exercícios e com o Quiz; sempre que for superior, substitui aquela nota inferior para compor a média das 6 atividades.</li>',
    '<p>No menu superior, "Minhas Notas" mostra as notas dos 5 exercícios, Quiz, Recuperação, média automática, situação da correção e Nota Final. Os 5 exercícios e o Quiz possuem o mesmo peso. A Recuperação substitui somente a menor nota entre essas 6 atividades quando for superior a ela; a substituição é identificada com * e pode ocorrer também no Quiz.</p>': '<p>No menu superior, "Minhas Notas" mostra as notas dos 5 exercícios, Quiz, Recuperação, média automática, situação da correção e Nota Final. Os 5 exercícios e o Quiz possuem o mesmo peso. A Recuperação substitui individualmente todas as notas dessas 6 atividades que forem inferiores à nota obtida na Recuperação. Quando houver substituição, a tela apresenta a nota original → nota considerada, inclusive no Quiz.</p>'
}
for old, new in replacements.items():
    if old not in s:
        raise SystemExit('Trecho do Manual do Aluno não encontrado: ' + old[:60])
    s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')

readme = Path('README.md')
r = readme.read_text(encoding='utf-8')
old_readme = 'A **nota automática do módulo** é calculada com 50% da média das 5 listas, já considerando eventuais substituições pela Recuperação, e 50% da nota do Quiz. A Recuperação não compõe a média diretamente: sua nota substitui, para efeito de cálculo, cada nota de lista que seja inferior à nota obtida na Recuperação. A Nota Final somente é considerada liberada quando o professor conclui a revisão do módulo.'
new_readme = 'A **nota automática do módulo** corresponde à média aritmética simples das 6 atividades avaliativas de mesmo peso: 5 listas de exercícios e Quiz. A Recuperação não é uma 7ª nota: sua nota é comparada individualmente com cada uma das 6 atividades e substitui, para efeito de cálculo, toda nota que seja inferior à nota obtida na Recuperação, inclusive a do Quiz. As notas originais permanecem preservadas e são exibidas ao lado das notas consideradas quando houver substituição. A Nota Final somente é considerada liberada quando o professor conclui a revisão do módulo.'
if old_readme not in r:
    raise SystemExit('Regra de nota no README não encontrada.')
r = r.replace(old_readme, new_readme, 1)
r = r.replace('3. Realiza o quiz e, quando houver Recuperação, a nota desta substitui individualmente as notas das listas que forem inferiores a ela para efeito do cálculo automático.', '3. Realiza o Quiz e, quando houver Recuperação, a nota desta substitui individualmente todas as notas inferiores entre os 5 exercícios e o próprio Quiz para efeito do cálculo automático.', 1)
r = r.replace('- indicação com `*` quando a nota exibida foi substituída pela nota da Recuperação;\n- nota do Quiz;', '- exibição da nota original e da nota considerada (`original → considerada`) quando houver substituição pela Recuperação;\n- nota do Quiz, também sujeita à substituição pela Recuperação quando for inferior;', 1)
readme.write_text(r, encoding='utf-8')

from pathlib import Path

p = Path('public/app.js')
s = p.read_text(encoding='utf-8')

old = """  function exerciseAverage10(mp){
    if (!mp || !Array.isArray(mp.exerciseScores)) return null;
    const vals = mp.exerciseScores.filter(v => v !== null && v !== undefined).map(v => Number(v));
    if (!vals.length) return null;
    return Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*10)/10;
  }
  function baseAutomaticModuleGrade(mp){
    if (!mp) return null;
    const ex = exerciseAverage10(mp);
    const q = score10(mp.quizScore, mp.quizTotal || 10);
    const r = score10(mp.recoveryScore, mp.recoveryTotal || 10);
    const avaliacao = r === null ? q : (q === null ? r : Math.max(q,r));
    if (ex === null && avaliacao === null) return null;
    if (ex === null) return avaliacao;
    if (avaliacao === null) return ex;
    return Math.round(((ex + avaliacao)/2)*10)/10;
  }
"""
new = """  function exerciseAverage10(mp){
    if (!mp || !Array.isArray(mp.exerciseScores)) return null;
    const recovery = score10(mp.recoveryScore, mp.recoveryTotal || 10);
    const vals = mp.exerciseScores
      .filter(v => v !== null && v !== undefined)
      .map(v => {
        const original = Number(v);
        return recovery !== null && recovery > original ? recovery : original;
      });
    if (!vals.length) return null;
    return Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*10)/10;
  }
  function baseAutomaticModuleGrade(mp){
    if (!mp) return null;
    const ex = exerciseAverage10(mp);
    const q = score10(mp.quizScore, mp.quizTotal || 10);
    if (ex === null && q === null) return null;
    if (ex === null) return q;
    if (q === null) return ex;
    return Math.round(((ex + q)/2)*10)/10;
  }
"""
if old not in s:
    raise SystemExit('Bloco de cálculo não encontrado')
s = s.replace(old, new, 1)

repls = [
    (
        'As listas e o quiz são autocorrigidos. A <b>nota automática do módulo</b> considera 50% da média das 5 listas e 50% do melhor resultado entre Quiz e Recuperação. A <b>Nota Final</b> só aparece como liberada após a revisão do professor.',
        'As listas e o quiz são autocorrigidos. A <b>nota automática do módulo</b> considera 50% da média das 5 listas e 50% da nota do Quiz. A <b>Recuperação não entra diretamente na média</b>: sua nota substitui, para efeito de cálculo, cada nota de lista que seja inferior a ela. As notas originais permanecem preservadas no histórico. A <b>Nota Final</b> só aparece como liberada após a revisão do professor.'
    ),
    ('<th class="num">Recup.</th>', '<th class="num">Recup. (substit.)</th>'),
    (
        'A recuperação é uma avaliação paralela, com questões diferentes do quiz principal. Pode ser feita a qualquer momento, como prática extra ou para tentar melhorar seu desempenho neste módulo.',
        'A recuperação é uma avaliação paralela e não entra diretamente na média do módulo. Quando realizada, sua nota substitui, apenas para efeito de cálculo, as notas das listas de exercícios que forem inferiores a ela. O Quiz mantém sua própria nota e não é substituído pela Recuperação.'
    ),
    (
        '<li><b>Recuperação</b> — avaliação paralela, com questões diferentes do quiz, que pode ser feita a qualquer momento como prática extra ou para tentar melhorar seu desempenho no módulo.</li>',
        '<li><b>Recuperação</b> — avaliação paralela que não entra diretamente na média. Sua nota substitui, para efeito de cálculo, cada nota das listas de exercícios que seja inferior a ela; o Quiz permanece independente.</li>'
    ),
    (
        '<p>No menu superior, "Minhas Notas" mostra média das listas, quiz, recuperação, nota automática, situação da correção e Nota Final quando liberada pelo professor.</p>',
        '<p>No menu superior, "Minhas Notas" mostra a média das listas já considerando eventuais substituições pela Recuperação, a nota do Quiz, a nota da Recuperação, a nota automática, a situação da correção e a Nota Final quando liberada pelo professor.</p>'
    ),
    (
        '<p>O menu "Notas da Turma" mostra, por aluno e módulo, a nota automática, a Nota Final liberada e a situação da correção, com exportação em CSV e impressão/PDF.</p>',
        '<p>O menu "Notas da Turma" mostra, por aluno e módulo, a nota automática, a Nota Final liberada e a situação da correção, com exportação em CSV e impressão/PDF. Na composição automática, a Recuperação não é somada à média: ela substitui as notas das listas que forem inferiores à nota obtida na Recuperação; o Quiz permanece independente.</p>'
    ),
]
for old_text, new_text in repls:
    if old_text in s:
        s = s.replace(old_text, new_text, 1)

p.write_text(s, encoding='utf-8')

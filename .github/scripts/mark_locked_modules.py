from pathlib import Path
p=Path('public/app.js')
s=p.read_text(encoding='utf-8')
old="""  function moduleStatusLabel(mp){
    if (!moduleCompleted(mp)) return 'Em andamento';
    return correctionState(mp).released ? 'Concluído / Liberado' : 'Aguardando liberação';
  }
"""
new="""  function moduleStatusLabel(mp, m){
    if (m){
      const access=moduleAccess(m);
      if (access.locked) return 'Bloqueado — aguardando liberação';
    }
    if (!moduleCompleted(mp)) return 'Em andamento';
    return correctionState(mp).released ? 'Concluído / Liberado' : 'Aguardando liberação';
  }
"""
if old not in s: raise SystemExit('helper não encontrado')
s=s.replace(old,new,1)
old="""      html += `<tr><td>${esc(m.num+'. '+m.title)}</td>${exerciseCells}<td class=\"num\">${quizCell}</td><td class=\"num\">${fmtGrade(recTxt)}</td><td class=\"num\"><b>${fmtGrade(grade)}</b></td><td>${moduleStatusLabel(mp)}</td></tr>`;
"""
new="""      const access=moduleAccess(m);
      const situation=access.locked ? `<span class=\"status-badge neutral\">Bloqueado</span><div class=\"cell-status\">Aguardando liberação do professor</div>` : moduleStatusLabel(mp,m);
      html += `<tr><td>${esc(m.num+'. '+m.title)}${access.locked?' <span class=\"status-badge neutral\">🔒 Bloqueado</span>':''}</td>${exerciseCells}<td class=\"num\">${quizCell}</td><td class=\"num\">${fmtGrade(recTxt)}</td><td class=\"num\"><b>${fmtGrade(grade)}</b></td><td>${situation}</td></tr>`;
"""
if old not in s: raise SystemExit('linha de notas não encontrada')
s=s.replace(old,new,1)
old="""          <h3>${esc(m.title)} ${access.locked?'<span class=\"status-badge neutral\">Bloqueado</span>':''}</h3>
"""
new="""          <h3>${esc(m.title)} ${access.locked?'<span class=\"status-badge neutral\">🔒 Bloqueado — aguardando liberação</span>':''}</h3>
"""
if old not in s: raise SystemExit('cartão bloqueado não encontrado')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

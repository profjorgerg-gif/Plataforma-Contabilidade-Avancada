from pathlib import Path
p=Path('public/app.js'); s=p.read_text(encoding='utf-8')
# Turmas: função de roteamento desapareceu, embora renderProfessor ainda a chame.
anchor="""  function renderTurmaList(){
"""
insert="""  function renderTurmasSection(){
    const turma = state.activeTurmaId ? (state.turmas || []).find(t => t.id === state.activeTurmaId) : null;
    if (state.activeTurmaId && !turma) state.activeTurmaId = null;
    return turma ? renderTurmaDetail(turma) : renderTurmaList();
  }

"""
if 'function renderTurmasSection(){' not in s:
    if anchor not in s: raise SystemExit('âncora Turmas não encontrada')
    s=s.replace(anchor,insert+anchor,1)
# Checklist: renderProfessor chama função inexistente. Restaura checklist operacional independente.
anchor2="""  const GUIA_PEDAGOGICO_MATERIAIS = {
"""
check="""  const STATUS_CHECKLIST = [
    ['CHK-001','Login Google e perfis de acesso','Implantado'],
    ['CHK-002','Aprovação de acesso do Professor','Implantado'],
    ['CHK-003','Cadastro e manutenção de Turmas','Implantado'],
    ['CHK-004','Cadastro/importação de alunos e matrícula','Implantado'],
    ['CHK-005','Prazos, atraso e bloqueio dos módulos','Implantado'],
    ['CHK-006','5 listas de exercícios por módulo','Implantado'],
    ['CHK-007','Quiz e Recuperação obrigatória','Implantado'],
    ['CHK-008','Cálculo automático e substituição pela Recuperação','Implantado'],
    ['CHK-009','Pendências e liberação pedagógica individual','Implantado'],
    ['CHK-010','Planejamento docente','Implantado'],
    ['CHK-011','Relatórios e exportação de notas','Implantado'],
    ['CHK-012','Suporte e chamados','Implantado'],
    ['CHK-013','Auditoria','Implantado'],
    ['CHK-014','Backup pedagógico e backup antes de sair','Implantado'],
    ['CHK-015','Manual Operacional e Checklist de Status','Implantado']
  ];
  function checklistCsv(){
    const rows=[['Código','Processo / Funcionalidade','Status'],...STATUS_CHECKLIST];
    return '\\ufeff'+rows.map(r=>r.map(csvEscape).join(';')).join('\\n');
  }
  function renderChecklistStatus(){
    return `<div class="section-title">Checklist de Status</div><div class="note">Conferência operacional das principais funcionalidades da plataforma Contabilidade Avançada.</div><div class="toolbar"><button class="btn-outline" id="btn-print-checklist">Imprimir / Salvar PDF</button><button class="btn-brass" id="btn-export-checklist">Exportar CSV</button></div><div class="table-scroll"><table class="roster"><tr><th>Código</th><th>Processo / Funcionalidade</th><th>Status</th></tr>${STATUS_CHECKLIST.map(r=>`<tr><td><b>${esc(r[0])}</b></td><td>${esc(r[1])}</td><td><span class="status-badge ok">${esc(r[2])}</span></td></tr>`).join('')}</table></div>`;
  }

"""
if 'function renderChecklistStatus(){' not in s:
    if anchor2 not in s: raise SystemExit('âncora Checklist não encontrada')
    s=s.replace(anchor2,check+anchor2,1)
# Handlers do checklist
needle="""    const printDoc=document.getElementById('btn-print-doc'); if(printDoc) printDoc.addEventListener('click',()=>window.print());
"""
handlers="""    const printChecklist=document.getElementById('btn-print-checklist'); if(printChecklist) printChecklist.addEventListener('click',()=>window.print());
    const exportChecklist=document.getElementById('btn-export-checklist'); if(exportChecklist) exportChecklist.addEventListener('click',()=>downloadText('checklist_status_contabilidade_avancada.csv',checklistCsv(),'text/csv;charset=utf-8'));
"""
if 'const printChecklist=document.getElementById' not in s:
    if needle not in s: raise SystemExit('âncora handlers não encontrada')
    s=s.replace(needle,needle+handlers,1)
p.write_text(s,encoding='utf-8')

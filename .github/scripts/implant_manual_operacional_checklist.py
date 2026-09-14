from pathlib import Path
p=Path('public/app.js')
s=p.read_text(encoding='utf-8')
marker='  function renderProfessor(){\n'
if marker not in s: raise SystemExit('renderProfessor marker not found')
block=r'''  // ---- Manual Operacional e Checklist de Status ----
  const OPERATIONAL_PROCESSES = [
    {id:'TELA-OP-001',title:'Acesso à plataforma',audience:'Professor / Aluno / Usuário Mestre',steps:['Acesse a plataforma pelo navegador.','Selecione o perfil correspondente no primeiro acesso.','Autentique-se com a conta Google.','Aluno: informe a matrícula quando solicitado. Professor: aguarde a aprovação do Usuário Mestre quando for o primeiro acesso.']},
    {id:'TELA-OP-002',title:'Aprovação de acesso do Professor',audience:'Usuário Mestre',steps:['Acesse Usuários.','Localize o cadastro com status Professor(a) — pendente.','Clique em Aprovar Professor.','Confirme que o perfil passou para Professor(a) ativo.']},
    {id:'TELA-OP-003',title:'Criação e manutenção de Turmas',audience:'Professor',steps:['Acesse Turmas.','Crie a turma e informe sua identificação.','Inclua alunos individualmente ou importe a lista em PDF.','Confira nome e matrícula antes de confirmar a inclusão.']},
    {id:'TELA-OP-004',title:'Definição de prazos e liberação dos módulos',audience:'Professor',steps:['Abra a turma desejada.','Defina o prazo de cada módulo.','Quando necessário, habilite a entrega em atraso.','Salve os prazos e acompanhe as liberações individuais.']},
    {id:'TELA-OP-005',title:'Realização das atividades do módulo',audience:'Aluno',steps:['Acesse o módulo liberado.','Estude o Conteúdo.','Realize sequencialmente as 5 listas de exercícios.','Conclua o Quiz e a Recuperação.','Aguarde a liberação do Professor para avançar ao módulo seguinte.']},
    {id:'TELA-OP-006',title:'Acompanhamento de notas e pendências',audience:'Professor',steps:['Acesse Notas da Turma para acompanhar o desempenho.','Use Ver detalhes para consultar as avaliações de cada módulo.','Acesse Pendências para localizar alunos aguardando liberação, cadastros incompletos e mensagens.','Efetue a liberação pedagógica quando cabível.']},
    {id:'TELA-OP-007',title:'Planejamento docente',audience:'Professor',steps:['Acesse Planejamento.','Mantenha os Cadastros de apoio atualizados.','Crie ou edite Planejamento Semestral e Plano de Aula.','Salve e utilize Imprimir / Salvar PDF quando necessário.']},
    {id:'TELA-OP-008',title:'Relatórios e exportação de notas',audience:'Professor',steps:['Acesse Relatórios.','Confira o resumo da turma e o detalhamento por atividade.','Use Imprimir / Salvar PDF para gerar o relatório visual.','Use Exportar CSV para obter os dados tabulares.']},
    {id:'TELA-OP-009',title:'Suporte e chamados',audience:'Todos os perfis',steps:['Acesse Suporte.','Selecione o canal disponível para seu perfil.','Registre a mensagem e acompanhe protocolo, status e prazo.','Quando autorizado, reabra o chamado dentro do período definido.']},
    {id:'TELA-OP-010',title:'Auditoria',audience:'Professor',steps:['Acesse Auditoria.','Consulte o histórico cronológico de eventos.','Alterne entre todos os eventos e somente acessos quando necessário.','Use os registros para conferência operacional.']},
    {id:'TELA-OP-011',title:'Backup manual',audience:'Professor',steps:['Acesse Backup.','Gere o arquivo de segurança quando desejar.','Armazene o arquivo em local seguro e identificado.','Utilize o backup como cópia complementar dos dados vinculados ao seu perfil.']},
    {id:'TELA-OP-012',title:'Backup antes de sair',audience:'Usuário autenticado',steps:['Clique em Sair.','No aviso de backup, escolha Sim, baixar backup e sair para gerar o arquivo.','Se não desejar gerar a cópia, escolha Sair sem backup.','Use Cancelar para permanecer conectado.']}
  ];
  function screenshotPlaceholder(id){
    return `<div style="border:2px dashed #9aa7b8;border-radius:10px;padding:24px 16px;margin:14px 0;background:#f8fafc;text-align:center;color:#52657a"><div style="font-size:28px;margin-bottom:8px">▧</div><b>TELA A INCLUIR — ${esc(id)}</b><div style="font-size:12px;margin-top:5px">Inserir posteriormente a captura de tela correspondente a esta identificação.</div></div>`;
  }
  function renderManualOperacional(){
    let html=`<div class="section-title">Manual de Operacionalização</div><div class="note"><b>Documento independente.</b> Este manual descreve os principais processos e procedimentos de utilização da plataforma. Cada procedimento possui uma identificação exclusiva para a futura inclusão da respectiva captura de tela.</div><div class="toolbar"><button class="btn-brass" id="btn-print-operational">Imprimir / Salvar PDF</button></div>`;
    OPERATIONAL_PROCESSES.forEach((x,i)=>{html+=`<div class="card-box operational-process"><div class="review-head"><div><span class="status-badge info">${esc(x.id)}</span><h4 style="margin:8px 0 2px">${i+1}. ${esc(x.title)}</h4><div class="thread-preview">Perfil: ${esc(x.audience)}</div></div></div><ol style="line-height:1.65;padding-left:22px">${x.steps.map(st=>`<li>${esc(st)}</li>`).join('')}</ol>${screenshotPlaceholder(x.id)}</div>`;});
    return html;
  }
  const STATUS_CHECKLIST = [
    ['CHK-001','Login com Google e controle de perfil','Implantado'],['CHK-002','Aprovação prévia de acesso do Professor','Implantado'],['CHK-003','Cadastro e importação de alunos por turma','Implantado'],['CHK-004','Prazos, atraso e liberação dos módulos','Implantado'],['CHK-005','5 listas, Quiz e Recuperação por módulo','Implantado'],['CHK-006','Notas da Turma e detalhamento das avaliações','Implantado'],['CHK-007','Pendências e liberação pedagógica','Implantado'],['CHK-008','Planejamento Semestral e Plano de Aula','Implantado'],['CHK-009','Relatórios com PDF e CSV','Implantado'],['CHK-010','Suporte com protocolo e status','Implantado'],['CHK-011','Auditoria de acessos e ações','Implantado'],['CHK-012','Backup manual e backup opcional ao sair','Implantado'],['CHK-013','Manual de Operacionalização independente','Implantado'],['CHK-014','Identificação de tela em cada procedimento do manual','Implantado'],['CHK-015','Checklist de Status independente','Implantado']
  ];
  function checklistCsv(){return '\ufeff'+[['Código','Processo / Recurso','Status'],...STATUS_CHECKLIST].map(r=>r.map(csvEscape).join(';')).join('\n');}
  function renderChecklistStatus(){
    let html=`<div class="section-title">Checklist de Status</div><div class="note"><b>Área independente.</b> Quadro de conferência dos principais recursos e processos previstos para a plataforma. Utilize-o como referência de validação operacional após atualizações.</div><div class="toolbar"><button class="btn-outline" id="btn-print-checklist">Imprimir / Salvar PDF</button><button class="btn-brass" id="btn-export-checklist">Exportar CSV</button></div><div class="table-scroll"><table class="roster"><tr><th>Código</th><th>Processo / Recurso</th><th>Status</th></tr>`;
    STATUS_CHECKLIST.forEach(r=>{html+=`<tr><td><b>${esc(r[0])}</b></td><td>${esc(r[1])}</td><td><span class="status-badge ok">✓ ${esc(r[2])}</span></td></tr>`;});
    return html+`</table></div>`;
  }

'''
s=s.replace(marker,block+marker,1)
# handlers
hmarker='    // ---- Planejamento docente ----\n'
handlers=r'''    const printOperational=document.getElementById('btn-print-operational'); if(printOperational) printOperational.addEventListener('click',()=>window.print());
    const printChecklist=document.getElementById('btn-print-checklist'); if(printChecklist) printChecklist.addEventListener('click',()=>window.print());
    const exportChecklist=document.getElementById('btn-export-checklist'); if(exportChecklist) exportChecklist.addEventListener('click',()=>downloadText('checklist_status_contabilidade_avancada.csv',checklistCsv(),'text/csv;charset=utf-8'));

'''
if hmarker not in s: raise SystemExit('handler marker not found')
s=s.replace(hmarker,handlers+hmarker,1)
p.write_text(s,encoding='utf-8')

# Update README with operational documentation note
rp=Path('README.md')
r=rp.read_text(encoding='utf-8')
section='''\n\n## Manual de Operacionalização e Checklist de Status\n\nA área do Professor possui telas independentes de **Manual Operacional** e **Checklist de Status**. O Manual Operacional identifica cada processo/procedimento com um código `TELA-OP-XXX` e reserva, em cada item, um espaço próprio para inclusão posterior da captura de tela correspondente. O Checklist de Status possui estrutura própria e exportação em PDF/CSV para conferência operacional.\n'''
if '## Manual de Operacionalização e Checklist de Status' not in r:
    rp.write_text(r.rstrip()+section+'\n',encoding='utf-8')

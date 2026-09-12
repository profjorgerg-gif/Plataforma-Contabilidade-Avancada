from pathlib import Path

p=Path('public/app.js')
s=p.read_text(encoding='utf-8')

# 1. Estado do planejamento
old="""    studentTurma: null,
    accessAuditOnly: false
  };"""
new="""    studentTurma: null,
    accessAuditOnly: false,

    // ---- Planejamento docente ----
    planningSubtab: 'semester', // semester | lesson
    planningRecords: { semester: [], lesson: [] },
    planningEditing: null,
    planningMessage: ''
  };"""
if old not in s: raise SystemExit('anchor state não encontrado')
s=s.replace(old,new,1)

# 2. Funções de persistência/renderização antes das pendências
anchor="""  // ---- Correções pendentes (professor) ----
"""
if anchor not in s: raise SystemExit('anchor planning functions não encontrado')
block=r'''  // ---- Planejamento docente (professor) ----
  function planningOwnerKey(){
    return (state.user && state.user.uid) ? state.user.uid : encodeURIComponent((state.user && state.user.name) || 'professor');
  }
  function planningPrefix(type){ return `planning:${planningOwnerKey()}:${type}:`; }
  function newPlanningId(type){ return `${type}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,7)}`; }
  async function loadPlanningType(type){
    const out=[];
    try{
      const list=await kvList(planningPrefix(type));
      for(const k of (list&&list.keys)||[]){
        try{ const r=await kvGet(k); if(r&&r.value) out.push(JSON.parse(r.value)); }catch(e){}
      }
    }catch(e){}
    out.sort((a,b)=>(b.updatedAt||b.createdAt||0)-(a.updatedAt||a.createdAt||0));
    state.planningRecords[type]=out;
    return out;
  }
  async function loadPlanningAll(){ await Promise.all([loadPlanningType('semester'),loadPlanningType('lesson')]); }
  async function savePlanningRecord(type,rec){
    rec.type=type; rec.professor=rec.professor||state.user.name; rec.professorUid=planningOwnerKey(); rec.updatedAt=Date.now();
    if(!rec.createdAt) rec.createdAt=rec.updatedAt;
    await kvSet(planningPrefix(type)+rec.id,JSON.stringify(rec));
  }
  function planningDefaults(type){
    if(type==='semester') return {
      id:newPlanningId(type),curso:'TÉCNICO EM CONTABILIDADE',disciplina:'CONTABILIDADE AVANÇADA',modulo:'',turma:'',professor:state.user.name,nAulas:'2',periodo:String(new Date().getFullYear()),
      ementa:'Contabilização da Provisão da Folha de Pagamento: Salário, Férias, 13º Salário, Rescisão; Apuração do Resultado do Exercício: LALUR, Participações e Destinações do Resultado do Exercício; Participações, Destinações, Reservas, Reserva de Lucros, Dividendos; Declaração de Ajuste Anual do Imposto de Renda Pessoa Física, Apuração do Ganho de Capital da Pessoa Física;',
      habilidades:'Estudar as demonstrações contábeis obrigatórias. Compreender sobre a apuração e recolhimento. Adquirir noção de obrigações legais da área.',
      basesTecnologicas:'',objetoConhecimento:'Contabilização da Provisão da Folha de Pagamento: Salário, Férias, 13º Salário, Rescisão; Apuração do Resultado do Exercício: LALUR, Participações e Destinações do Resultado do Exercício; Participações, Destinações, Reservas, Reserva de Lucros, Dividendos; Declaração de Ajuste Anual do Imposto de Renda Pessoa Física, Apuração do Ganho de Capital da Pessoa Física;',
      metodologia:'Sala de Aula Invertida – uso de materiais digitais e prática presencial.\nAprendizagem Baseada em Problemas (PBL) – resolução de casos reais.\nGrupos Operativos – trabalhos colaborativos com foco em competências socioemocionais.\nAbordagem Inclusiva – estratégias adaptadas às necessidades dos estudantes.',
      recursos:'QUADRO, SLIDES, IMPRESSOS',instrumentosAvaliacao:'Estudos de caso: resolução de problemas reais ou fictícios; pode envolver escrita, discussão e proposição de soluções.\nResolução de Exercícios: atividades individuais que consolidam os conceitos abordados, incentivando a organização de ideias e o raciocínio lógico.',
      datasAvaliacoes:'Por se tratar de um Curso Técnico Pós-Médio, os prazos para realização e entrega das atividades são definidos de acordo com o andamento do conteúdo programático e o desenvolvimento da turma.',
      recuperacaoParalela:'Art. 6º Portaria Nº 874 de 01/04/2025. A recuperação paralela constitui nova oportunidade de aprendizagem e avaliação. Deve ser ofertada a todos os estudantes e prevalece o maior resultado obtido.',
      adaptacoes:'As adaptações e adequações curriculares serão realizadas conforme as necessidades educacionais dos estudantes, respeitando os princípios da educação inclusiva.',referencias:'',localData:'Blumenau'
    };
    return {
      id:newPlanningId(type),dataInicio:'',dataFim:'',professor:state.user.name,areaConhecimento:'EIXO GESTÃO & NEGÓCIOS',turma:'',nAulasSemanais:'2',componenteCurricular:'CONTABILIDADE AVANÇADA',
      objetosConhecimento:'Contabilização da Provisão da Folha de Pagamento: Salário, Férias, 13º Salário, Rescisão; Apuração do Resultado do Exercício: LALUR, Participações e Destinações do Resultado do Exercício; Participações, Destinações, Reservas, Reserva de Lucros, Dividendos; Declaração de Ajuste Anual do Imposto de Renda Pessoa Física, Apuração do Ganho de Capital da Pessoa Física;',
      habilidades:'Estudar as demonstrações contábeis obrigatórias. Compreender sobre a apuração e recolhimento. Adquirir noção de obrigações legais da área.',objetivoAprendizagem:'',
      metodologia:'Sala de Aula Invertida – uso de materiais digitais e prática presencial.\nAprendizagem Baseada em Problemas (PBL) – resolução de casos reais.\nGrupos Operativos – trabalhos colaborativos com foco em competências socioemocionais.\nAbordagem Inclusiva – estratégias adaptadas às necessidades dos estudantes.',recursos:'QUADRO, SLIDES, IMPRESSOS',
      instrumentosAvaliacao:'Estudos de caso e resolução de exercícios.',datasAvaliacoes:'',recuperacaoParalela:'Art. 6º Portaria Nº 874 de 01/04/2025. A recuperação paralela constitui nova oportunidade de aprendizagem e avaliação, prevalecendo o maior resultado obtido.',adaptacoes:'',referencias:''
    };
  }
  function planningField(name,label,value,kind='text',required=false){
    const req=required?' required':''; const v=value===null||value===undefined?'':String(value);
    if(kind==='textarea') return `<div style="grid-column:1/-1"><label>${esc(label)}</label><textarea name="${esc(name)}" rows="5"${req}>${esc(v)}</textarea></div>`;
    return `<div><label>${esc(label)}</label><input name="${esc(name)}" type="${kind}" value="${esc(v)}"${req}></div>`;
  }
  function renderPlanningForm(type,rec){
    let fields='';
    if(type==='semester'){
      fields+=planningField('periodo','Período/Ano',rec.periodo,'text',true)+planningField('curso','Curso',rec.curso,'text',true)+planningField('disciplina','Disciplina',rec.disciplina,'text',true)+planningField('modulo','Módulo',rec.modulo)+planningField('turma','Turma',rec.turma,'text',true)+planningField('professor','Professor',rec.professor,'text',true)+planningField('nAulas','Nº de aulas',rec.nAulas);
      fields+=planningField('ementa','Ementa',rec.ementa,'textarea')+planningField('habilidades','Habilidades',rec.habilidades,'textarea')+planningField('basesTecnologicas','Bases Tecnológicas / Conteúdos por unidade',rec.basesTecnologicas,'textarea')+planningField('objetoConhecimento','Objeto do Conhecimento',rec.objetoConhecimento,'textarea')+planningField('metodologia','Metodologia de Ensino-Aprendizagem',rec.metodologia,'textarea')+planningField('recursos','Recursos Utilizados',rec.recursos,'textarea')+planningField('instrumentosAvaliacao','Instrumentos Diversificados de Avaliação',rec.instrumentosAvaliacao,'textarea')+planningField('datasAvaliacoes','Datas Previstas de Avaliações e Recuperações',rec.datasAvaliacoes,'textarea')+planningField('recuperacaoParalela','Recuperação Paralela de Aprendizagem',rec.recuperacaoParalela,'textarea')+planningField('adaptacoes','Adaptações e Observações',rec.adaptacoes,'textarea')+planningField('referencias','Referências Bibliográficas',rec.referencias,'textarea')+planningField('localData','Local',rec.localData);
    }else{
      fields+=planningField('dataInicio','Data de início',rec.dataInicio,'date',true)+planningField('dataFim','Data de fim',rec.dataFim,'date',true)+planningField('professor','Professor',rec.professor,'text',true)+planningField('areaConhecimento','Área(s) do Conhecimento',rec.areaConhecimento,'text',true)+planningField('turma','Turma(s)',rec.turma,'text',true)+planningField('nAulasSemanais','Nº de aulas semanais',rec.nAulasSemanais)+planningField('componenteCurricular','Componente Curricular',rec.componenteCurricular,'text',true);
      fields+=planningField('objetosConhecimento','Objetos de Conhecimento',rec.objetosConhecimento,'textarea')+planningField('habilidades','Habilidades',rec.habilidades,'textarea')+planningField('objetivoAprendizagem','Objetivo de Aprendizagem',rec.objetivoAprendizagem,'textarea')+planningField('metodologia','Metodologia de Ensino-Aprendizagem',rec.metodologia,'textarea')+planningField('recursos','Recursos Utilizados',rec.recursos,'textarea')+planningField('instrumentosAvaliacao','Instrumentos Diversificados de Avaliação',rec.instrumentosAvaliacao,'textarea')+planningField('datasAvaliacoes','Datas Previstas de Avaliações e Recuperações',rec.datasAvaliacoes,'textarea')+planningField('recuperacaoParalela','Recuperação Paralela de Aprendizagem',rec.recuperacaoParalela,'textarea')+planningField('adaptacoes','Adaptações e Observações',rec.adaptacoes,'textarea')+planningField('referencias','Referências Bibliográficas',rec.referencias,'textarea');
    }
    const title=type==='semester'?'Planejamento Semestral':'Plano de Aula';
    return `<div class="card-box"><h4>${esc(title)} — ${rec.createdAt?'Editar':'Novo'}</h4>${type==='lesson'?'<div class="note">A periodicidade do Plano de Aula é de no máximo 30 dias. Planos da mesma turma não podem ter períodos sobrepostos.</div>':''}<form id="planning-form" data-planning-type="${type}" data-planning-id="${esc(rec.id)}"><div class="support-controls" style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;align-items:start">${fields}</div><div class="toolbar" style="margin-top:16px"><button class="btn-brass" type="submit">Salvar planejamento</button><button class="btn-outline" type="button" id="btn-cancel-planning">Cancelar</button></div></form></div>`;
  }
  function planningDateBR(v){ if(!v)return '—'; const [y,m,d]=String(v).split('-'); return y&&m&&d?`${d}/${m}/${y}`:v; }
  function planningPrintRows(type,r){
    const rows=type==='semester' ? [
      ['Curso',r.curso],['Disciplina',r.disciplina],['Módulo',r.modulo],['Turma',r.turma],['Professor',r.professor],['Nº aulas',r.nAulas],['EMENTA',r.ementa],['HABILIDADES',r.habilidades],['BASES TECNOLÓGICAS / Conteúdos por unidade',r.basesTecnologicas],['OBJETO DO CONHECIMENTO',r.objetoConhecimento],['METODOLOGIA DE ENSINO APRENDIZAGEM',r.metodologia],['RECURSOS UTILIZADOS',r.recursos],['INSTRUMENTOS DIVERSIFICADOS DE AVALIAÇÃO',r.instrumentosAvaliacao],['DATAS PREVISTAS DE AVALIAÇÕES E RECUPERAÇÕES',r.datasAvaliacoes],['RECUPERAÇÃO PARALELA DE APRENDIZAGEM',r.recuperacaoParalela],['ADAPTAÇÕES E OBSERVAÇÕES',r.adaptacoes],['REFERÊNCIAS BIBLIOGRÁFICAS',r.referencias]
    ] : [
      ['Período',`${planningDateBR(r.dataInicio)} a ${planningDateBR(r.dataFim)}`],['Professor(a)',r.professor],['Área(s) do Conhecimento',r.areaConhecimento],['Turma(s)',r.turma],['Nº aulas semanais',r.nAulasSemanais],['COMPONENTE CURRICULAR',r.componenteCurricular],['OBJETOS DE CONHECIMENTO',r.objetosConhecimento],['HABILIDADES',r.habilidades],['OBJETIVO DE APRENDIZAGEM',r.objetivoAprendizagem],['METODOLOGIA DE ENSINO APRENDIZAGEM',r.metodologia],['RECURSOS UTILIZADOS',r.recursos],['INSTRUMENTOS DIVERSIFICADOS DE AVALIAÇÃO',r.instrumentosAvaliacao],['DATAS PREVISTAS DE AVALIAÇÕES E RECUPERAÇÕES',r.datasAvaliacoes],['RECUPERAÇÃO PARALELA DE APRENDIZAGEM',r.recuperacaoParalela],['ADAPTAÇÕES E OBSERVAÇÕES',r.adaptacoes],['REFERÊNCIAS BIBLIOGRÁFICAS',r.referencias]
    ];
    return rows.map(([a,b])=>`<tr><th>${esc(a)}</th><td>${esc(b||'').replace(/\n/g,'<br>')}</td></tr>`).join('');
  }
  function printPlanningRecord(type,r){
    const title=type==='semester'?`PLANO SEMESTRAL PÓS MÉDIO — ${r.periodo||''}`:`SEQUÊNCIA DIDÁTICA / PLANO DE AULA — ${planningDateBR(r.dataInicio)} a ${planningDateBR(r.dataFim)}`;
    const w=window.open('','_blank'); if(!w)return alert('Permita pop-ups para imprimir/salvar o planejamento em PDF.');
    w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title><style>body{font-family:Arial,sans-serif;color:#111;margin:24px}h1,h2,p{text-align:center}h1{font-size:15px;margin:0}h2{font-size:16px;margin:12px 0}table{width:100%;border-collapse:collapse;font-size:12px}th,td{border:1px solid #333;padding:8px;vertical-align:top}th{width:25%;background:#f2d0ad;text-align:left}td{white-space:normal;line-height:1.45}@media print{body{margin:8mm}button{display:none}}</style></head><body><h1>ESTADO DE SANTA CATARINA<br>SECRETARIA DE ESTADO DA EDUCAÇÃO<br>CEDUP – CENTRO DE EDUCAÇÃO PROFISSIONAL HERMANN HERING</h1><h2>${esc(title)}</h2><table>${planningPrintRows(type,r)}</table><p style="text-align:left;margin-top:16px">Blumenau, ${new Date().toLocaleDateString('pt-BR')}.</p><script>window.onload=()=>window.print()<\/script></body></html>`); w.document.close();
  }
  function renderPlanning(){
    const type=state.planningSubtab||'semester', records=(state.planningRecords&&state.planningRecords[type])||[];
    let html=`<div class="section-title">Planejamento</div><div class="note">Elabore, salve e imprima os planejamentos pedagógicos conforme os modelos institucionais do CEDUP Hermann Hering.</div><div class="ptabs"><div class="ptab ${type==='semester'?'active':''}" data-planning-tab="semester">Planejamento Semestral</div><div class="ptab ${type==='lesson'?'active':''}" data-planning-tab="lesson">Plano de Aula</div></div>`;
    if(state.planningMessage) html+=`<div class="note">${esc(state.planningMessage)}</div>`;
    if(state.planningEditing) return html+renderPlanningForm(type,state.planningEditing);
    html+=`<div class="toolbar"><button class="btn-brass" id="btn-new-planning">${type==='semester'?'Novo Planejamento Semestral':'Novo Plano de Aula'}</button></div>`;
    if(!records.length) return html+`<div class="empty-state">Nenhum ${type==='semester'?'planejamento semestral':'plano de aula'} salvo.</div>`;
    records.forEach(r=>{
      const title=type==='semester'?`${r.turma||'Turma não informada'} · ${r.periodo||''}`:`${r.turma||'Turma não informada'} · ${planningDateBR(r.dataInicio)} a ${planningDateBR(r.dataFim)}`;
      html+=`<div class="review-card"><div class="review-head"><div><b>${esc(title)}</b><div class="thread-preview">${esc(type==='semester'?(r.disciplina||'CONTABILIDADE AVANÇADA'):(r.componenteCurricular||'CONTABILIDADE AVANÇADA'))}</div></div><span class="status-badge ok">Salvo</span></div><div class="review-actions"><button class="btn-outline" data-edit-planning="${esc(r.id)}">Editar</button><button class="btn-brass" data-print-planning="${esc(r.id)}">Imprimir / Salvar PDF</button></div></div>`;
    });
    return html;
  }
'''
s=s.replace(anchor,block+'\n'+anchor,1)

# 3. Menu professor
old="""    else if (role === 'professor') items = [['professor:turmas','Turmas'],['professor:acompanhamento','Notas da Turma'],['professor:correcoes','Pendências'],['professor:relatorios','Relatórios'],['professor:backup','Backup'],['professor:auditoria','Auditoria'],['professor:operacional','Manual Operacional'],['professor:checklist','Checklist'],['professor:guia','Guia Pedagógico'],['manual','Manual do Professor'],['suporte','Suporte']];"""
new="""    else if (role === 'professor') items = [['professor:turmas','Turmas'],['professor:planejamento','Planejamento'],['professor:acompanhamento','Notas da Turma'],['professor:correcoes','Pendências'],['professor:relatorios','Relatórios'],['professor:backup','Backup'],['professor:auditoria','Auditoria'],['professor:operacional','Manual Operacional'],['professor:checklist','Checklist'],['professor:guia','Guia Pedagógico'],['manual','Manual do Professor'],['suporte','Suporte']];"""
if old not in s: raise SystemExit('menu professor não encontrado')
s=s.replace(old,new,1)

# 4. Render professor
old="""    if (state.professorTab === 'turmas') return renderTurmasSection();
    if (state.professorTab === 'auditoria') return renderAuditoria();"""
new="""    if (state.professorTab === 'turmas') return renderTurmasSection();
    if (state.professorTab === 'planejamento') return renderPlanning();
    if (state.professorTab === 'auditoria') return renderAuditoria();"""
if old not in s: raise SystemExit('render professor anchor não encontrado')
s=s.replace(old,new,1)

# 5. Carregar ao abrir o menu
old="""          if (tab === 'auditoria') await loadAuditoria();
          else if (tab === 'correcoes') await loadCorrecoesPendentes();"""
new="""          if (tab === 'auditoria') await loadAuditoria();
          else if (tab === 'correcoes') await loadCorrecoesPendentes();
          else if (tab === 'planejamento') await loadPlanningAll();"""
if old not in s: raise SystemExit('handler nav não encontrado')
s=s.replace(old,new,1)

# 6. Handlers de planejamento antes do suporte tabs
anchor="""    // ---- Suporte: tabs, inbox, conversation ----
"""
if anchor not in s: raise SystemExit('handler planning anchor não encontrado')
handlers=r'''    // ---- Planejamento docente ----
    document.querySelectorAll('[data-planning-tab]').forEach(el=>el.addEventListener('click',async()=>{
      state.planningSubtab=el.getAttribute('data-planning-tab'); state.planningEditing=null; state.planningMessage=''; await loadPlanningType(state.planningSubtab); render();
    }));
    const newPlanning=document.getElementById('btn-new-planning'); if(newPlanning) newPlanning.addEventListener('click',()=>{state.planningEditing=planningDefaults(state.planningSubtab);state.planningMessage='';render();});
    const cancelPlanning=document.getElementById('btn-cancel-planning'); if(cancelPlanning) cancelPlanning.addEventListener('click',()=>{state.planningEditing=null;state.planningMessage='';render();});
    document.querySelectorAll('[data-edit-planning]').forEach(btn=>btn.addEventListener('click',()=>{const id=btn.getAttribute('data-edit-planning'), rec=(state.planningRecords[state.planningSubtab]||[]).find(x=>x.id===id); if(rec){state.planningEditing=JSON.parse(JSON.stringify(rec));state.planningMessage='';render();}}));
    document.querySelectorAll('[data-print-planning]').forEach(btn=>btn.addEventListener('click',()=>{const id=btn.getAttribute('data-print-planning'),rec=(state.planningRecords[state.planningSubtab]||[]).find(x=>x.id===id);if(rec)printPlanningRecord(state.planningSubtab,rec);}));
    const planningForm=document.getElementById('planning-form'); if(planningForm) planningForm.addEventListener('submit',async e=>{
      e.preventDefault(); const type=planningForm.getAttribute('data-planning-type'); const fd=new FormData(planningForm); const rec=JSON.parse(JSON.stringify(state.planningEditing||planningDefaults(type)));
      for(const [k,v] of fd.entries()) rec[k]=String(v).trim();
      if(type==='lesson'){
        const ini=new Date(rec.dataInicio+'T00:00:00'), fim=new Date(rec.dataFim+'T00:00:00');
        if(!rec.dataInicio||!rec.dataFim||!Number.isFinite(ini.getTime())||!Number.isFinite(fim.getTime())||fim<ini){state.planningMessage='Informe um período válido para o Plano de Aula.';render();return;}
        const days=Math.floor((fim-ini)/86400000)+1; if(days>30){state.planningMessage='O Plano de Aula não pode ultrapassar 30 dias.';render();return;}
        const overlap=(state.planningRecords.lesson||[]).some(x=>x.id!==rec.id && String(x.turma||'').toLocaleLowerCase('pt-BR')===String(rec.turma||'').toLocaleLowerCase('pt-BR') && x.dataInicio&&x.dataFim && !(rec.dataFim<x.dataInicio || rec.dataInicio>x.dataFim));
        if(overlap){state.planningMessage='Já existe um Plano de Aula para esta turma com período sobreposto. Ajuste as datas.';render();return;}
      }
      await savePlanningRecord(type,rec); await logAudit(type==='semester'?'planejamento_semestral_salvo':'plano_aula_salvo',`${state.user.name} salvou ${type==='semester'?'Planejamento Semestral':'Plano de Aula'}${rec.turma?' da turma '+rec.turma:''}.`); await loadPlanningType(type); state.planningEditing=null; state.planningMessage='Planejamento salvo com sucesso.'; render();
    });

'''
s=s.replace(anchor,handlers+anchor,1)

# 7. Backup inclui planejamentos e carrega antes de exportar
old="""    const exportBackup=document.getElementById('btn-export-backup'); if(exportBackup) exportBackup.addEventListener('click',()=>{const names=new Set(); (state.turmas||[]).forEach(t=>(t.students||[]).forEach(a=>names.add((a.nome||'').trim()))); const alunos=(state.roster||[]).filter(r=>names.has((r.name||'').trim())); const payload={plataforma:'Contabilidade Avançada',geradoEm:new Date().toISOString(),professor:state.user.name,turmas:state.turmas,alunos}; downloadText(`backup_contabilidade_avancada_${new Date().toISOString().slice(0,10)}.json`,JSON.stringify(payload,null,2),'application/json;charset=utf-8'); logAudit('backup_exportado',`${state.user.name} gerou backup pedagógico.`);});"""
new="""    const exportBackup=document.getElementById('btn-export-backup'); if(exportBackup) exportBackup.addEventListener('click',async()=>{await loadPlanningAll(); const names=new Set(); (state.turmas||[]).forEach(t=>(t.students||[]).forEach(a=>names.add((a.nome||'').trim()))); const alunos=(state.roster||[]).filter(r=>names.has((r.name||'').trim())); const payload={plataforma:'Contabilidade Avançada',geradoEm:new Date().toISOString(),professor:state.user.name,turmas:state.turmas,alunos,planejamentos:state.planningRecords}; downloadText(`backup_contabilidade_avancada_${new Date().toISOString().slice(0,10)}.json`,JSON.stringify(payload,null,2),'application/json;charset=utf-8'); logAudit('backup_exportado',`${state.user.name} gerou backup pedagógico incluindo planejamentos.`);});"""
if old not in s: raise SystemExit('backup handler não encontrado')
s=s.replace(old,new,1)
old="""<p class=\"desc\">Inclui turmas, alunos cadastrados nas turmas e progresso/notas disponíveis.</p>"""
new="""<p class=\"desc\">Inclui turmas, alunos cadastrados, progresso/notas e os Planejamentos Semestrais e Planos de Aula do professor.</p>"""
if old not in s: raise SystemExit('backup texto não encontrado')
s=s.replace(old,new,1)

# 8. Manual operacional e manual do professor
old="""<h4>5. Pendências, relatórios e suporte</h4><p>Pendências reúne alunos aguardando liberação de módulo, cadastros a regularizar e mensagens aguardando resposta. Relatórios apresentam resumo e detalhamento por atividade; Auditoria, Backup e Suporte permanecem disponíveis no painel do Professor.</p>"""
new="""<h4>5. Planejamento docente</h4><p>O menu Planejamento possui os submenus Planejamento Semestral e Plano de Aula. Os registros podem ser criados, editados, impressos ou salvos em PDF. O Plano de Aula exige data de início e fim, tem periodicidade máxima de 30 dias e não permite sobreposição de períodos para a mesma turma.</p><h4>6. Pendências, relatórios e suporte</h4><p>Pendências reúne alunos aguardando liberação de módulo, cadastros a regularizar e mensagens aguardando resposta. Relatórios apresentam resumo e detalhamento por atividade; Auditoria, Backup e Suporte permanecem disponíveis no painel do Professor.</p>"""
if old not in s: raise SystemExit('manual operacional não encontrado')
s=s.replace(old,new,1)
old="""    <h4>Notas da Turma</h4>
    <p>O menu \"Notas da Turma\" mostra a Nota do Módulo"""
new="""    <h4>Planejamento</h4><p>O menu \"Planejamento\" reúne o Planejamento Semestral e o Plano de Aula conforme os modelos institucionais. É possível salvar, editar e imprimir/salvar em PDF. No Plano de Aula, informe obrigatoriamente data de início e fim; cada período pode ter no máximo 30 dias e não pode se sobrepor a outro plano da mesma turma.</p>
    <h4>Notas da Turma</h4>
    <p>O menu \"Notas da Turma\" mostra a Nota do Módulo"""
if old not in s: raise SystemExit('manual professor não encontrado')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')

# 9. Segurança Firestore para chaves de planejamento
r=Path('firestore.rules')
rules=r.read_text(encoding='utf-8')
old="""    match /kv_store/{key} {
      allow read, write: if isActiveUser();
    }"""
new="""    match /kv_store/{key} {
      // Planejamentos são documentos internos do Professor. Cada professor acessa
      // apenas as próprias chaves (prefixadas pelo UID); o Usuário Mestre mantém acesso.
      allow read, write: if isActiveUser() && (
        !key.matches('^planning:.*') ||
        myRole() == 'admin' ||
        (myRole() == 'professor' && key.matches('^planning:' + request.auth.uid + ':.*'))
      );
    }"""
if old not in rules: raise SystemExit('firestore anchor não encontrado')
rules=rules.replace(old,new,1)
r.write_text(rules,encoding='utf-8')

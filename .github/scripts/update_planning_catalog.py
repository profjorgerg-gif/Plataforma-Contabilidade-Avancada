from pathlib import Path

app_path=Path('public/app.js')
s=app_path.read_text(encoding='utf-8')

# Estado do planejamento: preserva registros e acrescenta os cadastros reutilizáveis.
old="""    // ---- Planejamento docente ----
    planningSubtab: 'semester', // semester | lesson
    planningRecords: { semester: [], lesson: [] },
    planningEditing: null,
    planningMessage: ''"""
new="""    // ---- Planejamento docente ----
    planningSubtab: 'catalog', // catalog | semester | lesson
    planningCatalogSubtab: 'header', // header | schools | courses | classes | disciplines
    planningCatalog: null,
    planningCatalogEditing: null,
    planningRecords: { semester: [], lesson: [] },
    planningEditing: null,
    planningMessage: ''"""
if old not in s:
    raise SystemExit('estado do planejamento não encontrado')
s=s.replace(old,new,1)

# Substitui integralmente o bloco do Planejamento para evitar cadastros paralelos e manter compatibilidade.
start=s.index('  // ---- Planejamento docente (professor) ----')
end=s.index('  // ---- Correções pendentes (professor) ----', start)
block=r'''  // ---- Planejamento docente (professor) ----
  function planningOwnerKey(){
    return (state.user && state.user.uid) ? state.user.uid : encodeURIComponent((state.user && state.user.name) || 'professor');
  }
  function planningPrefix(type){ return `planning:${planningOwnerKey()}:${type}:`; }
  function planningCatalogKey(){ return `planning:${planningOwnerKey()}:catalog`; }
  function newPlanningId(type){ return `${type}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,7)}`; }
  function newCatalogId(type){ return `${type}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,7)}`; }
  function planningCatalogDefaults(){
    return {
      header:{
        name:(state.user&&state.user.name)||'',
        email:(state.user&&state.user.email)||'',
        area:'EIXO GESTÃO & NEGÓCIOS'
      },
      schools:[{
        id:'cedup_hh',name:'CEDUP HERMANN HERING',city:'BLUMENAU',
        address:'Rua Benjamin Constant, 857, Escola Agrícola, CEP 89037-501.',
        email:'ceduphh@sed.sc.gov.br',phone:'47 3378-8613',headerUrl:''
      }],
      courses:[
        {id:'tec_cont_pos',name:'Técnico em Contabilidade',sigla:'Pós-médio',modalidade:'Pós-Médio'},
        {id:'tec_adm_pos',name:'Técnico em Administração',sigla:'Pós-médio',modalidade:'Pós-Médio'},
        {id:'tec_adm_emiep',name:'Técnico em Administração',sigla:'EMIEP',modalidade:'EMIEP'}
      ],
      classMeta:{},
      discipline:{name:'CONTABILIDADE AVANÇADA',sigla:'CA'}
    };
  }
  function normalizePlanningCatalog(raw){
    const d=planningCatalogDefaults(), c=raw||{};
    c.header=Object.assign({},d.header,c.header||{});
    c.schools=Array.isArray(c.schools)&&c.schools.length?c.schools:d.schools;
    c.courses=Array.isArray(c.courses)&&c.courses.length?c.courses:d.courses;
    c.classMeta=c.classMeta&&typeof c.classMeta==='object'?c.classMeta:{};
    // Esta plataforma é exclusiva da disciplina CA.
    c.discipline={name:'CONTABILIDADE AVANÇADA',sigla:'CA'};
    return c;
  }
  async function loadPlanningCatalog(){
    let raw=null;
    try{ const r=await kvGet(planningCatalogKey()); if(r&&r.value) raw=JSON.parse(r.value); }catch(e){}
    state.planningCatalog=normalizePlanningCatalog(raw);
    return state.planningCatalog;
  }
  async function savePlanningCatalog(){
    state.planningCatalog=normalizePlanningCatalog(state.planningCatalog);
    await kvSet(planningCatalogKey(),JSON.stringify(state.planningCatalog));
  }
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
  async function loadPlanningAll(){
    await Promise.all([loadPlanningCatalog(),loadPlanningType('semester'),loadPlanningType('lesson')]);
  }
  async function savePlanningRecord(type,rec){
    rec.type=type; rec.professor=rec.professor||state.user.name; rec.professorUid=planningOwnerKey(); rec.updatedAt=Date.now();
    rec.disciplina='CONTABILIDADE AVANÇADA'; rec.componenteCurricular='CONTABILIDADE AVANÇADA'; rec.disciplinaSigla='CA';
    if(!rec.createdAt) rec.createdAt=rec.updatedAt;
    await kvSet(planningPrefix(type)+rec.id,JSON.stringify(rec));
  }
  function planningHeader(){ return (state.planningCatalog&&state.planningCatalog.header)||planningCatalogDefaults().header; }
  function planningSchools(){ return (state.planningCatalog&&state.planningCatalog.schools)||planningCatalogDefaults().schools; }
  function planningCourses(){ return (state.planningCatalog&&state.planningCatalog.courses)||planningCatalogDefaults().courses; }
  function planningClasses(){ return (state.turmas||[]).slice().sort((a,b)=>(a.name||'').localeCompare(b.name||'')); }
  function planningDefaults(type){
    const h=planningHeader(), school=planningSchools()[0]||{}, course=planningCourses()[0]||{}, turma=planningClasses()[0]||{};
    if(type==='semester') return {
      id:newPlanningId(type),escola:school.name||'',curso:course.name||'TÉCNICO EM CONTABILIDADE',disciplina:'CONTABILIDADE AVANÇADA',disciplinaSigla:'CA',modulo:'',turma:turma.name||'',professor:h.name||state.user.name,nAulas:'2',periodo:String(new Date().getFullYear()),
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
      id:newPlanningId(type),dataInicio:'',dataFim:'',escola:school.name||'',curso:course.name||'TÉCNICO EM CONTABILIDADE',professor:h.name||state.user.name,areaConhecimento:h.area||'EIXO GESTÃO & NEGÓCIOS',turma:turma.name||'',nAulasSemanais:'2',componenteCurricular:'CONTABILIDADE AVANÇADA',disciplinaSigla:'CA',
      objetosConhecimento:'Contabilização da Provisão da Folha de Pagamento: Salário, Férias, 13º Salário, Rescisão; Apuração do Resultado do Exercício: LALUR, Participações e Destinações do Resultado do Exercício; Participações, Destinações, Reservas, Reserva de Lucros, Dividendos; Declaração de Ajuste Anual do Imposto de Renda Pessoa Física, Apuração do Ganho de Capital da Pessoa Física;',
      habilidades:'Estudar as demonstrações contábeis obrigatórias. Compreender sobre a apuração e recolhimento. Adquirir noção de obrigações legais da área.',objetivoAprendizagem:'',
      metodologia:'Sala de Aula Invertida – uso de materiais digitais e prática presencial.\nAprendizagem Baseada em Problemas (PBL) – resolução de casos reais.\nGrupos Operativos – trabalhos colaborativos com foco em competências socioemocionais.\nAbordagem Inclusiva – estratégias adaptadas às necessidades dos estudantes.',recursos:'QUADRO, SLIDES, IMPRESSOS',
      instrumentosAvaliacao:'Estudos de caso e resolução de exercícios.',datasAvaliacoes:'',recuperacaoParalela:'Art. 6º Portaria Nº 874 de 01/04/2025. A recuperação paralela constitui nova oportunidade de aprendizagem e avaliação, prevalecendo o maior resultado obtido.',adaptacoes:'',referencias:''
    };
  }
  function planningField(name,label,value,kind='text',required=false,full=false,readonly=false){
    const req=required?' required':'', ro=readonly?' readonly':'', v=value===null||value===undefined?'':String(value), cls=full?' planning-full':'';
    if(kind==='textarea') return `<div class="planning-field planning-full"><label>${esc(label)}${required?' *':''}</label><textarea name="${esc(name)}" rows="5"${req}${ro}>${esc(v)}</textarea></div>`;
    return `<div class="planning-field${cls}"><label>${esc(label)}${required?' *':''}</label><input name="${esc(name)}" type="${kind}" value="${esc(v)}"${req}${ro}></div>`;
  }
  function planningSelect(name,label,value,options,required=false,full=false,disabled=false){
    const req=required?' required':'', dis=disabled?' disabled':'', cls=full?' planning-full':'';
    let html=`<div class="planning-field${cls}"><label>${esc(label)}${required?' *':''}</label><select name="${esc(name)}"${req}${dis}>`;
    html+=`<option value="">— selecione —</option>`;
    options.forEach(o=>{ const val=String(o.value??o.label??''), lab=String(o.label??o.value??''); html+=`<option value="${esc(val)}" ${String(value||'')===val?'selected':''}>${esc(lab)}</option>`; });
    return html+`</select></div>`;
  }
  function planningSchoolOptions(){ return planningSchools().map(x=>({value:x.name,label:`${x.name}${x.city?' — '+x.city:''}`})); }
  function planningCourseOptions(){ return planningCourses().map(x=>({value:x.name,label:`${x.name}${x.modalidade?' — '+x.modalidade:''}`})); }
  function planningClassOptions(){ return planningClasses().map(x=>({value:x.name,label:x.name})); }
  function renderPlanningForm(type,rec){
    let fields='';
    if(type==='semester'){
      fields+=planningSelect('escola','Escola',rec.escola,planningSchoolOptions(),true)+planningSelect('curso','Curso',rec.curso,planningCourseOptions(),true)+planningField('disciplina','Disciplina', 'CONTABILIDADE AVANÇADA (CA)','text',true,false,true)+planningField('periodo','Período/Ano',rec.periodo,'text',true)+planningField('modulo','Módulo',rec.modulo)+planningSelect('turma','Turma',rec.turma,planningClassOptions(),true)+planningField('professor','Professor',rec.professor,'text',true)+planningField('nAulas','Nº de aulas',rec.nAulas);
      fields+=planningField('ementa','Ementa',rec.ementa,'textarea')+planningField('habilidades','Habilidades',rec.habilidades,'textarea')+planningField('basesTecnologicas','Bases Tecnológicas / Conteúdos por unidade',rec.basesTecnologicas,'textarea')+planningField('objetoConhecimento','Objeto do Conhecimento',rec.objetoConhecimento,'textarea')+planningField('metodologia','Metodologia de Ensino-Aprendizagem',rec.metodologia,'textarea')+planningField('recursos','Recursos Utilizados',rec.recursos,'textarea')+planningField('instrumentosAvaliacao','Instrumentos Diversificados de Avaliação',rec.instrumentosAvaliacao,'textarea')+planningField('datasAvaliacoes','Datas Previstas de Avaliações e Recuperações',rec.datasAvaliacoes,'textarea')+planningField('recuperacaoParalela','Recuperação Paralela de Aprendizagem',rec.recuperacaoParalela,'textarea')+planningField('adaptacoes','Adaptações e Observações',rec.adaptacoes,'textarea')+planningField('referencias','Referências Bibliográficas',rec.referencias,'textarea')+planningField('localData','Local',rec.localData);
    }else{
      fields+=planningField('dataInicio','Data de início',rec.dataInicio,'date',true)+planningField('dataFim','Data de fim',rec.dataFim,'date',true)+planningSelect('escola','Escola',rec.escola,planningSchoolOptions(),true)+planningSelect('curso','Curso',rec.curso,planningCourseOptions(),true)+planningSelect('turma','Turma(s)',rec.turma,planningClassOptions(),true)+planningField('componenteCurricular','Componente Curricular','CONTABILIDADE AVANÇADA (CA)','text',true,false,true)+planningField('professor','Professor',rec.professor,'text',true)+planningField('areaConhecimento','Área(s) do Conhecimento',rec.areaConhecimento,'text',true)+planningField('nAulasSemanais','Nº de aulas semanais',rec.nAulasSemanais);
      fields+=planningField('objetosConhecimento','Objetos de Conhecimento',rec.objetosConhecimento,'textarea')+planningField('habilidades','Habilidades',rec.habilidades,'textarea')+planningField('objetivoAprendizagem','Objetivo de Aprendizagem',rec.objetivoAprendizagem,'textarea')+planningField('metodologia','Metodologia de Ensino-Aprendizagem',rec.metodologia,'textarea')+planningField('recursos','Recursos Utilizados',rec.recursos,'textarea')+planningField('instrumentosAvaliacao','Instrumentos Diversificados de Avaliação',rec.instrumentosAvaliacao,'textarea')+planningField('datasAvaliacoes','Datas Previstas de Avaliações e Recuperações',rec.datasAvaliacoes,'textarea')+planningField('recuperacaoParalela','Recuperação Paralela de Aprendizagem',rec.recuperacaoParalela,'textarea')+planningField('adaptacoes','Adaptações e Observações',rec.adaptacoes,'textarea')+planningField('referencias','Referências Bibliográficas',rec.referencias,'textarea');
    }
    const title=type==='semester'?'Planejamento Semestral':'Plano de Aula';
    return `<div class="card-box planning-card"><h4>${esc(title)} — ${rec.createdAt?'Editar':'Novo'}</h4>${type==='lesson'?'<div class="note">A periodicidade do Plano de Aula é de no máximo 30 dias. Planos da mesma turma não podem ter períodos sobrepostos.</div>':''}<form id="planning-form" data-planning-type="${type}" data-planning-id="${esc(rec.id)}"><div class="planning-grid">${fields}</div><div class="toolbar" style="margin-top:16px"><button class="btn-brass" type="submit">Salvar planejamento</button><button class="btn-outline" type="button" id="btn-cancel-planning">Cancelar</button></div></form></div>`;
  }
  function planningDateBR(v){ if(!v)return '—'; const [y,m,d]=String(v).split('-'); return y&&m&&d?`${d}/${m}/${y}`:v; }
  function planningPrintRows(type,r){
    const rows=type==='semester' ? [
      ['Escola',r.escola],['Curso',r.curso],['Disciplina','CONTABILIDADE AVANÇADA (CA)'],['Módulo',r.modulo],['Turma',r.turma],['Professor',r.professor],['Nº aulas',r.nAulas],['EMENTA',r.ementa],['HABILIDADES',r.habilidades],['BASES TECNOLÓGICAS / Conteúdos por unidade',r.basesTecnologicas],['OBJETO DO CONHECIMENTO',r.objetoConhecimento],['METODOLOGIA DE ENSINO APRENDIZAGEM',r.metodologia],['RECURSOS UTILIZADOS',r.recursos],['INSTRUMENTOS DIVERSIFICADOS DE AVALIAÇÃO',r.instrumentosAvaliacao],['DATAS PREVISTAS DE AVALIAÇÕES E RECUPERAÇÕES',r.datasAvaliacoes],['RECUPERAÇÃO PARALELA DE APRENDIZAGEM',r.recuperacaoParalela],['ADAPTAÇÕES E OBSERVAÇÕES',r.adaptacoes],['REFERÊNCIAS BIBLIOGRÁFICAS',r.referencias]
    ] : [
      ['Período',`${planningDateBR(r.dataInicio)} a ${planningDateBR(r.dataFim)}`],['Escola',r.escola],['Curso',r.curso],['Professor(a)',r.professor],['Área(s) do Conhecimento',r.areaConhecimento],['Turma(s)',r.turma],['Nº aulas semanais',r.nAulasSemanais],['COMPONENTE CURRICULAR','CONTABILIDADE AVANÇADA (CA)'],['OBJETOS DE CONHECIMENTO',r.objetosConhecimento],['HABILIDADES',r.habilidades],['OBJETIVO DE APRENDIZAGEM',r.objetivoAprendizagem],['METODOLOGIA DE ENSINO APRENDIZAGEM',r.metodologia],['RECURSOS UTILIZADOS',r.recursos],['INSTRUMENTOS DIVERSIFICADOS DE AVALIAÇÃO',r.instrumentosAvaliacao],['DATAS PREVISTAS DE AVALIAÇÕES E RECUPERAÇÕES',r.datasAvaliacoes],['RECUPERAÇÃO PARALELA DE APRENDIZAGEM',r.recuperacaoParalela],['ADAPTAÇÕES E OBSERVAÇÕES',r.adaptacoes],['REFERÊNCIAS BIBLIOGRÁFICAS',r.referencias]
    ];
    return rows.map(([a,b])=>`<tr><th>${esc(a)}</th><td>${esc(b||'').replace(/\n/g,'<br>')}</td></tr>`).join('');
  }
  function printPlanningRecord(type,r){
    const title=type==='semester'?`PLANO SEMESTRAL PÓS MÉDIO — ${r.periodo||''}`:`SEQUÊNCIA DIDÁTICA / PLANO DE AULA — ${planningDateBR(r.dataInicio)} a ${planningDateBR(r.dataFim)}`;
    const w=window.open('','_blank'); if(!w)return alert('Permita pop-ups para imprimir/salvar o planejamento em PDF.');
    w.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title><style>body{font-family:Arial,sans-serif;color:#111;margin:24px}h1,h2,p{text-align:center}h1{font-size:15px;margin:0}h2{font-size:16px;margin:12px 0}table{width:100%;border-collapse:collapse;font-size:12px}th,td{border:1px solid #333;padding:8px;vertical-align:top}th{width:25%;background:#f2d0ad;text-align:left}td{white-space:normal;line-height:1.45}@media print{body{margin:8mm}button{display:none}}</style></head><body><h1>ESTADO DE SANTA CATARINA<br>SECRETARIA DE ESTADO DA EDUCAÇÃO<br>CEDUP – CENTRO DE EDUCAÇÃO PROFISSIONAL HERMANN HERING</h1><h2>${esc(title)}</h2><table>${planningPrintRows(type,r)}</table><p style="text-align:left;margin-top:16px">Blumenau, ${new Date().toLocaleDateString('pt-BR')}.</p><script>window.onload=()=>window.print()<\/script></body></html>`); w.document.close();
  }
  function planningCatalogTabs(){
    const tabs=[['header','Cabeçalho'],['schools','Escolas'],['courses','Cursos'],['classes','Turmas'],['disciplines','Disciplinas']];
    return `<div class="planning-catalog-tabs">${tabs.map(([k,l])=>`<button type="button" class="planning-catalog-tab ${state.planningCatalogSubtab===k?'active':''}" data-planning-catalog-tab="${k}">${esc(l)}</button>`).join('')}</div>`;
  }
  function renderPlanningHeaderCatalog(){
    const h=planningHeader();
    return `<div class="card-box planning-card"><h4>Cabeçalho do Professor</h4><div class="note">Esses dados são sugeridos automaticamente ao criar novos planejamentos.</div><form id="planning-header-form"><div class="planning-grid">${planningField('name','Nome completo',h.name,'text',true)}${planningField('email','E-mail institucional do professor',h.email,'email',true)}${planningField('area','Área do conhecimento (padrão)',h.area,'text',true)}</div><div class="toolbar"><button class="btn-brass" type="submit">Salvar cabeçalho</button></div></form></div>`;
  }
  function renderPlanningSchoolsCatalog(){
    const editing=state.planningCatalogEditing&&state.planningCatalogEditing.kind==='school'?state.planningCatalogEditing:null;
    let html=`<div class="toolbar"><button class="btn-brass" id="btn-new-planning-school">+ Nova escola</button></div>`;
    if(editing){ html+=`<div class="card-box planning-card"><h4>${editing.id?'Editar escola':'Nova escola'}</h4><form id="planning-school-form"><div class="planning-grid">${planningField('name','Nome da escola/centro',editing.name||'','text',true)}${planningField('city','Cidade',editing.city||'','text',true)}${planningField('address','Endereço',editing.address||'','text',false,true)}${planningField('email','E-mail',editing.email||'','email')}${planningField('phone','Telefone',editing.phone||'')}${planningField('headerUrl','Brasão/cabeçalho — URL da imagem (opcional)',editing.headerUrl||'','url',false,true)}</div><div class="toolbar"><button class="btn-brass" type="submit">Salvar escola</button><button class="btn-outline" type="button" id="btn-cancel-catalog-edit">Cancelar</button></div></form></div>`; }
    html+=`<div class="planning-card-grid">`+planningSchools().map(x=>`<div class="review-card"><div class="review-head"><div><b>${esc(x.name)}</b><div class="thread-preview">${esc(x.city||'')}</div></div></div>${x.address?`<div class="thread-preview">${esc(x.address)}</div>`:''}<div class="review-actions"><button class="btn-outline" data-edit-planning-school="${esc(x.id)}">Editar</button><button class="btn-outline" data-delete-planning-school="${esc(x.id)}">Excluir</button></div></div>`).join('')+`</div>`;
    return html;
  }
  function renderPlanningCoursesCatalog(){
    const editing=state.planningCatalogEditing&&state.planningCatalogEditing.kind==='course'?state.planningCatalogEditing:null;
    let html=`<div class="toolbar"><button class="btn-brass" id="btn-new-planning-course">+ Novo curso</button></div>`;
    if(editing){ const mods=['Ambas / não se aplica','EMIEP','Pós-Médio']; html+=`<div class="card-box planning-card"><h4>${editing.id?'Editar curso':'Novo curso'}</h4><form id="planning-course-form"><div class="planning-grid">${planningField('name','Nome do curso',editing.name||'','text',true)}${planningField('sigla','Sigla / abreviação',editing.sigla||'')}${planningSelect('modalidade','Modalidade',editing.modalidade||'',mods.map(x=>({value:x,label:x})),true)}</div><div class="toolbar"><button class="btn-brass" type="submit">Salvar curso</button><button class="btn-outline" type="button" id="btn-cancel-catalog-edit">Cancelar</button></div></form></div>`; }
    html+=`<div class="planning-card-grid">`+planningCourses().map(x=>`<div class="review-card"><b>${esc(x.name)}</b><div class="thread-preview">Modalidade: ${esc(x.modalidade||'—')} · Sigla: ${esc(x.sigla||'—')}</div><div class="review-actions"><button class="btn-outline" data-edit-planning-course="${esc(x.id)}">Editar</button><button class="btn-outline" data-delete-planning-course="${esc(x.id)}">Excluir</button></div></div>`).join('')+`</div>`;
    return html;
  }
  function renderPlanningClassesCatalog(){
    const classes=planningClasses();
    let html=`<div class="note">As turmas são as mesmas já cadastradas no menu <b>Turmas</b>. Aqui você apenas define a modalidade usada nos planejamentos, evitando cadastro duplicado.</div><div class="toolbar"><button class="btn-outline" id="btn-manage-planning-classes">Gerenciar alunos e turmas</button></div>`;
    if(!classes.length) return html+`<div class="empty-state">Nenhuma turma cadastrada.</div>`;
    html+=`<div class="planning-card-grid">`+classes.map(t=>{const meta=(state.planningCatalog.classMeta||{})[t.id]||{}; return `<div class="review-card"><b>${esc(t.name)}</b><div class="thread-preview">${(t.students||[]).length} aluno(s)</div><label>Modalidade</label><select data-planning-class-mode="${esc(t.id)}"><option value="">— selecione —</option>${['EMIEP','Pós-Médio','Ambas / não se aplica'].map(x=>`<option value="${x}" ${meta.modalidade===x?'selected':''}>${x}</option>`).join('')}</select></div>`;}).join('')+`</div>`;
    return html;
  }
  function renderPlanningDisciplinesCatalog(){
    return `<div class="card-box planning-card"><h4>Disciplina da plataforma</h4><div class="note">Esta plataforma é exclusiva de Contabilidade Avançada. Não é permitido cadastrar ou selecionar outra disciplina.</div><div class="review-card"><b>CONTABILIDADE AVANÇADA</b><div class="thread-preview">Sigla usada nos planejamentos e documentos: <b>CA</b></div></div></div>`;
  }
  function renderPlanningCatalog(){
    if(!state.planningCatalog) state.planningCatalog=planningCatalogDefaults();
    let html=`<div class="note">Cadastros reutilizáveis para preencher Planejamentos Semestrais e Planos de Aula. As Turmas reaproveitam o cadastro pedagógico existente.</div>${planningCatalogTabs()}`;
    if(state.planningCatalogSubtab==='header') html+=renderPlanningHeaderCatalog();
    else if(state.planningCatalogSubtab==='schools') html+=renderPlanningSchoolsCatalog();
    else if(state.planningCatalogSubtab==='courses') html+=renderPlanningCoursesCatalog();
    else if(state.planningCatalogSubtab==='classes') html+=renderPlanningClassesCatalog();
    else html+=renderPlanningDisciplinesCatalog();
    return html;
  }
  function renderPlanning(){
    const tab=state.planningSubtab||'catalog';
    let html=`<div class="section-title">Planejamento</div><div class="note">Elabore, salve e imprima os planejamentos pedagógicos conforme os modelos institucionais do CEDUP Hermann Hering.</div><div class="ptabs planning-main-tabs"><div class="ptab ${tab==='catalog'?'active':''}" data-planning-tab="catalog">Cadastros</div><div class="ptab ${tab==='semester'?'active':''}" data-planning-tab="semester">Planejamento Semestral</div><div class="ptab ${tab==='lesson'?'active':''}" data-planning-tab="lesson">Plano de Aula</div></div>`;
    if(state.planningMessage) html+=`<div class="note">${esc(state.planningMessage)}</div>`;
    if(tab==='catalog') return html+renderPlanningCatalog();
    const type=tab, records=(state.planningRecords&&state.planningRecords[type])||[];
    if(state.planningEditing) return html+renderPlanningForm(type,state.planningEditing);
    html+=`<div class="toolbar"><button class="btn-brass" id="btn-new-planning">${type==='semester'?'Novo Planejamento Semestral':'Novo Plano de Aula'}</button></div>`;
    if(!records.length) return html+`<div class="empty-state">Nenhum ${type==='semester'?'planejamento semestral':'plano de aula'} salvo.</div>`;
    records.forEach(r=>{
      const title=type==='semester'?`${r.turma||'Turma não informada'} · ${r.periodo||''}`:`${r.turma||'Turma não informada'} · ${planningDateBR(r.dataInicio)} a ${planningDateBR(r.dataFim)}`;
      html+=`<div class="review-card"><div class="review-head"><div><b>${esc(title)}</b><div class="thread-preview">CONTABILIDADE AVANÇADA (CA)${r.escola?' · '+esc(r.escola):''}</div></div><span class="status-badge ok">Salvo</span></div><div class="review-actions"><button class="btn-outline" data-edit-planning="${esc(r.id)}">Editar</button><button class="btn-brass" data-print-planning="${esc(r.id)}">Imprimir / Salvar PDF</button></div></div>`;
    });
    return html;
  }
'''
s=s[:start]+block+'\n'+s[end:]

# Handlers do planejamento: substitui apenas o bloco dentro de attachHandlers.
hstart=s.rfind('    // ---- Planejamento docente ----')
hend=s.index('    // ---- Suporte: tabs, inbox, conversation ----',hstart)
handlers=r'''    // ---- Planejamento docente ----
    document.querySelectorAll('[data-planning-tab]').forEach(el=>el.addEventListener('click',async()=>{
      state.planningSubtab=el.getAttribute('data-planning-tab'); state.planningEditing=null; state.planningCatalogEditing=null; state.planningMessage='';
      if(state.planningSubtab==='catalog') await loadPlanningCatalog(); else await loadPlanningType(state.planningSubtab); render();
    }));
    document.querySelectorAll('[data-planning-catalog-tab]').forEach(el=>el.addEventListener('click',()=>{state.planningCatalogSubtab=el.getAttribute('data-planning-catalog-tab');state.planningCatalogEditing=null;state.planningMessage='';render();}));
    const newPlanning=document.getElementById('btn-new-planning'); if(newPlanning) newPlanning.addEventListener('click',()=>{state.planningEditing=planningDefaults(state.planningSubtab);state.planningMessage='';render();});
    const cancelPlanning=document.getElementById('btn-cancel-planning'); if(cancelPlanning) cancelPlanning.addEventListener('click',()=>{state.planningEditing=null;state.planningMessage='';render();});
    document.querySelectorAll('[data-edit-planning]').forEach(btn=>btn.addEventListener('click',()=>{const id=btn.getAttribute('data-edit-planning'),rec=(state.planningRecords[state.planningSubtab]||[]).find(x=>x.id===id);if(rec){state.planningEditing=JSON.parse(JSON.stringify(rec));state.planningMessage='';render();}}));
    document.querySelectorAll('[data-print-planning]').forEach(btn=>btn.addEventListener('click',()=>{const id=btn.getAttribute('data-print-planning'),rec=(state.planningRecords[state.planningSubtab]||[]).find(x=>x.id===id);if(rec)printPlanningRecord(state.planningSubtab,rec);}));
    const planningForm=document.getElementById('planning-form'); if(planningForm) planningForm.addEventListener('submit',async e=>{
      e.preventDefault(); const type=planningForm.getAttribute('data-planning-type'),fd=new FormData(planningForm),rec=JSON.parse(JSON.stringify(state.planningEditing||planningDefaults(type)));
      for(const [k,v] of fd.entries()) rec[k]=String(v).trim(); rec.disciplina='CONTABILIDADE AVANÇADA';rec.componenteCurricular='CONTABILIDADE AVANÇADA';rec.disciplinaSigla='CA';
      if(type==='lesson'){
        const ini=new Date(rec.dataInicio+'T00:00:00'),fim=new Date(rec.dataFim+'T00:00:00');
        if(!rec.dataInicio||!rec.dataFim||!Number.isFinite(ini.getTime())||!Number.isFinite(fim.getTime())||fim<ini){state.planningMessage='Informe um período válido para o Plano de Aula.';render();return;}
        const days=Math.floor((fim-ini)/86400000)+1;if(days>30){state.planningMessage='O Plano de Aula não pode ultrapassar 30 dias.';render();return;}
        const overlap=(state.planningRecords.lesson||[]).some(x=>x.id!==rec.id&&String(x.turma||'').toLocaleLowerCase('pt-BR')===String(rec.turma||'').toLocaleLowerCase('pt-BR')&&x.dataInicio&&x.dataFim&&!(rec.dataFim<x.dataInicio||rec.dataInicio>x.dataFim));
        if(overlap){state.planningMessage='Já existe um Plano de Aula para esta turma com período sobreposto. Ajuste as datas.';render();return;}
      }
      await savePlanningRecord(type,rec);await logAudit(type==='semester'?'planejamento_semestral_salvo':'plano_aula_salvo',`${state.user.name} salvou ${type==='semester'?'Planejamento Semestral':'Plano de Aula'}${rec.turma?' da turma '+rec.turma:''}.`);await loadPlanningType(type);state.planningEditing=null;state.planningMessage='Planejamento salvo com sucesso.';render();
    });
    const headerForm=document.getElementById('planning-header-form'); if(headerForm) headerForm.addEventListener('submit',async e=>{e.preventDefault();const fd=new FormData(headerForm);state.planningCatalog.header={name:String(fd.get('name')||'').trim(),email:String(fd.get('email')||'').trim(),area:String(fd.get('area')||'').trim()};await savePlanningCatalog();await logAudit('cadastro_planejamento_atualizado',`${state.user.name} atualizou o Cabeçalho do Planejamento.`);state.planningMessage='Cabeçalho salvo com sucesso.';render();});
    const newSchool=document.getElementById('btn-new-planning-school');if(newSchool)newSchool.addEventListener('click',()=>{state.planningCatalogEditing={kind:'school',id:'',name:'',city:'',address:'',email:'',phone:'',headerUrl:''};render();});
    document.querySelectorAll('[data-edit-planning-school]').forEach(btn=>btn.addEventListener('click',()=>{const x=planningSchools().find(v=>v.id===btn.getAttribute('data-edit-planning-school'));if(x){state.planningCatalogEditing=Object.assign({kind:'school'},JSON.parse(JSON.stringify(x)));render();}}));
    document.querySelectorAll('[data-delete-planning-school]').forEach(btn=>btn.addEventListener('click',async()=>{const id=btn.getAttribute('data-delete-planning-school');if(!confirm('Excluir esta escola do cadastro de planejamento?'))return;state.planningCatalog.schools=planningSchools().filter(x=>x.id!==id);await savePlanningCatalog();state.planningMessage='Escola excluída.';render();}));
    const schoolForm=document.getElementById('planning-school-form');if(schoolForm)schoolForm.addEventListener('submit',async e=>{e.preventDefault();const fd=new FormData(schoolForm),cur=state.planningCatalogEditing||{},rec={id:cur.id||newCatalogId('school')};for(const [k,v] of fd.entries())rec[k]=String(v).trim();const arr=planningSchools().slice(),idx=arr.findIndex(x=>x.id===rec.id);if(idx>=0)arr[idx]=rec;else arr.push(rec);state.planningCatalog.schools=arr;await savePlanningCatalog();await logAudit('cadastro_planejamento_atualizado',`${state.user.name} salvou a escola ${rec.name}.`);state.planningCatalogEditing=null;state.planningMessage='Escola salva com sucesso.';render();});
    const newCourse=document.getElementById('btn-new-planning-course');if(newCourse)newCourse.addEventListener('click',()=>{state.planningCatalogEditing={kind:'course',id:'',name:'',sigla:'',modalidade:'Pós-Médio'};render();});
    document.querySelectorAll('[data-edit-planning-course]').forEach(btn=>btn.addEventListener('click',()=>{const x=planningCourses().find(v=>v.id===btn.getAttribute('data-edit-planning-course'));if(x){state.planningCatalogEditing=Object.assign({kind:'course'},JSON.parse(JSON.stringify(x)));render();}}));
    document.querySelectorAll('[data-delete-planning-course]').forEach(btn=>btn.addEventListener('click',async()=>{const id=btn.getAttribute('data-delete-planning-course');if(!confirm('Excluir este curso do cadastro de planejamento?'))return;state.planningCatalog.courses=planningCourses().filter(x=>x.id!==id);await savePlanningCatalog();state.planningMessage='Curso excluído.';render();}));
    const courseForm=document.getElementById('planning-course-form');if(courseForm)courseForm.addEventListener('submit',async e=>{e.preventDefault();const fd=new FormData(courseForm),cur=state.planningCatalogEditing||{},rec={id:cur.id||newCatalogId('course')};for(const [k,v] of fd.entries())rec[k]=String(v).trim();const arr=planningCourses().slice(),idx=arr.findIndex(x=>x.id===rec.id);if(idx>=0)arr[idx]=rec;else arr.push(rec);state.planningCatalog.courses=arr;await savePlanningCatalog();await logAudit('cadastro_planejamento_atualizado',`${state.user.name} salvou o curso ${rec.name}.`);state.planningCatalogEditing=null;state.planningMessage='Curso salvo com sucesso.';render();});
    const cancelCatalog=document.getElementById('btn-cancel-catalog-edit');if(cancelCatalog)cancelCatalog.addEventListener('click',()=>{state.planningCatalogEditing=null;render();});
    document.querySelectorAll('[data-planning-class-mode]').forEach(sel=>sel.addEventListener('change',async()=>{const id=sel.getAttribute('data-planning-class-mode');if(!state.planningCatalog.classMeta)state.planningCatalog.classMeta={};state.planningCatalog.classMeta[id]={modalidade:sel.value};await savePlanningCatalog();}));
    const manageClasses=document.getElementById('btn-manage-planning-classes');if(manageClasses)manageClasses.addEventListener('click',()=>{state.professorTab='turmas';render();});

'''
s=s[:hstart]+handlers+s[hend:]

# Backup também inclui os cadastros do planejamento.
s=s.replace('planejamentos:state.planningRecords','planejamentos:state.planningRecords,cadastrosPlanejamento:state.planningCatalog')

# Manuais embutidos: atualiza orientação de uso do novo cadastro reutilizável.
s=s.replace('<h4>5. Planejamento docente</h4><p>O menu Planejamento possui os submenus Planejamento Semestral e Plano de Aula. Os registros podem ser criados, editados, impressos ou salvos em PDF. O Plano de Aula exige data de início e fim, tem periodicidade máxima de 30 dias e não permite sobreposição de períodos para a mesma turma.</p>', '<h4>5. Planejamento docente</h4><p>O menu Planejamento reúne Cadastros, Planejamento Semestral e Plano de Aula. Em Cadastros, configure Cabeçalho, Escolas e Cursos; as Turmas são reaproveitadas do cadastro pedagógico da plataforma. A disciplina é fixa em Contabilidade Avançada (CA). Os planejamentos podem ser criados, editados, impressos ou salvos em PDF. O Plano de Aula exige data de início e fim, tem periodicidade máxima de 30 dias e não permite sobreposição de períodos para a mesma turma.</p>')
s=s.replace('<h4>Planejamento</h4><p>O menu "Planejamento" reúne o Planejamento Semestral e o Plano de Aula conforme os modelos institucionais. É possível salvar, editar e imprimir/salvar em PDF. No Plano de Aula, informe obrigatoriamente data de início e fim; cada período pode ter no máximo 30 dias e não pode se sobrepor a outro plano da mesma turma.</p>', '<h4>Planejamento</h4><p>O menu "Planejamento" possui Cadastros, Planejamento Semestral e Plano de Aula. Em Cadastros, mantenha Cabeçalho, Escolas e Cursos; as Turmas são compartilhadas com o cadastro principal. A única disciplina disponível é Contabilidade Avançada (CA). É possível salvar, editar e imprimir/salvar em PDF. No Plano de Aula, informe obrigatoriamente data de início e fim; cada período pode ter no máximo 30 dias e não pode se sobrepor a outro plano da mesma turma.</p>')

app_path.write_text(s,encoding='utf-8')

# Ajuste visual: campos proporcionais, largura completa, tema escuro e responsividade.
idx_path=Path('public/index.html')
h=idx_path.read_text(encoding='utf-8')
css=r'''
  /* Planejamento docente — formulário proporcional e responsivo */
  #cont-avancada .planning-card { width:100%; max-width:none; }
  #cont-avancada .planning-grid {
    display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
    gap:14px 18px; align-items:start; width:100%;
  }
  #cont-avancada .planning-field { min-width:0; margin:0; }
  #cont-avancada .planning-full { grid-column:1 / -1; }
  #cont-avancada .planning-field label { margin:0 0 6px; font-weight:500; }
  #cont-avancada .planning-field input,
  #cont-avancada .planning-field select,
  #cont-avancada .planning-field textarea,
  #cont-avancada [data-planning-class-mode] {
    display:block; width:100%; max-width:none; min-width:0;
    padding:10px 12px; border:1px solid var(--line); border-radius:4px;
    background:var(--card); color:var(--ink); font:inherit; line-height:1.45;
  }
  #cont-avancada .planning-field textarea { min-height:118px; resize:vertical; overflow:auto; }
  #cont-avancada .planning-field input[readonly] { opacity:.88; cursor:not-allowed; }
  #cont-avancada .planning-field input:focus,
  #cont-avancada .planning-field select:focus,
  #cont-avancada .planning-field textarea:focus { outline:2px solid var(--brass); outline-offset:1px; }
  #cont-avancada .planning-main-tabs { flex-wrap:wrap; }
  #cont-avancada .planning-catalog-tabs { display:flex; flex-wrap:wrap; gap:8px; margin:0 0 18px; }
  #cont-avancada .planning-catalog-tab {
    border:1px solid var(--line); border-radius:18px; padding:8px 14px;
    background:var(--card); color:var(--ink-soft); cursor:pointer; font:inherit;
  }
  #cont-avancada .planning-catalog-tab.active { border-color:var(--brass); color:var(--ink); font-weight:600; }
  #cont-avancada .planning-card-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
  @media (max-width:800px) {
    #cont-avancada .planning-grid, #cont-avancada .planning-card-grid { grid-template-columns:1fr; }
    #cont-avancada .planning-full { grid-column:1; }
    #cont-avancada .planning-field textarea { min-height:140px; }
  }
'''
if '/* Planejamento docente — formulário proporcional e responsivo */' not in h:
    pos=h.rfind('</style>')
    if pos<0: raise SystemExit('style de index não encontrado')
    h=h[:pos]+css+'\n'+h[pos:]
idx_path.write_text(h,encoding='utf-8')

# Documentação resumida da funcionalidade atual.
readme=Path('README.md')
r=readme.read_text(encoding='utf-8')
section='''\n\n## Planejamento docente\n\nO perfil Professor possui o menu **Planejamento**, organizado em **Cadastros**, **Planejamento Semestral** e **Plano de Aula**. Em Cadastros ficam Cabeçalho, Escolas, Cursos, Turmas e Disciplinas. As Turmas reutilizam o cadastro principal da plataforma, e a única disciplina disponível é **Contabilidade Avançada (CA)**. Os planejamentos podem ser salvos, editados e impressos/salvos em PDF. O Plano de Aula exige data de início e fim, com período máximo de 30 dias e sem sobreposição para a mesma turma.\n'''
if '## Planejamento docente' not in r:
    r+=section
readme.write_text(r,encoding='utf-8')

from pathlib import Path

p = Path('public/app.js')
s = p.read_text(encoding='utf-8')


def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Padrão não encontrado: {label}')
    s = s.replace(old, new, 1)

rep("    masterCode: '',\n    progress: null, // current student's progress object", "    masterCode: '',\n    loginMatricula: '', // confirmação obrigatória do aluno em todo login\n    progress: null, // current student's progress object", 'estado loginMatricula')

marker = "  // ---- PDF import (pdf.js loaded on demand from cdnjs) ----"
helper = r'''  function normalizeMatricula(value){
    return String(value || '').replace(/\D/g, '');
  }

  async function findStudentEnrollmentByMatricula(matricula){
    const target = normalizeMatricula(matricula);
    if (!target) return null;
    try {
      const list = await kvList('turma:');
      if (!list || !list.keys) return null;
      const matches = [];
      for (const k of list.keys){
        try {
          const r = await kvGet(k);
          if (!r || !r.value) continue;
          const turma = JSON.parse(r.value);
          const student = (turma.students || []).find(st => normalizeMatricula(st.matricula) === target);
          if (student) matches.push({ turma, student });
        } catch(e){}
      }
      matches.sort((a,b) => ((b.turma.updatedAt||b.turma.createdAt||0) - (a.turma.updatedAt||a.turma.createdAt||0)));
      return matches[0] || null;
    } catch(e){
      return null;
    }
  }

  async function loadProgressForEnrollment(oldName, academicName){
    const newName = (academicName || '').trim();
    const previousName = (oldName || '').trim();
    if (!newName) return emptyProgress(previousName || 'Aluno');
    try {
      const current = await kvGet('student:' + newName);
      if (current && current.value) return await loadProgress(newName);
      if (previousName && previousName.toLocaleLowerCase('pt-BR') !== newName.toLocaleLowerCase('pt-BR')){
        const old = await kvGet('student:' + previousName);
        if (old && old.value){
          const parsed = JSON.parse(old.value);
          parsed.name = newName;
          parsed.updatedAt = Date.now();
          await kvSet('student:' + newName, JSON.stringify(parsed));
          return await loadProgress(newName);
        }
      }
    } catch(e){}
    return await loadProgress(newName);
  }

'''
if marker not in s:
    raise SystemExit('Marcador PDF não encontrado')
s = s.replace(marker, helper + marker, 1)

old_login = '''            <p class="auth-hint2">Só é usado na primeira vez que esta conta entra no sistema. Depois disso, o perfil só pode ser alterado por um Usuário Mestre, no painel de Usuários.</p>\n\n            <label class="auth-label" for="master-code">Código de Mestre (opcional)</label>'''
new_login = '''            <p class="auth-hint2">Só é usado na primeira vez que esta conta entra no sistema. Depois disso, o perfil só pode ser alterado por um Usuário Mestre, no painel de Usuários.</p>\n\n            ${state.signupRole==='aluno' ? `<label class="auth-label" for="student-matricula">Matrícula do aluno</label>\n            <input type="text" id="student-matricula" inputmode="numeric" autocomplete="off" placeholder="Informe sua matrícula" value="${esc(state.loginMatricula)}" />\n            <p class="auth-hint2">Obrigatória em todo acesso do Aluno. A matrícula precisa constar em uma turma criada pelo Professor, por importação PDF ou cadastro individual.</p>` : ''}\n\n            <label class="auth-label" for="master-code">Código de Mestre (opcional)</label>'''
rep(old_login, new_login, 'campo matrícula no login')

old_handlers = '''    document.getElementById('role-professor').addEventListener('click', () => { state.signupRole='professor'; render(); });\n    const mc = document.getElementById('master-code');'''
new_handlers = '''    document.getElementById('role-professor').addEventListener('click', () => { state.signupRole='professor'; render(); });\n    const sm = document.getElementById('student-matricula');\n    if (sm) sm.addEventListener('input', e => { state.loginMatricula = e.target.value; });\n    const mc = document.getElementById('master-code');'''
rep(old_handlers, new_handlers, 'handler matrícula')

rep("    <p>Entre com sua conta Google e selecione o perfil \"Aluno(a)\" no primeiro acesso. Seu progresso é salvo automaticamente e fica visível para o professor acompanhar.</p>", "    <p>Entre com sua conta Google e informe sua <b>matrícula em todo acesso</b>. A entrada somente é liberada quando a matrícula estiver cadastrada em uma turma criada pelo Professor, por importação PDF ou inclusão individual. O nome acadêmico da turma passa a identificar seu progresso na plataforma.</p>", 'manual aluno acesso')

rep("    <p>No menu \"Turmas\" você cria turmas informando apenas um nome. Dentro de cada turma é possível montar a lista de alunos de duas formas:</p>", "    <p>No menu \"Turmas\" você cria turmas informando apenas um nome. <b>Somente alunos com matrícula cadastrada em uma dessas turmas conseguem entrar na plataforma.</b> A matrícula é confirmada obrigatoriamente em todo login do Aluno. Dentro de cada turma é possível montar a lista de alunos de duas formas:</p>", 'manual professor turmas')

# Atualiza o texto operacional quando presente.
s = s.replace('O login utiliza Google. Professores novos dependem de aprovação do Usuário Mestre.', 'O login utiliza Google. Alunos confirmam obrigatoriamente a matrícula em todo acesso e só entram quando a matrícula consta em uma turma criada pelo Professor. Professores novos dependem de aprovação do Usuário Mestre.')

# Limpa matrícula ao sair explicitamente.
s = s.replace("      state.authError = ''; state.masterCode = ''; state.signupRole = 'aluno';", "      state.authError = ''; state.masterCode = ''; state.loginMatricula = ''; state.signupRole = 'aluno';", 1)

start = s.index("  onAuthStateChanged(auth, async (fbUser) => {")
end = s.index("\n})();", start)
new_auth = r'''  onAuthStateChanged(auth, async (fbUser) => {
    if (fbUser){
      let profile;
      let userRef;
      try {
        userRef = doc(db, 'users', fbUser.uid);
        const snap = await getDoc(userRef);
        if (snap.exists()){
          profile = snap.data();
        } else {
          // Primeira vez que esta conta entra: cria o perfil com o papel
          // escolhido na tela de login (e o Código de Mestre, se informado).
          let role = state.signupRole === 'professor' ? 'pending_professor' : 'aluno';
          if (state.masterCode && MASTER_CODE && state.masterCode === MASTER_CODE) role = 'admin';
          profile = { name: fbUser.displayName || fbUser.email || 'Usuário', email: fbUser.email || '', role, status: role==='pending_professor'?'pending':'active', createdAt:Date.now() };
          await setDoc(userRef, profile);
        }
      } catch(e){
        console.error('Erro ao carregar/criar perfil', e);
        profile = null;
      }
      if (!profile){
        await signOut(auth);
        return;
      }

      if (profile.role === 'aluno'){
        const informedMatricula = normalizeMatricula(state.loginMatricula);
        if (!informedMatricula){
          state.authError = 'Informe sua matrícula para entrar como Aluno(a). A confirmação é obrigatória em todo acesso.';
          await signOut(auth);
          return;
        }
        const enrollment = await findStudentEnrollmentByMatricula(informedMatricula);
        if (!enrollment){
          state.authError = 'Matrícula não localizada em nenhuma turma ativa. Solicite ao professor a conferência do cadastro da turma.';
          state.loginMatricula = '';
          await signOut(auth);
          return;
        }
        const storedMatricula = normalizeMatricula(profile.matricula);
        if (storedMatricula && storedMatricula !== informedMatricula){
          state.authError = 'A matrícula informada não corresponde à matrícula já vinculada a esta conta Google. Solicite a correção ao Professor ou Usuário Mestre.';
          state.loginMatricula = '';
          await signOut(auth);
          return;
        }
        const academicName = (enrollment.student.nome || profile.name || fbUser.displayName || fbUser.email || 'Aluno').trim();
        const oldName = profile.academicName || profile.name || '';
        try {
          await updateDoc(userRef, {
            name: academicName,
            academicName,
            matricula: informedMatricula,
            turmaId: enrollment.turma.id,
            turmaName: enrollment.turma.name,
            enrollmentVerifiedAt: Date.now()
          });
        } catch(e){
          console.error('Erro ao vincular matrícula ao perfil', e);
          state.authError = 'Não foi possível confirmar sua matrícula neste acesso. Tente novamente ou comunique o professor.';
          await signOut(auth);
          return;
        }
        profile = { ...profile, name: academicName, academicName, matricula: informedMatricula, turmaId: enrollment.turma.id, turmaName: enrollment.turma.name };
        state.user = { name: academicName, email: profile.email || fbUser.email || '', role: 'aluno', uid: fbUser.uid, matricula: informedMatricula };
        state.progress = await loadProgressForEnrollment(oldName, academicName);
        state.studentTurma = enrollment.turma;
        state.authError = ''; state.masterCode = ''; state.loginMatricula = '';
        await logAudit('login', `${academicName} realizou login na plataforma com matrícula confirmada.`);
        state.view = 'dashboard';
      } else {
        state.user = { name: profile.name, email: profile.email || fbUser.email || '', role: profile.role, uid: fbUser.uid };
        state.authError = ''; state.masterCode = ''; state.loginMatricula = '';
        await logAudit('login', `${profile.name || fbUser.email || 'Usuário'} realizou login na plataforma.`);
        if (profile.role === 'pending_professor'){
          state.view='access-pending';
        } else if (profile.role === 'professor'){
          state.roster = await loadRoster();
          state.turmas = await loadTurmasForProfessor(profile.name);
          state.professorTab = state.professorTab || 'acompanhamento';
          state.view = 'professor';
        } else if (profile.role === 'admin'){
          state.suporteTab = 'alunos';
          await loadSuporteForCurrentTab();
          state.view = 'suporte';
        }
      }
    } else {
      state.user = null;
      state.progress = null; state.roster = null; state.studentTurma=null;
      state.view = 'login';
    }
    render();
  });'''
s = s[:start] + new_auth + s[end:]

p.write_text(s, encoding='utf-8')
print('app.js atualizado')

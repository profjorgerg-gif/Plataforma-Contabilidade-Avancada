# Plataforma Contabilidade Avançada

Plataforma didática da disciplina de **Contabilidade Avançada**, destinada aos cursos técnicos em Administração e Contabilidade do CEDUP Hermann Hering.

## Ambiente

- **Produção:** https://ca-contabilidade-avancada.web.app
- **Front-end:** HTML, CSS e JavaScript puro com ES Modules
- **Autenticação:** Firebase Authentication com conta Google
- **Banco de dados:** Cloud Firestore
- **Hospedagem:** Firebase Hosting
- **Deploy:** GitHub Actions a partir da branch `main`

## Estrutura pedagógica

A plataforma possui 5 módulos. Cada módulo contém:

- conteúdo teórico;
- 5 listas de exercícios com 10 questões cada;
- autocorreção das listas;
- quiz avaliativo autocorrigido;
- recuperação paralela autocorrigida;
- fluxo de envio do módulo para revisão do professor;
- feedback e liberação da Nota Final pelo professor.

A **nota automática do módulo** é calculada com 50% da média das 5 listas, já considerando eventuais substituições pela Recuperação, e 50% da nota do Quiz. A Recuperação não compõe a média diretamente: sua nota substitui, para efeito de cálculo, cada nota de lista que seja inferior à nota obtida na Recuperação. A Nota Final somente é considerada liberada quando o professor conclui a revisão do módulo.

## Fluxo de correção por módulo

1. O aluno estuda o conteúdo do módulo.
2. Realiza as 5 listas, que são corrigidas automaticamente.
3. Realiza o quiz e, quando houver Recuperação, a nota desta substitui individualmente as notas das listas que forem inferiores a ela para efeito do cálculo automático.
4. Quando os requisitos do módulo estiverem concluídos, o aluno usa **Enviar módulo para correção**.
5. O módulo passa para o status **Enviado para correção**.
6. O professor acessa **Correções Pendentes**, visualiza a nota automática e pode:
   - aprovar e liberar a Nota Final;
   - ajustar a Nota Final antes da liberação;
   - registrar feedback;
   - devolver o módulo para ajustes.
7. Quando devolvido, o aluno recebe o feedback e pode refazer as atividades avaliativas do módulo antes de novo envio.

## Acompanhamento de notas

### Aluno

O menu **Minhas Notas** apresenta, por módulo:

- nota individual de cada uma das 5 listas/exercícios;
- indicação com `*` quando a nota exibida foi substituída pela nota da Recuperação;
- nota do Quiz;
- nota da Recuperação;
- nota automática;
- status da correção;
- Nota Final liberada;
- feedback do professor.

### Professor

O menu **Notas da Turma** apresenta os alunos vinculados às turmas daquele professor, com notas e situação dos 5 módulos. Também estão disponíveis:

- exportação das notas em CSV;
- impressão / salvamento em PDF;
- menu **Relatórios**;
- menu **Backup** para exportação pedagógica em JSON;
- **Correções Pendentes**;
- **Auditoria**.

## Turmas e alunos

O professor pode criar turmas e cadastrar alunos:

- individualmente, por nome e matrícula;
- por importação de PDF.

Os painéis de notas, correções, relatórios e backup do professor trabalham com os alunos vinculados às suas próprias turmas.

## Suporte

O suporte mantém canais entre aluno, professor e administração. Os chamados possuem:

- protocolo automático;
- histórico das mensagens;
- status **Aberto** ou **Encerrado**;
- possibilidade de encerramento e reabertura pelo responsável.

## Controle de acesso

Os perfis são:

- **Aluno(a)**;
- **Professor(a)**;
- **Usuário Mestre**.

No primeiro acesso como Professor(a), a conta é criada como **aguardando aprovação**. O professor não entra na área pedagógica até que um Usuário Mestre aprove seu cadastro no painel **Usuários**.

O Usuário Mestre pode aprovar Professores e administrar os perfis cadastrados.

## Firestore e regras de segurança

O arquivo `firestore.rules` do repositório contém a versão reforçada das regras para impedir acesso ao armazenamento pedagógico por contas de Professor ainda pendentes e limitar alterações de perfil.

**Situação de implantação:** o Service Account atualmente utilizado pelo GitHub Actions possui permissão para publicar o Firebase Hosting, mas não possui a permissão `firebaserules` necessária para publicar as regras do Firestore. Por isso, o workflow tenta publicar as regras, registra um aviso em caso de falta de permissão e continua com a publicação do Hosting.

Até que a permissão do Service Account seja ampliada e o deploy das regras seja concluído com sucesso, a proteção de Professor pendente está ativa na interface da aplicação, mas o endurecimento correspondente das regras do Firestore ainda não deve ser considerado publicado em produção.

## Publicação automática

O workflow `.github/workflows/firebase-hosting-deploy.yml` é executado em pushes para `main`.

O Hosting é publicado automaticamente com o segredo `FIREBASE_SERVICE_ACCOUNT` configurado no repositório.

Para que o mesmo workflow consiga publicar `firestore.rules`, o Service Account precisa receber no projeto Firebase/Google Cloud uma função que inclua as permissões de Firebase Rules necessárias, por exemplo uma função administrativa apropriada para Firebase Rules.

## Arquivos principais

- `public/index.html` — estrutura visual e estilos;
- `public/app.js` — conteúdo, exercícios, avaliações, notas, turmas, suporte, auditoria e fluxos da aplicação;
- `public/firebase-config.js` — configuração do Firebase;
- `firestore.rules` — regras de segurança do Firestore;
- `firebase.json` — configuração de Hosting e Firestore;
- `.github/workflows/firebase-hosting-deploy.yml` — deploy automático.

## Verificações recomendadas após atualizações

- login como Aluno, Professor e Usuário Mestre;
- solicitação e aprovação de novo Professor;
- realização e autocorreção das 5 listas;
- Quiz e Recuperação;
- substituição das notas de listas inferiores pela nota da Recuperação;
- envio de módulo para correção;
- aprovação, feedback e devolução para ajustes;
- menus de notas do Aluno e Professor;
- exportação CSV, impressão/PDF e backup JSON;
- suporte com protocolo e status;
- visualização em desktop e celular.

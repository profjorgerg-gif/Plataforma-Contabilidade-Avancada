# Contabilidade Avançada — plataforma (GitHub + Firebase)

Este é o mesmo aplicativo que você já vinha usando como artefato, agora
preparado para rodar como um site de verdade, hospedado no **Firebase
Hosting**, com login real (e-mail e senha) via **Firebase Authentication**
e dados salvos no **Firestore** — em vez do armazenamento temporário do
artefato.

Você não precisa saber programar para seguir este guia; é
principalmente clicar em botões nos sites do GitHub e do Firebase e
copiar/colar alguns comandos no terminal.

---

## Parte 1 — Criar sua conta no GitHub e o repositório

1. Acesse **https://github.com** e clique em **Sign up** para criar sua conta (se já tiver uma, pule para o passo 2).
2. Já logado, clique no **+** no canto superior direito → **New repository**.
3. Dê um nome, por exemplo `contabilidade-avancada`. Deixe como **Private** se preferir que só você tenha acesso ao código. Não marque nenhuma opção de inicializar com README (nós já temos os arquivos prontos). Clique em **Create repository**.
4. O GitHub vai te mostrar um endereço parecido com:
   `https://github.com/SEU-USUARIO/contabilidade-avancada.git`
   Guarde esse endereço, vamos usar no passo 6.

### Instalando o Git no seu computador (se ainda não tiver)

- **Windows:** baixe em https://git-scm.com/download/win e instale (pode manter todas as opções padrão).
- **Mac:** abra o Terminal e digite `git --version` — se não estiver instalado, o próprio macOS vai oferecer para instalar.

### Enviando os arquivos deste projeto para o GitHub

5. Abra o terminal (ou "Prompt de Comando" no Windows) **dentro da pasta deste projeto** (a pasta que contém `firebase.json`, `public/`, etc.).
6. Rode, um comando de cada vez:

```bash
git init
git add .
git commit -m "Primeira versão da plataforma"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/contabilidade-avancada.git
git push -u origin main
```

Pronto — seu código já está no GitHub. Sempre que quiser atualizar depois de uma mudança, basta rodar:

```bash
git add .
git commit -m "Descrição da mudança"
git push
```

---

## Parte 2 — Criar o projeto no Console do Firebase

1. Acesse **https://console.firebase.google.com** e faça login com uma conta Google.
2. Clique em **Adicionar projeto** (ou "Add project").
3. Dê um nome ao projeto, por exemplo `contabilidade-avancada`. O Firebase vai gerar um ID único (algo como `contabilidade-avancada-a1b2c`) — anote esse ID, você vai precisar dele mais adiante.
4. Você pode desativar o Google Analytics (não é necessário para este projeto). Clique em **Criar projeto** e aguarde.

### Ativar a Autenticação (login por e-mail e senha)

5. No menu à esquerda, clique em **Build → Authentication** → **Get started**.
6. Na aba **Sign-in method**, clique em **E-mail/senha**, ative a primeira opção (Email/Password) e clique em **Salvar**.

### Ativar o Firestore (banco de dados)

7. No menu à esquerda, clique em **Build → Firestore Database** → **Create database**.
8. Escolha **Modo de produção** (production mode) — nós já preparamos as regras de segurança certas no arquivo `firestore.rules`.
9. Escolha a localização mais próxima de você (ex.: `southamerica-east1` para o Brasil) e clique em **Ativar/Enable**.

### Ativar o Hosting

10. No menu à esquerda, clique em **Build → Hosting** → **Get started**. Você pode simplesmente seguir e fechar o assistente — vamos publicar pelo terminal, não é preciso rodar os comandos que ele sugere agora.

### Pegar as chaves de configuração do seu projeto

11. Clique no ícone de engrenagem (⚙️) ao lado de "Project Overview" → **Configurações do projeto**.
12. Role até **Seus aplicativos** e clique no ícone **</>** (Web) para registrar um app da Web. Dê um apelido (ex.: `plataforma-web`) e clique em **Registrar app**.
13. O Firebase vai te mostrar um bloco de código com `apiKey`, `authDomain`, `projectId`, etc. **Copie esses valores.**
14. Abra o arquivo `public/firebase-config.js` deste projeto e substitua os valores de exemplo pelos que você acabou de copiar. Salve o arquivo.

---

## Parte 3 — Instalar o Firebase CLI e publicar o site

1. No terminal, instale a ferramenta de linha de comando do Firebase (só precisa fazer isso uma vez no seu computador):

```bash
npm install -g firebase-tools
```

> Se o comando `npm` não existir, instale o Node.js primeiro em https://nodejs.org (baixe a versão "LTS").

2. Faça login com sua conta Google:

```bash
firebase login
```

3. Abra o arquivo `.firebaserc` deste projeto e troque `"SEU-PROJETO-ID"` pelo ID do seu projeto Firebase (o mesmo do passo 3 da Parte 2).

4. Publique as regras do Firestore:

```bash
firebase deploy --only firestore:rules
```

5. Publique o site:

```bash
firebase deploy --only hosting
```

6. Ao final, o terminal mostra um endereço parecido com `https://SEU-PROJETO-ID.web.app` — esse é o link da sua plataforma no ar. Abra no navegador para conferir.

Sempre que quiser publicar uma atualização, rode novamente `firebase deploy --only hosting`.

---

## Parte 4 — Criando suas contas

1. Abra o link do seu site publicado (`https://SEU-PROJETO-ID.web.app`).
2. Clique em **Criar conta**, informe nome, e-mail, senha e escolha o perfil **Professor** (é assim que você mesmo vai acessar a área do professor).
3. Peça para os alunos criarem a própria conta escolhendo o perfil **Aluno**.

### Criando um administrador

Por segurança, o cadastro público **não** oferece a opção "Admin" (só Aluno ou Professor) — assim ninguém consegue se autopromover a administrador.

Para criar um administrador:
1. Crie uma conta normalmente (como professor, por exemplo).
2. No Console do Firebase, vá em **Firestore Database** → coleção `users` → encontre o documento com o `uid` dessa pessoa (você pode identificar pelo campo `email`).
3. Edite o campo `role` de `"professor"` para `"admin"` e salve.
4. Na próxima vez que essa pessoa entrar na plataforma, ela verá o menu de administrador.

---

## Parte 5 (opcional) — Deploy automático a cada push no GitHub

Se quiser que o site seja publicado automaticamente sempre que você enviar uma atualização para o GitHub (sem precisar rodar `firebase deploy` manualmente):

1. No terminal, dentro da pasta do projeto, rode:
   ```bash
   firebase init hosting:github
   ```
2. Siga as instruções na tela — o próprio comando cria o segredo `FIREBASE_SERVICE_ACCOUNT` no seu repositório do GitHub e ajusta o workflow automaticamente.
3. Edite `.github/workflows/firebase-hosting-deploy.yml` e troque `SEU-PROJETO-ID` pelo ID real do seu projeto.

Se preferir não configurar isso agora, não tem problema — o arquivo do workflow fica parado sem causar erro, e você continua publicando com `firebase deploy --only hosting` manualmente.

---

## O que mudou em relação à versão de teste (artefato)

- **Login real:** antes era só digitar um nome; agora é conta de verdade com e-mail e senha (Firebase Authentication).
- **Dados permanentes:** progresso dos alunos, turmas, mensagens de suporte e o log de auditoria agora ficam no **Firestore**, o banco de dados do Firebase — não dependem mais do artefato do Claude.
- **Regras de segurança:** o arquivo `firestore.rules` define quem pode ler/escrever o quê. Hoje qualquer usuário autenticado (aluno, professor ou admin) pode ler e gravar no armazenamento compartilhado do app — adequado para o uso interno de uma turma, mas vale refinar antes de abrir a plataforma para um público maior (veja a próxima seção).

## Limitações atuais e próximos passos sugeridos

- **Identificação por nome, não por conta:** assim como na versão de teste, alunos e turmas são identificados pelo **nome** informado no cadastro (não pelo `uid` da conta). Isso significa que dois usuários com o mesmo nome compartilhariam os mesmos registros. Um próximo passo natural é migrar as chaves de armazenamento de "nome" para o `uid` do Firebase Auth — isso deixa tanto os dados quanto as regras de segurança mais robustos, mas exige uma nova rodada de ajustes no código.
- **Regras de acesso amplas:** hoje as regras liberam leitura/escrita para qualquer usuário autenticado no armazenamento compartilhado (`kv_store`). Funciona bem para uma turma que confia entre si, mas não é o ideal para uma plataforma aberta ao público. Posso ajudar a refinar isso por perfil e por dono do registro quando você quiser.
- **PDF de matrícula:** a extração de texto do PDF (para importar listas de alunos) continua rodando no navegador, sem mudanças.

Qualquer dúvida durante os passos acima, é só me chamar aqui que eu ajudo a resolver.

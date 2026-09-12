// =====================================================================
// Contabilidade Avançada — camada Firebase
// Este arquivo importa o SDK modular do Firebase (via CDN), inicializa
// Auth + Firestore, e expõe um pequeno "shim" (kvGet/kvSet/kvList) que
// imita a API de armazenamento chave-valor usada pelo resto do app,
// agora gravando/lendo do Firestore em vez do storage do artefato.
// =====================================================================
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import {
  getAuth, onAuthStateChanged, signOut,
  GoogleAuthProvider, signInWithPopup
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-auth.js";
import {
  getFirestore, doc, getDoc, setDoc, updateDoc, collection, getDocs, query,
  where, documentId
} from "https://www.gstatic.com/firebasejs/10.13.2/firebase-firestore.js";
import { firebaseConfig, MASTER_CODE } from "./firebase-config.js";

const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const db = getFirestore(firebaseApp);

// ---- kv shim: mimics the get/set/list(prefix) storage API used below ----
// Every record lives in a single Firestore collection ("kv_store"), with
// the document ID equal to the same key strings already used throughout
// the app (e.g. "student:Maria", "turma:turma_xxx", "audit:172..._ab12").
async function kvGet(key){
  const snap = await getDoc(doc(db, 'kv_store', key));
  if (!snap.exists()) return null;
  return { key, value: snap.data().value };
}
async function kvSet(key, value){
  await setDoc(doc(db, 'kv_store', key), { value, updatedAt: Date.now() });
  return { key, value };
}
async function kvList(prefix){
  const kvRef = collection(db, 'kv_store');
  const q = query(kvRef, where(documentId(), '>=', prefix), where(documentId(), '<', prefix + '\uf8ff'));
  const snap = await getDocs(q);
  const keys = [];
  snap.forEach(d => keys.push(d.id));
  return { keys };
}


(function(){
  const root = document.getElementById('cont-avancada');

  // ---------------------------------------------------------------------
  // Helpers to build exercise-list items compactly
  // mc(q, opts, correctIndex, note)  |  vf(q, correctBool, note)
  // ---------------------------------------------------------------------
  function mc(q, opts, correct, note){ return { type:'mc', q, opts, correct, note: note||'' }; }
  function vf(q, correct, note){ return { type:'vf', q, correct, note: note||'' }; }

  const MODULES = [
    // =====================================================================
    // MODULE 1
    // =====================================================================
    {
      id:'m1', num:1, color:'#A87C3F',
      title:'Provisão da Folha de Pagamento',
      subtitle:'Salário, Férias, 13º Salário e Rescisão',
      content: `
        <h4>Regime de competência</h4>
        <p>As obrigações trabalhistas devem ser reconhecidas no período em que o direito é gerado pelo empregado, independentemente da data de pagamento. Isso exige que a empresa constitua provisões mensais para férias, 13º salário e os encargos sociais correspondentes.</p>

        <h4>Provisão de férias</h4>
        <p>A cada mês trabalhado, o empregado adquire 1/12 avos do direito a férias, mais o adicional constitucional de 1/3. A provisão mensal é lançada a débito de despesa e a crédito de uma conta de passivo (Provisão de Férias a Pagar).</p>

        <h4>Provisão de 13º salário</h4>
        <p>Segue a mesma lógica de 1/12 avos por mês trabalhado, mas sem o adicional de 1/3 (que é exclusivo das férias).</p>

        <h4>Encargos sociais sobre as provisões</h4>
        <p>Sobre férias e 13º incidem encargos patronais — INSS patronal (didaticamente considerado 20%) e FGTS (8%) — que também devem ser provisionados no mesmo período de competência.</p>

        <h4>Exemplo — salário mensal de R$ 3.000,00</h4>
        <table class="ledger">
          <tr><th>Item</th><th>Cálculo</th><th class="num">Valor</th></tr>
          <tr><td>Provisão de férias (1/12)</td><td>3.000 ÷ 12</td><td class="num">R$ 250,00</td></tr>
          <tr><td>1/3 constitucional</td><td>250 × 1/3</td><td class="num">R$ 83,33</td></tr>
          <tr><td>Provisão de 13º (1/12)</td><td>3.000 ÷ 12</td><td class="num">R$ 250,00</td></tr>
          <tr><td><b>Subtotal das provisões</b></td><td></td><td class="num"><b>R$ 583,33</b></td></tr>
          <tr><td>Encargos sociais (28%)</td><td>583,33 × 28%</td><td class="num">R$ 163,33</td></tr>
          <tr><td><b>Total provisionado no mês</b></td><td></td><td class="num"><b>R$ 746,66</b></td></tr>
        </table>

        <h4>Lançamento contábil</h4>
        <div class="journal mono">
          <div class="d">D – Despesa com Férias e 13º Salário <span class="val">583,33</span></div>
          <div class="d">D – Despesa com Encargos Sociais <span class="val">163,33</span></div>
          <div class="c">C – Provisão de Férias a Pagar <span class="val">333,33</span></div>
          <div class="c">C – Provisão de 13º Salário a Pagar <span class="val">250,00</span></div>
          <div class="c">C – Provisão de Encargos s/ Férias e 13º <span class="val">163,33</span></div>
        </div>

        <h4>Rescisão contratual</h4>
        <p>No desligamento, reverte-se a provisão acumulada do funcionário e apuram-se as verbas rescisórias: saldo de salário, aviso prévio, férias vencidas e proporcionais + 1/3, 13º proporcional e, em demissão sem justa causa, a multa de 40% sobre o saldo do FGTS.</p>
      `,
      exerciseLists: [
        { title:'Lista 1 — Conceitos gerais', items:[
          vf('A provisão da folha de pagamento segue o regime de competência.', true),
          vf('As provisões de férias e 13º podem ser reconhecidas apenas no mês do pagamento.', false),
          mc('Qual conta recebe o crédito na provisão mensal de férias?', ['Despesa com férias','Provisão de Férias a Pagar (passivo)','Caixa','Receita diferida'], 1),
          vf('O adicional de 1/3 constitucional incide sobre o 13º salário.', false),
          mc('O 13º salário provisionado mensalmente corresponde a:', ['1/13 do salário','1/12 do salário','1/10 do salário','Valor fixo definido em lei'], 1),
          vf('A provisão de férias é lançada no passivo circulante.', true),
          mc('Os encargos sociais tipicamente provisionados sobre férias e 13º são:', ['ICMS e ISS','INSS patronal e FGTS','PIS e COFINS','IPI e IOF'], 1),
          vf('A provisão mensal de férias e 13º reduz o resultado do exercício em que é constituída.', true),
          mc('Ao pagar as férias efetivamente, a empresa deve:', ['Lançar nova despesa integral','Baixar a provisão constituída anteriormente','Ignorar a provisão','Lançar como receita'], 1),
          vf('A provisão de férias e 13º só é obrigatória para empresas do Lucro Real.', false, 'É consequência do regime de competência, exigido também por outras normas contábeis.')
        ]},
        { title:'Lista 2 — Cálculo de férias', items:[
          mc('Salário de R$ 2.400,00: qual a provisão mensal de férias, sem o 1/3?', ['R$ 180,00','R$ 200,00','R$ 240,00','R$ 300,00'], 1),
          mc('Sobre a provisão de R$ 200,00, qual o valor do 1/3 constitucional?', ['R$ 50,00','R$ 66,67','R$ 100,00','R$ 80,00'], 1),
          mc('Total da provisão de férias (com 1/3) para salário de R$ 2.400,00:', ['R$ 240,00','R$ 266,67','R$ 300,00','R$ 320,00'], 1),
          vf('A provisão de férias sempre é igual a 1/12 do salário, sem qualquer acréscimo.', false),
          mc('Salário de R$ 3.600,00: provisão de férias base (1/12):', ['R$ 250,00','R$ 300,00','R$ 360,00','R$ 400,00'], 1),
          mc('Sobre R$ 300,00, o 1/3 constitucional equivale a:', ['R$ 80,00','R$ 90,00','R$ 100,00','R$ 120,00'], 2),
          mc('Total da provisão de férias (com 1/3) para salário de R$ 3.600,00:', ['R$ 375,00','R$ 390,00','R$ 400,00','R$ 410,00'], 2),
          vf('O 1/3 constitucional é sempre um terço do salário integral do empregado.', false, 'É um terço da provisão de férias (1/12), não do salário integral.'),
          mc('Salário de R$ 5.000,00: provisão de férias base (1/12):', ['R$ 400,00','R$ 416,67','R$ 450,00','R$ 500,00'], 1),
          mc('Sobre R$ 416,67, o 1/3 constitucional equivale, aproximadamente, a:', ['R$ 100,00','R$ 120,00','R$ 138,89','R$ 150,00'], 2)
        ]},
        { title:'Lista 3 — Cálculo de 13º e encargos', items:[
          mc('Salário de R$ 3.000,00: provisão mensal de 13º salário:', ['R$ 225,00','R$ 250,00','R$ 275,00','R$ 300,00'], 1),
          vf('A provisão do 13º salário inclui o adicional de 1/3.', false),
          mc('Salário de R$ 4.200,00: provisão mensal de 13º salário:', ['R$ 300,00','R$ 350,00','R$ 375,00','R$ 400,00'], 1),
          mc('Somando férias com 1/3 (R$ 333,33) e 13º (R$ 250,00) para salário de R$ 3.000,00, o subtotal é:', ['R$ 550,00','R$ 583,33','R$ 600,00','R$ 620,00'], 1),
          mc('Aplicando 28% de encargos sociais sobre R$ 583,33, o valor é, aproximadamente:', ['R$ 140,00','R$ 150,00','R$ 163,33','R$ 180,00'], 2),
          vf('O percentual de encargos sociais é sempre uniforme e nunca varia entre empresas.', false, 'Varia conforme o regime tributário e a atividade da empresa.'),
          mc('Total mensal provisionado no exemplo do módulo (subtotal + encargos):', ['R$ 700,00','R$ 746,66','R$ 800,00','R$ 650,00'], 1),
          vf('O FGTS incide sobre os valores de férias e 13º provisionados.', true),
          mc('Alíquota didática de FGTS utilizada no exemplo do módulo:', ['5%','8%','11%','13%'], 1),
          vf('O INSS patronal utilizado no exemplo didático do módulo foi de 20%.', true)
        ]},
        { title:'Lista 4 — Lançamentos contábeis', items:[
          mc('A provisão mensal de férias e 13º é lançada com débito em:', ['Ativo circulante','Despesa do período','Patrimônio líquido','Receita'], 1),
          vf('O crédito da provisão de férias é lançado em uma conta de resultado.', false, 'O crédito vai para uma conta de passivo (obrigação futura).'),
          mc('Ao pagar efetivamente as férias já provisionadas, o lançamento típico é:', ['D-Provisão de Férias / C-Caixa','D-Caixa / C-Provisão de Férias','D-Despesa / C-Caixa, sem baixar a provisão','D-Receita / C-Caixa'], 0),
          vf('Não baixar a provisão ao pagar as férias gera duplicidade de despesa.', true),
          mc('A provisão de encargos sociais sobre férias e 13º é lançada a crédito de:', ['Despesa','Provisão de Encargos Sociais (passivo)','Receita diferida','Ativo'], 1),
          vf('As contas de provisão de férias e 13º são classificadas no Ativo Circulante.', false),
          mc('O grupo contábil mais adequado para "Provisão de Férias a Pagar" é:', ['Ativo não circulante','Passivo circulante','Patrimônio líquido','Ativo circulante'], 1),
          vf('A reversão (baixa) da provisão ocorre no momento do efetivo pagamento ao empregado.', true),
          mc('Se a empresa não constituir a provisão mensalmente, o resultado do período fica:', ['Subavaliado em despesas (lucro superestimado)','Correto','Superavaliado em despesas','Não é afetado'], 0),
          vf('A provisão da folha de pagamento é uma aplicação prática do princípio da competência.', true)
        ]},
        { title:'Lista 5 — Rescisão e revisão geral', items:[
          mc('Em demissão sem justa causa, a multa sobre o saldo do FGTS é de:', ['10%','20%','40%','50%'], 2),
          vf('Em pedido de demissão pelo próprio empregado, há multa de 40% sobre o FGTS.', false),
          mc('São verbas rescisórias típicas, EXCETO:', ['Saldo de salário','Férias proporcionais + 1/3','13º salário proporcional','Provisão para contingências'], 3),
          vf('O aviso prévio pode ser trabalhado ou indenizado.', true),
          mc('As férias proporcionais pagas na rescisão são calculadas:', ['Sem o adicional de 1/3','Com o adicional de 1/3','Apenas se já vencidas','Nunca são pagas'], 1),
          vf('A provisão acumulada do funcionário é revertida (baixada) no momento da rescisão.', true),
          mc('O 13º salário proporcional pago na rescisão considera:', ['Os meses trabalhados no ano até a rescisão','Apenas o último mês','O salário mínimo vigente','Não é devido em rescisão'], 0),
          vf('Mesmo em rescisão por justa causa, o empregado tem direito às férias vencidas.', true),
          mc('O principal objetivo da provisão mensal de férias e 13º é:', ['Reduzir o lucro tributável','Reconhecer a despesa no período de competência do direito','Antecipar o pagamento do imposto de renda','Aumentar o caixa da empresa'], 1),
          vf('As provisões trabalhistas fazem parte do passivo circulante da empresa.', true)
        ]}
      ],
      quiz: [
        { q:'A provisão de férias e 13º salário é constituída em qual regime contábil?', opts:['Regime de caixa','Regime de competência','Regime misto','Regime de competência apenas para 13º'], correct:1,
          explain:'A obrigação nasce quando o direito é adquirido pelo empregado, mês a mês — regime de competência.' },
        { q:'O adicional de 1/3 constitucional se aplica a qual verba?', opts:['13º salário','Férias','Aviso prévio','FGTS'], correct:1,
          explain:'O 1/3 constitucional (art. 7º, XVII, CF/88) incide sobre as férias, não sobre o 13º.' },
        { q:'Sobre a provisão de férias e 13º incidem, tipicamente, quais encargos patronais?', opts:['Apenas IRRF','INSS patronal e FGTS','Apenas ISS','PIS e COFINS'], correct:1,
          explain:'INSS patronal e FGTS são os encargos sociais que a empresa deve provisionar sobre a folha.' },
        { q:'Em uma demissão sem justa causa, qual multa incide sobre o saldo do FGTS?', opts:['20%','40%','10%','Não há multa'], correct:1,
          explain:'A multa rescisória do FGTS em demissão sem justa causa é de 40% sobre os depósitos.' },
        { q:'A provisão mensal de férias é lançada como:', opts:['Débito de ativo e crédito de despesa','Débito de despesa e crédito de passivo','Débito de passivo e crédito de receita','Débito de patrimônio líquido'], correct:1,
          explain:'Debita-se a despesa do período e credita-se uma conta de provisão no passivo (obrigação futura).' }
      ],
      recovery: [
        { q:'A provisão mensal de férias representa:', opts:['1/12 do salário + 1/3','1/10 do salário','Um valor fixo definido pela empresa','1/6 do salário'], correct:0,
          explain:'A cada mês, o empregado adquire 1/12 do direito a férias, acrescido do 1/3 constitucional.' },
        { q:'O 13º salário é regido por qual regime contábil?', opts:['Regime de caixa','Regime de competência','Regime misto','Nenhum regime específico'], correct:1,
          explain:'Assim como as férias, o 13º segue o regime de competência.' },
        { q:'A multa do FGTS na demissão sem justa causa é de:', opts:['10%','40%','20%','0%'], correct:1,
          explain:'A multa rescisória é de 40% sobre o saldo do FGTS.' },
        { q:'O encargo social geralmente somado ao INSS na provisão da folha é:', opts:['FGTS','IOF','ISS','ICMS'], correct:0,
          explain:'FGTS e INSS patronal são os encargos sociais típicos sobre a folha de pagamento.' },
        { q:'O saldo da conta "Provisão de Férias a Pagar" é classificado como:', opts:['Ativo','Passivo','Patrimônio líquido','Receita'], correct:1,
          explain:'É uma obrigação da empresa com o empregado, portanto passivo circulante.' }
      ]
    },

    // =====================================================================
    // MODULE 2
    // =====================================================================
    {
      id:'m2', num:2, color:'#2F5233',
      title:'Apuração do Resultado do Exercício — LALUR',
      subtitle:'Do lucro contábil ao lucro real',
      content:`
        <h4>O que é o LALUR</h4>
        <p>O Livro de Apuração do Lucro Real (hoje escriturado digitalmente como e-LALUR, parte da ECF) é o instrumento em que a empresa ajusta o lucro contábil para chegar à base de cálculo do IRPJ e da CSLL, sem alterar a contabilidade societária.</p>

        <h4>Parte A e Parte B</h4>
        <p>A <b>Parte A</b> registra os ajustes do próprio período: adições, exclusões e compensações que afetam a apuração do lucro real daquele ano. A <b>Parte B</b> é um controle de valores que impactarão períodos futuros — por exemplo, o saldo de prejuízos fiscais a compensar ou diferenças temporárias ainda não realizadas.</p>

        <h4>Adições</h4>
        <p>Somam-se ao lucro líquido contábil as despesas contabilizadas que a legislação fiscal não permite deduzir naquele período — por exemplo, multas de natureza fiscal não dedutíveis, doações fora das hipóteses legais, e provisões constituídas sem amparo legal (como PDD não homologada).</p>

        <h4>Exclusões</h4>
        <p>Subtraem-se do lucro líquido as receitas contabilizadas que a lei não tributa, ou despesas dedutíveis fiscalmente que não passaram pelo resultado contábil — por exemplo, a reversão de uma provisão que já havia sido adicionada em período anterior.</p>

        <h4>Compensação de prejuízos fiscais</h4>
        <p>Prejuízos fiscais de períodos anteriores podem ser compensados, mas a lei limita essa compensação a 30% do lucro real apurado antes da própria compensação — a chamada "trava dos 30%".</p>

        <h4>Exemplo de apuração</h4>
        <table class="ledger">
          <tr><th>Item</th><th class="num">Valor</th></tr>
          <tr><td>Lucro líquido contábil (antes do IR/CSLL)</td><td class="num">R$ 500.000,00</td></tr>
          <tr><td>(+) Multas fiscais indedutíveis</td><td class="num">R$ 10.000,00</td></tr>
          <tr><td>(+) Provisão para contingência sem amparo legal</td><td class="num">R$ 20.000,00</td></tr>
          <tr><td>(−) Reversão de provisão já tributada em período anterior</td><td class="num">R$ 5.000,00</td></tr>
          <tr><td><b>Lucro real antes da compensação</b></td><td class="num"><b>R$ 525.000,00</b></td></tr>
          <tr><td>(−) Compensação de prejuízo fiscal (limite 30% = R$157.500; saldo disponível R$100.000)</td><td class="num">R$ 100.000,00</td></tr>
          <tr><td><b>Lucro real do período</b></td><td class="num"><b>R$ 425.000,00</b></td></tr>
        </table>
        <p>Sobre o lucro real aplicam-se 15% de IRPJ, mais adicional de 10% sobre o que exceder R$ 20.000,00/mês (R$ 240.000,00/ano), e 9% de CSLL.</p>
      `,
      exerciseLists: [
        { title:'Lista 1 — Conceitos gerais', items:[
          vf('O LALUR é uma escrituração exclusivamente fiscal e não altera a contabilidade societária.', true),
          mc('A Parte A do LALUR registra:', ['Ajustes do próprio período','Apenas prejuízos futuros','Somente receitas isentas','Nada relevante para a apuração'], 0),
          vf('A Parte B controla valores que afetarão períodos futuros.', true),
          mc('O lucro real é obtido a partir do lucro líquido contábil por meio de:', ['Adições e exclusões','Apenas exclusões','Apenas adições','Reavaliação de ativos imobilizados'], 0),
          vf('Despesas contabilizadas mas indedutíveis fiscalmente devem ser excluídas do lucro líquido.', false, 'Devem ser adicionadas, não excluídas.'),
          mc('Uma receita não tributável, contabilizada como receita, deve ser:', ['Adicionada','Excluída','Ignorada','Compensada como prejuízo'], 1),
          vf('O regime do Lucro Real é obrigatório apenas para optantes do Simples Nacional.', false),
          mc('O e-LALUR atualmente é escriturado dentro de qual obrigação acessória?', ['DCTF','ECF','DIRF','GFIP'], 1),
          vf('Multas fiscais indedutíveis contabilizadas como despesa geram adição ao lucro líquido.', true),
          mc('A finalidade do LALUR é:', ['Apurar o ICMS devido','Apurar a base de cálculo do IRPJ e da CSLL','Apurar o Simples Nacional','Apurar o FGTS devido'], 1)
        ]},
        { title:'Lista 2 — Adições e exclusões', items:[
          mc('Lucro contábil de R$ 200.000,00 + adição de R$ 10.000,00 (multa indedutível): lucro ajustado:', ['R$ 190.000,00','R$ 200.000,00','R$ 210.000,00','R$ 220.000,00'], 2),
          mc('Do valor acima, com exclusão de R$ 5.000,00 (receita isenta): lucro real antes da compensação:', ['R$ 200.000,00','R$ 205.000,00','R$ 210.000,00','R$ 215.000,00'], 1),
          vf('Uma provisão constituída sem amparo legal gera adição ao lucro líquido.', true),
          mc('Lucro contábil R$ 150.000,00, adição de R$ 8.000,00, exclusão de R$ 3.000,00: lucro real:', ['R$ 145.000,00','R$ 153.000,00','R$ 155.000,00','R$ 158.000,00'], 2),
          vf('A receita de dividendos recebidos de outra empresa costuma ser excluída, por já ter sido tributada na origem.', true),
          mc('Se as adições superam as exclusões, o lucro real tende a ficar:', ['Maior que o lucro contábil','Menor que o lucro contábil','Sempre igual ao contábil','Sempre zero'], 0),
          vf('Se as exclusões superam as adições, o lucro real fica menor que o lucro contábil.', true),
          mc('Lucro contábil R$ 400.000,00, adições R$ 50.000,00, exclusões R$ 20.000,00: lucro real antes da compensação:', ['R$ 410.000,00','R$ 420.000,00','R$ 430.000,00','R$ 450.000,00'], 2),
          vf('Toda despesa contabilizada é automaticamente dedutível para fins fiscais.', false),
          mc('A reversão de uma provisão adicionada em período anterior deve ser, no período da reversão:', ['Adicionada novamente','Excluída','Ignorada','Compensada como prejuízo fiscal'], 1)
        ]},
        { title:'Lista 3 — Compensação de prejuízos fiscais', items:[
          mc('A trava de compensação de prejuízos fiscais é de:', ['20%','30%','50%','100%'], 1),
          vf('A trava dos 30% é calculada sobre o lucro líquido contábil.', false, 'É calculada sobre o lucro real antes da própria compensação.'),
          mc('Lucro real antes da compensação R$ 100.000,00, prejuízo acumulado R$ 50.000,00: limite de compensação no período:', ['R$ 20.000,00','R$ 30.000,00','R$ 50.000,00','R$ 100.000,00'], 1),
          mc('No exemplo acima, o saldo de prejuízo fiscal a compensar em períodos futuros é:', ['R$ 0,00','R$ 20.000,00','R$ 30.000,00','R$ 50.000,00'], 1),
          vf('O saldo de prejuízo fiscal não compensado em um período se perde ao final do exercício.', false, 'Pode ser compensado em exercícios futuros, sempre respeitada a trava de 30%.'),
          mc('Lucro real antes da compensação R$ 300.000,00, prejuízo acumulado R$ 40.000,00: valor efetivamente compensado no período:', ['R$ 30.000,00','R$ 40.000,00','R$ 90.000,00','R$ 300.000,00'], 1),
          vf('A trava dos 30% existe para garantir arrecadação mínima de IRPJ/CSLL mesmo havendo prejuízos anteriores.', true),
          mc('Os prejuízos fiscais a compensar são controlados em qual parte do LALUR?', ['Parte A','Parte B','Não são controlados no LALUR','Na DCTF'], 1),
          vf('Empresas do Lucro Presumido também compensam prejuízos fiscais pelo LALUR.', false, 'O LALUR e a compensação de prejuízos fiscais são próprios do regime do Lucro Real.'),
          mc('Lucro real antes da compensação de R$ 500.000,00: limite máximo de compensação de prejuízos:', ['R$ 100.000,00','R$ 150.000,00','R$ 200.000,00','R$ 250.000,00'], 1)
        ]},
        { title:'Lista 4 — IRPJ e CSLL sobre o lucro real', items:[
          mc('A alíquota básica do IRPJ sobre o lucro real é:', ['10%','15%','20%','25%'], 1),
          vf('Há um adicional de 10% de IRPJ sobre a parcela do lucro que exceder R$ 20.000,00 por mês.', true),
          mc('O limite anual equivalente ao adicional de IRPJ (sem adicional) é de:', ['R$ 120.000,00','R$ 180.000,00','R$ 240.000,00','R$ 300.000,00'], 2),
          vf('A alíquota da CSLL para as empresas em geral é de 9%.', true),
          mc('Lucro real de R$ 400.000,00 no ano: parcela sujeita ao adicional de 10% (limite anual de R$240.000,00):', ['R$ 0,00','R$ 160.000,00','R$ 240.000,00','R$ 400.000,00'], 1),
          mc('IRPJ total (15% + adicional) sobre lucro real de R$ 400.000,00, considerando adicional sobre R$ 160.000,00:', ['R$ 60.000,00','R$ 76.000,00','R$ 90.000,00','R$ 100.000,00'], 1, '400.000×15% = 60.000; 160.000×10% = 16.000; total = 76.000.'),
          vf('O adicional de IRPJ se aplica a todas as empresas, independentemente do lucro apurado no período.', false),
          mc('CSLL (9%) sobre lucro real de R$ 400.000,00:', ['R$ 30.000,00','R$ 36.000,00','R$ 40.000,00','R$ 45.000,00'], 1),
          vf('IRPJ e CSLL sempre têm exatamente a mesma base de cálculo, sem qualquer ajuste específico.', false, 'A CSLL possui ajustes próprios, que podem diferir dos ajustes do IRPJ.'),
          mc('No exemplo do módulo, IRPJ e CSLL incidem sobre um lucro real de:', ['R$ 300.000,00','R$ 425.000,00','R$ 500.000,00','R$ 100.000,00'], 1)
        ]},
        { title:'Lista 5 — Revisão geral', items:[
          vf('O LALUR gera lançamentos contábeis próprios na escrituração societária da empresa.', false),
          mc('O principal objetivo do LALUR é:', ['Ajustar o lucro contábil à base de cálculo fiscal','Substituir o balanço patrimonial','Calcular o ICMS devido','Apurar o PIS e a COFINS'], 0),
          vf('Todas as empresas, independentemente do regime tributário, são obrigadas a escriturar o LALUR.', false, 'É obrigatório para as empresas tributadas pelo Lucro Real.'),
          mc('Uma adição aumenta o lucro real porque representa:', ['Despesa contabilizada mas não dedutível fiscalmente','Receita isenta','Compensação de prejuízo fiscal','Receita tributável ainda não contabilizada'], 0),
          vf('Uma exclusão diminui o lucro real em relação ao lucro contábil.', true),
          mc('A trava dos 30% se aplica especificamente a:', ['Compensação de prejuízos fiscais','Adições em geral','Exclusões em geral','Cálculo do FGTS'], 0),
          vf('O lucro real pode ser menor que o lucro contábil, dependendo das exclusões apuradas.', true),
          mc('Assinale a alternativa correta sobre o e-LALUR:', ['É parte da ECF (Escrituração Contábil Fiscal)','É parte do SPED Fiscal de ICMS/IPI','É parte da GFIP','Não existe mais atualmente'], 0),
          vf('Despesas com multas de trânsito são, em regra, indedutíveis para fins fiscais.', true),
          mc('Uma diferença temporária controlada na Parte B do LALUR se caracteriza por:', ['Um valor que afetará o lucro real em período futuro','Uma receita definitivamente isenta','Um erro contábil a ser corrigido','Uma despesa sempre dedutível'], 0)
        ]}
      ],
      quiz:[
        { q:'O LALUR tem por finalidade:', opts:['Substituir a escrituração contábil','Ajustar o lucro contábil para apurar a base fiscal do IRPJ/CSLL','Calcular o ICMS devido','Registrar apenas receitas isentas'], correct:1,
          explain:'É um livro fiscal de ajuste, não uma escrituração contábil societária.' },
        { q:'Uma despesa contabilizada mas não dedutível fiscalmente deve ser:', opts:['Excluída no LALUR','Adicionada no LALUR','Ignorada','Lançada como receita'], correct:1,
          explain:'Despesas indedutíveis são somadas (adicionadas) de volta ao lucro contábil para achar o lucro real.' },
        { q:'A Parte B do LALUR serve para:', opts:['Ajustes definitivos do próprio período','Controlar valores que afetarão períodos futuros','Calcular o dividendo obrigatório','Apurar o ganho de capital'], correct:1,
          explain:'A Parte B controla saldos como prejuízos fiscais e diferenças temporárias a compensar depois.' },
        { q:'A compensação de prejuízos fiscais é limitada a que percentual do lucro real do período?', opts:['20%','30%','50%','100%'], correct:1,
          explain:'A "trava dos 30%" limita a compensação de prejuízos fiscais em cada período de apuração.' },
        { q:'A reversão de uma provisão que já havia sido adicionada em período anterior deve ser, no período da reversão:', opts:['Adicionada novamente','Excluída, pois já foi tributada antes','Ignorada','Compensada como prejuízo'], correct:1,
          explain:'Para evitar dupla tributação, a reversão é excluída no período em que volta a compor o resultado contábil.' }
      ],
      recovery:[
        { q:'A Parte A do LALUR trata de:', opts:['Ajustes do próprio período','Apenas valores futuros','Nenhum tipo de ajuste','Apenas compensações antigas'], correct:0,
          explain:'A Parte A registra adições, exclusões e compensações do período corrente.' },
        { q:'A trava de compensação de prejuízos fiscais é de:', opts:['10%','30%','50%','70%'], correct:1,
          explain:'A compensação é limitada a 30% do lucro real apurado antes da própria compensação.' },
        { q:'O adicional de IRPJ incide sobre o que exceder, por mês:', opts:['R$ 10.000,00','R$ 20.000,00','R$ 30.000,00','R$ 40.000,00'], correct:1,
          explain:'O adicional de 10% incide sobre a parcela do lucro real que exceder R$20.000,00 por mês.' },
        { q:'A alíquota da CSLL para as empresas em geral é de:', opts:['7%','9%','12%','15%'], correct:1,
          explain:'A CSLL das empresas em geral corresponde a 9% sobre a base ajustada.' },
        { q:'Uma despesa indedutível fiscalmente deve ser:', opts:['Excluída','Adicionada','Ignorada','Compensada'], correct:1,
          explain:'Despesas indedutíveis somam-se (adicionam-se) de volta ao lucro contábil.' }
      ]
    },

    // =====================================================================
    // MODULE 3
    // =====================================================================
    {
      id:'m3', num:3, color:'#1C2B39',
      title:'Destinação do Resultado do Exercício',
      subtitle:'Participações, Reservas, Reserva de Lucros e Dividendos',
      content:`
        <h4>Ordem legal de destinação (Lei 6.404/76)</h4>
        <p>Apurado o lucro líquido do exercício, a Lei das S.A. estabelece uma sequência para sua destinação:</p>
        <ul>
          <li>Absorção de prejuízos acumulados, se houver;</li>
          <li>Participações estatutárias, na ordem: debenturistas, empregados, administradores e partes beneficiárias (art. 190);</li>
          <li>Reserva legal: 5% do lucro líquido do exercício, até atingir 20% do capital social (art. 193);</li>
          <li>Reservas estatutárias, se previstas no estatuto;</li>
          <li>Dividendo obrigatório: definido no estatuto ou, no silêncio deste, 50% do lucro líquido ajustado (art. 202);</li>
          <li>Reserva de lucros a realizar ou de retenção de lucros, quando houver orçamento de capital aprovado.</li>
        </ul>

        <h4>Participação de empregados e administradores</h4>
        <p>Calculada sobre o lucro antes da provisão para IR/CSLL ou sobre o lucro líquido, conforme definido em lei ou estatuto, e contabilizada como despesa do próprio exercício — reduz o lucro líquido a ser posteriormente destinado às reservas e dividendos.</p>

        <h4>Reserva legal</h4>
        <p>Obrigatória para todas as sociedades por ações, tem por finalidade assegurar a integridade do capital social. Não precisa mais ser constituída quando seu saldo, somado às reservas de capital, atingir 30% do capital social.</p>

        <h4>Dividendo obrigatório</h4>
        <p>É a parcela mínima do lucro que deve ser distribuída aos acionistas. Se o estatuto for omisso, aplica-se a regra supletiva de 50% do lucro líquido ajustado (lucro líquido menos as reservas legal e de contingência, mais a reversão de reservas anteriores).</p>

        <h4>Exemplo de destinação</h4>
        <table class="ledger">
          <tr><th>Item</th><th class="num">Valor</th></tr>
          <tr><td>Lucro líquido do exercício</td><td class="num">R$ 1.000.000,00</td></tr>
          <tr><td>(−) Participação de empregados (10%)</td><td class="num">R$ 100.000,00</td></tr>
          <tr><td><b>Base para reserva legal</b></td><td class="num"><b>R$ 900.000,00</b></td></tr>
          <tr><td>(−) Reserva legal (5%)</td><td class="num">R$ 45.000,00</td></tr>
          <tr><td><b>Lucro líquido ajustado</b></td><td class="num"><b>R$ 855.000,00</b></td></tr>
          <tr><td>Dividendo obrigatório estatutário (25%)</td><td class="num">R$ 213.750,00</td></tr>
          <tr><td>Reserva estatutária (saldo remanescente)</td><td class="num">R$ 641.250,00</td></tr>
        </table>
      `,
      exerciseLists: [
        { title:'Lista 1 — Conceitos e ordem legal', items:[
          vf('A Lei 6.404/76 estabelece uma ordem legal para a destinação do lucro líquido.', true),
          mc('A primeira destinação, quando existente, é:', ['Dividendos','Absorção de prejuízos acumulados','Reserva legal','Participação de administradores'], 1),
          vf('As participações estatutárias antecedem a reserva legal na ordem de destinação.', true),
          mc('A ordem das participações estatutárias no art. 190 é:', ['Empregados, debenturistas, administradores','Debenturistas, empregados, administradores e partes beneficiárias','Administradores, empregados, debenturistas','Não há ordem definida em lei'], 1),
          vf('A reserva legal é facultativa para companhias abertas.', false),
          mc('A reserva legal corresponde a:', ['5% do lucro líquido, até 20% do capital social','10% do lucro líquido, sem limite','1% do lucro líquido','15% do capital social'], 0),
          vf('O dividendo obrigatório é sempre a última destinação possível na ordem legal.', false, 'Após ele ainda pode haver reserva de lucros a realizar ou de retenção de lucros.'),
          mc('Na omissão do estatuto quanto ao dividendo, aplica-se:', ['25% do lucro líquido','50% do lucro líquido ajustado','100% do lucro líquido','Nenhum dividendo é devido'], 1),
          vf('A participação de empregados é contabilizada como despesa do próprio exercício.', true),
          mc('A reserva legal deixa de ser obrigatória quando, somada às reservas de capital, atinge:', ['10% do capital social','20% do capital social','30% do capital social','50% do capital social'], 2)
        ]},
        { title:'Lista 2 — Participações e reserva legal', items:[
          mc('Lucro líquido de R$ 800.000,00, participação de empregados de 10%: valor da participação:', ['R$ 70.000,00','R$ 80.000,00','R$ 90.000,00','R$ 100.000,00'], 1),
          mc('Base para reserva legal após a participação acima:', ['R$ 700.000,00','R$ 720.000,00','R$ 730.000,00','R$ 800.000,00'], 1),
          mc('Reserva legal (5%) sobre R$ 720.000,00:', ['R$ 32.000,00','R$ 35.000,00','R$ 36.000,00','R$ 40.000,00'], 2),
          vf('A participação de empregados é calculada sobre o lucro já líquido de todas as reservas.', false, 'É calculada antes, reduzindo o lucro que servirá de base às demais destinações.'),
          mc('Lucro líquido ajustado após a reserva legal do exemplo acima:', ['R$ 650.000,00','R$ 684.000,00','R$ 700.000,00','R$ 720.000,00'], 1),
          vf('A reserva legal é sempre 5% do lucro líquido, independentemente do saldo já acumulado.', false, 'Só até atingir o limite de 20% do capital social.'),
          mc('Lucro líquido de R$ 500.000,00, sem participação de empregados: reserva legal (5%):', ['R$ 15.000,00','R$ 20.000,00','R$ 25.000,00','R$ 30.000,00'], 2),
          vf('Se a reserva legal já atingiu o teto de 20% do capital social, a empresa deixa de constituí-la naquele exercício.', true),
          mc('Lucro líquido de R$ 1.200.000,00, participação de administradores de 5%: valor da participação:', ['R$ 50.000,00','R$ 55.000,00','R$ 60.000,00','R$ 70.000,00'], 2),
          mc('Capital social de R$ 2.000.000,00: teto da reserva legal (20%):', ['R$ 200.000,00','R$ 300.000,00','R$ 400.000,00','R$ 500.000,00'], 2)
        ]},
        { title:'Lista 3 — Dividendos', items:[
          mc('Lucro líquido ajustado de R$ 900.000,00, dividendo obrigatório estatutário de 30%:', ['R$ 250.000,00','R$ 270.000,00','R$ 280.000,00','R$ 300.000,00'], 1),
          vf('O dividendo obrigatório mínimo, na omissão do estatuto, é de 50% do lucro líquido ajustado.', true),
          mc('Lucro líquido ajustado de R$ 600.000,00, estatuto omisso: dividendo obrigatório mínimo:', ['R$ 150.000,00','R$ 200.000,00','R$ 300.000,00','R$ 600.000,00'], 2),
          vf('Os dividendos são distribuídos aos acionistas conforme sua participação no capital social.', true),
          mc('O dividendo obrigatório pode ser reduzido ou suspenso quando:', ['Os administradores decidirem sozinhos, sem justificativa','Os órgãos sociais informarem que é incompatível com a situação financeira da companhia, nos termos da lei','Nunca pode ser suspenso','Apenas por decisão judicial'], 1),
          vf('Ações preferenciais podem ter prioridade no recebimento de dividendos, conforme previsto no estatuto.', true),
          mc('Lucro líquido ajustado de R$ 1.000.000,00, dividendo obrigatório de 40%:', ['R$ 350.000,00','R$ 400.000,00','R$ 450.000,00','R$ 500.000,00'], 1),
          vf('O pagamento de dividendos reduz o patrimônio líquido da companhia.', true),
          mc('O saldo do lucro líquido ajustado que não vira dividendo nem reserva legal pode ser destinado a:', ['Reserva estatutária ou de retenção de lucros','Despesas do exercício seguinte','Ativo intangível','Conta de compensação'], 0),
          vf('Dividendos distribuídos acima do mínimo obrigatório são proibidos por lei.', false)
        ]},
        { title:'Lista 4 — Reservas de lucros', items:[
          mc('A reserva legal tem por finalidade principal:', ['Aumentar o lucro tributável','Assegurar a integridade do capital social','Reduzir o capital social','Pagar dividendos extraordinários'], 1),
          vf('A reserva de retenção de lucros exige orçamento de capital aprovado em assembleia.', true),
          mc('São exemplos de reservas de lucros, EXCETO:', ['Reserva legal','Reserva estatutária','Reserva de capital','Reserva de retenção de lucros'], 2),
          vf('A reserva de capital tem a mesma natureza da reserva de lucros.', false, 'A reserva de capital tem origem distinta (ex.: ágio na emissão de ações), não decorre do lucro do exercício.'),
          mc('A reserva de lucros a realizar destina-se a:', ['Reter parcela do lucro ainda não financeiramente realizada','Substituir a reserva legal','Pagar dividendos antecipados','Cobrir prejuízos futuros automaticamente'], 0),
          vf('As reservas de lucros podem, em regra, ser posteriormente utilizadas para distribuição de dividendos ou absorção de prejuízos.', true),
          mc('A reserva estatutária é constituída:', ['Por obrigação legal genérica, igual à reserva legal','Conforme previsão específica no estatuto social','Apenas por determinação judicial','Nunca é permitida por lei'], 1),
          vf('O total das reservas de lucros, sem justificativa, não pode ultrapassar o capital social, sob pena de capitalização ou distribuição do excesso.', true),
          mc('A finalidade da reserva de contingência é:', ['Compensar futura perda considerada provável','Substituir o dividendo obrigatório','Pagar participação de administradores','Reduzir o capital social'], 0),
          vf('As reservas de lucros aumentam o patrimônio líquido da companhia.', true)
        ]},
        { title:'Lista 5 — Revisão geral', items:[
          vf('A ordem de destinação do resultado busca proteger credores, sócios minoritários e a integridade do capital social.', true),
          mc('Assinale a alternativa que representa corretamente a sequência legal:', ['Dividendos, reserva legal, participações','Prejuízos acumulados, participações, reserva legal, dividendos','Reserva legal, prejuízos, dividendos, participações','Participações, dividendos, prejuízos, reserva legal'], 1),
          vf('As participações estatutárias reduzem o lucro líquido que serve de base para as demais destinações.', true),
          mc('O artigo da Lei 6.404/76 que trata do dividendo obrigatório é o:', ['Art. 190','Art. 193','Art. 202','Art. 176'], 2),
          vf('O artigo 193 da Lei 6.404/76 trata da reserva legal.', true),
          mc('Se uma companhia não tem prejuízos acumulados nem participações estatutárias previstas, a primeira destinação efetiva do lucro líquido é:', ['Reserva legal','Dividendos','Reserva de capital','Ativo diferido'], 0),
          vf('A companhia pode reter todo o lucro do exercício sem pagar dividendo obrigatório, sem qualquer justificativa legal.', false),
          mc('A finalidade última da sequência legal de destinações é:', ['Maximizar apenas o lucro dos administradores','Equilibrar a proteção ao capital, aos credores e o retorno aos acionistas','Eliminar a reserva legal','Evitar o pagamento de impostos'], 1),
          vf('A reserva legal e as reservas estatutárias compõem o patrimônio líquido da empresa.', true),
          mc('Em qual grupo contábil os dividendos já deliberados, mas ainda não pagos, são classificados?', ['Ativo circulante','Passivo circulante','Patrimônio líquido','Receita diferida'], 1)
        ]}
      ],
      quiz:[
        { q:'A reserva legal deixa de ser obrigatória quando atinge, junto com as reservas de capital, qual percentual do capital social?', opts:['10%','20%','30%','50%'], correct:2,
          explain:'Art. 193, §1º da Lei 6.404/76: dispensa-se a reserva legal quando o total (reserva legal + reservas de capital) atinge 30% do capital social.' },
        { q:'Se o estatuto for omisso quanto ao dividendo, aplica-se qual regra supletiva?', opts:['25% do lucro líquido','50% do lucro líquido ajustado','100% do lucro líquido','Não há dividendo obrigatório'], correct:1,
          explain:'Art. 202, a regra supletiva fixa o dividendo obrigatório em 50% do lucro líquido ajustado.' },
        { q:'A participação de empregados no resultado é contabilizada como:', opts:['Destinação do lucro após o IR','Despesa do próprio exercício','Reserva de capital','Ativo intangível'], correct:1,
          explain:'É reconhecida como despesa, reduzindo o lucro líquido do próprio período.' },
        { q:'Entre debenturistas, empregados, administradores e partes beneficiárias, qual a ordem legal de participação no art. 190?', opts:['Empregados, administradores, debenturistas, partes beneficiárias','Debenturistas, empregados, administradores, partes beneficiárias','Administradores, debenturistas, empregados, partes beneficiárias','Não há ordem definida em lei'], correct:1,
          explain:'O art. 190 estabelece exatamente essa sequência: debenturistas, empregados, administradores e partes beneficiárias.' },
        { q:'A reserva legal corresponde a que percentual do lucro líquido do exercício, por padrão?', opts:['1%','5%','10%','20%'], correct:1,
          explain:'5% do lucro líquido do exercício, até o limite de 20% do capital social.' }
      ],
      recovery:[
        { q:'A reserva legal corresponde a:', opts:['5% do lucro líquido','10% do lucro líquido','15% do lucro líquido','20% do lucro líquido'], correct:0,
          explain:'5% do lucro líquido do exercício, até 20% do capital social.' },
        { q:'Na omissão do estatuto, o dividendo obrigatório mínimo é de:', opts:['25%','50%','75%','100%'], correct:1,
          explain:'A regra supletiva do art. 202 fixa 50% do lucro líquido ajustado.' },
        { q:'A primeira destinação do lucro, quando aplicável, é:', opts:['Reserva legal','Absorção de prejuízos acumulados','Dividendos','Participação de administradores'], correct:1,
          explain:'Antes de qualquer outra destinação, absorvem-se prejuízos acumulados.' },
        { q:'A reserva legal deixa de ser obrigatória ao atingir, com as reservas de capital:', opts:['10% do capital social','20%','30%','50%'], correct:2,
          explain:'O limite combinado é de 30% do capital social.' },
        { q:'A participação de empregados é lançada como:', opts:['Reserva de lucros','Despesa do exercício','Ativo','Dividendo'], correct:1,
          explain:'É reconhecida como despesa do próprio período.' }
      ]
    },

    // =====================================================================
    // MODULE 4
    // =====================================================================
    {
      id:'m4', num:4, color:'#A83A3A',
      title:'Declaração de Ajuste Anual — IRPF',
      subtitle:'Apuração do Imposto de Renda da Pessoa Física',
      content:`
        <h4>Modelo completo x modelo simplificado</h4>
        <p>No modelo completo, o contribuinte deduz despesas legais efetivamente comprovadas (saúde, educação até o limite anual, previdência, dependentes, pensão alimentícia). No modelo simplificado, substitui-se todas as deduções por um desconto padrão de 20% dos rendimentos tributáveis, limitado a um teto anual. O sistema calcula ambos e aponta o mais vantajoso.</p>

        <h4>Rendimentos tributáveis, isentos e sujeitos à tributação exclusiva</h4>
        <p>Rendimentos como salários, pró-labore e aluguéis recebidos de pessoa física entram na base tributável mensal (ou via carnê-leão) e anual. Rendimentos isentos (como poupança) e os sujeitos à tributação exclusiva na fonte (como 13º salário) são informados separadamente e não compõem a base de cálculo do ajuste.</p>

        <h4>Deduções legais no modelo completo</h4>
        <ul>
          <li>Contribuição à Previdência Social oficial (sem limite);</li>
          <li>Previdência privada complementar (PGBL), limitada a 12% da renda bruta tributável;</li>
          <li>Dependentes, valor fixo por dependente informado na tabela anual;</li>
          <li>Despesas com instrução, até o limite anual por pessoa;</li>
          <li>Despesas médicas, sem limite, desde que comprovadas;</li>
          <li>Pensão alimentícia judicial.</li>
        </ul>

        <h4>Apuração do imposto devido</h4>
        <p>Soma-se os rendimentos tributáveis do ano, subtraem-se as deduções legais, chegando-se à base de cálculo anual. Aplica-se a tabela progressiva anualizada (12× a tabela mensal), com alíquotas de 7,5% a 27,5% conforme a faixa. O imposto devido é comparado ao total já retido na fonte e recolhido via carnê-leão: se o devido for maior, há saldo a pagar; se for menor, há restituição.</p>

        <h4>Exemplo simplificado</h4>
        <table class="ledger">
          <tr><th>Item</th><th class="num">Valor</th></tr>
          <tr><td>Rendimentos tributáveis no ano</td><td class="num">R$ 120.000,00</td></tr>
          <tr><td>(−) Contribuição à previdência oficial</td><td class="num">R$ 14.400,00</td></tr>
          <tr><td>(−) Dependente (1)</td><td class="num">R$ 2.275,08</td></tr>
          <tr><td>(−) Despesas com educação (limite anual)</td><td class="num">R$ 3.561,50</td></tr>
          <tr><td><b>Base de cálculo anual</b></td><td class="num"><b>R$ 99.763,42</b></td></tr>
          <tr><td>Imposto apurado pela tabela progressiva anual</td><td class="num">≈ R$ 14.200,00</td></tr>
          <tr><td>(−) IR retido na fonte durante o ano</td><td class="num">R$ 8.000,00</td></tr>
          <tr><td><b>Saldo de imposto a pagar</b></td><td class="num"><b>R$ 6.200,00</b></td></tr>
        </table>
        <p>Os valores da tabela são ilustrativos e devem ser atualizados conforme a legislação vigente no ano-calendário da declaração.</p>
      `,
      exerciseLists: [
        { title:'Lista 1 — Conceitos gerais', items:[
          vf('O contribuinte pode optar entre o modelo completo e o simplificado na declaração anual.', true),
          mc('No modelo simplificado, o desconto padrão é de:', ['10%','15%','20%','25%'], 2),
          vf('O desconto simplificado substitui todas as deduções legais do modelo completo.', true),
          mc('São exemplos de deduções do modelo completo, EXCETO:', ['Dependentes','Despesas médicas','Desconto simplificado de 20%','Previdência oficial'], 2),
          vf('Rendimentos sujeitos à tributação exclusiva na fonte entram na base de cálculo do ajuste anual.', false),
          mc('O 13º salário é tributado, em regra, de forma:', ['Exclusiva na fonte','Incluída na base de ajuste anual','Isenta','Progressiva mensal normal, junto do salário'], 0),
          vf('As despesas médicas são dedutíveis, no modelo completo, sem limite de valor.', true),
          mc('As despesas com instrução (educação), no modelo completo, têm:', ['Dedução sem limite','Limite anual por pessoa','Vedação total de dedução','Limite apenas para ensino superior'], 1),
          vf('A contribuição à previdência privada PGBL é dedutível sem qualquer limite.', false, 'É limitada a 12% da renda bruta tributável.'),
          mc('O programa da Receita Federal usado para apurar o IRPF anual é chamado de:', ['GCAP','Programa da Declaração de Ajuste Anual (IRPF)','e-Social','SPED'], 1)
        ]},
        { title:'Lista 2 — Deduções legais (cálculo)', items:[
          mc('Rendimento tributável anual R$ 100.000,00, previdência oficial R$ 12.000,00: base parcial após essa dedução:', ['R$ 85.000,00','R$ 88.000,00','R$ 90.000,00','R$ 100.000,00'], 1),
          vf('Cada dependente informado gera uma dedução fixa de valor anual definido em tabela.', true),
          mc('Rendimento tributável R$ 90.000,00, um dependente (dedução aproximada de R$ 2.275,08): base parcial aproximada:', ['R$ 85.000,00','R$ 87.724,92','R$ 88.000,00','R$ 90.000,00'], 1),
          vf('As despesas com educação têm limite anual de dedução por pessoa, no modelo completo.', true),
          mc('No modelo simplificado, rendimento tributável de R$ 60.000,00: desconto padrão (20%):', ['R$ 6.000,00','R$ 10.000,00','R$ 12.000,00','R$ 15.000,00'], 2),
          mc('Base de cálculo no modelo simplificado do exemplo acima:', ['R$ 45.000,00','R$ 48.000,00','R$ 50.000,00','R$ 54.000,00'], 1),
          vf('A pensão alimentícia judicial é dedutível no modelo completo.', true),
          mc('Rendimento tributável R$ 150.000,00, previdência oficial R$ 18.000,00, dois dependentes (≈R$4.550,16): base de cálculo aproximada:', ['R$ 125.000,00','R$ 127.449,84','R$ 132.000,00','R$ 140.000,00'], 1),
          vf('O contribuinte deve, por obrigação legal, escolher sempre o modelo completo, mesmo que o simplificado resulte em imposto menor.', false),
          mc('Se o desconto simplificado (20%) ultrapassar o teto anual definido em lei, o sistema aplica:', ['O valor do teto legal','O percentual completo mesmo assim, sem limite','Zero de dedução','O dobro do teto'], 0)
        ]},
        { title:'Lista 3 — Apuração do imposto e tabela progressiva', items:[
          vf('A tabela progressiva do IRPF possui faixas de isenção e alíquotas crescentes.', true),
          mc('A alíquota máxima da tabela progressiva do IRPF é:', ['15%','22,5%','27,5%','35%'], 2),
          vf('Quanto maior a base de cálculo, maior tende a ser a alíquota efetiva aplicada.', true),
          mc('O imposto apurado na declaração é comparado com:', ['Apenas o IPTU pago no ano','O IR retido na fonte e o recolhido via carnê-leão','O ICMS pago no ano','O FGTS depositado'], 1),
          vf('Se o imposto devido é maior que o retido na fonte, o contribuinte tem direito a restituição.', false, 'Nesse caso há saldo de imposto a pagar, não restituição.'),
          mc('Se o imposto devido é menor que o retido, o resultado é:', ['Saldo a pagar','Restituição','Multa automática','Isenção total retroativa'], 1),
          vf('A restituição do IRPF é paga pela Receita Federal em lotes ao longo do ano.', true),
          mc('A base de cálculo anual é obtida por meio de:', ['Rendimentos tributáveis menos deduções legais','Apenas rendimentos isentos','Apenas rendimentos exclusivos','Patrimônio total do contribuinte'], 0),
          vf('Os rendimentos isentos, como os da caderneta de poupança, compõem a base de cálculo tributável do ajuste.', false),
          mc('A faixa de isenção da tabela progressiva é aplicada a rendimentos:', ['Até um determinado valor mínimo mensal/anual','Acima de R$50.000,00','Somente para aposentados','Somente para autônomos'], 0)
        ]},
        { title:'Lista 4 — Prazos e obrigatoriedade', items:[
          mc('A Declaração de Ajuste Anual do IRPF deve ser entregue, em regra, em qual período do ano seguinte?', ['Janeiro a fevereiro','Março a maio','Junho a agosto','Setembro a novembro'], 1),
          vf('Todo contribuinte, com qualquer valor de renda, é obrigado a declarar o IRPF.', false, 'A obrigatoriedade depende de critérios legais, como limites de renda e patrimônio.'),
          mc('São critérios que podem gerar obrigatoriedade de declarar, EXCETO:', ['Rendimentos tributáveis acima do limite anual','Posse de bens acima de determinado valor','Ter recebido ganho de capital tributável','Ter menos de 18 anos'], 3),
          vf('A entrega da declaração fora do prazo pode gerar multa.', true),
          mc('A multa mínima por atraso na entrega da declaração é:', ['Um valor fixo mínimo estabelecido em lei','Sempre isenta se o imposto devido for zero','Igual à alíquota máxima da tabela','Inexistente'], 0),
          vf('O contribuinte pode retificar a declaração já entregue, caso identifique erros.', true),
          mc('A malha fina ocorre quando:', ['A declaração é entregue no prazo, sem qualquer erro','Há inconsistências entre informações declaradas e as recebidas de terceiros','O contribuinte não é obrigado a declarar','O imposto devido é zero'], 1),
          vf('Informar rendimentos de forma incompatível com o patrimônio declarado pode levar a declaração à malha fina.', true),
          mc('Após a entrega da declaração, o comprovante de recebimento é gerado:', ['Automaticamente pelo sistema da Receita Federal','Manualmente, pelos Correios','Apenas em cartório','Não é gerado nenhum comprovante'], 0),
          vf('A declaração pode ser feita pelo modelo completo ou pelo simplificado, e o programa indica o mais vantajoso.', true)
        ]},
        { title:'Lista 5 — Revisão geral', items:[
          vf('O objetivo da Declaração de Ajuste Anual é confrontar o que foi retido/pago ao longo do ano com o imposto realmente devido.', true),
          mc('O carnê-leão é utilizado quando:', ['Há retenção automática na fonte','O contribuinte recebe rendimentos de pessoa física ou do exterior, sem retenção na fonte','É usado apenas por empresas','Nunca é necessário'], 1),
          vf('O carnê-leão é uma forma de recolhimento mensal obrigatório de IR para certos rendimentos.', true),
          mc('Rendimentos de aluguel recebidos de pessoa física, em regra:', ['São isentos de IR','Exigem recolhimento mensal via carnê-leão','Só entram na declaração anual, sem recolhimento mensal','São tributados exclusivamente na fonte'], 1),
          vf('O modelo completo tende a ser mais vantajoso para quem tem muitas despesas dedutíveis comprovadas.', true),
          mc('O modelo simplificado tende a ser mais vantajoso para quem:', ['Tem poucas deduções comprováveis','Tem despesas médicas altas','Tem muitos dependentes','Paga pensão alimentícia alta'], 0),
          vf('A Receita Federal permite ao contribuinte comparar automaticamente os dois modelos antes da entrega da declaração.', true),
          mc('O resultado final da declaração pode ser:', ['Somente restituição','Somente imposto a pagar','Restituição, imposto a pagar ou declaração sem saldo','Sempre isenção total'], 2),
          vf('Rendimentos tributáveis recebidos no exterior por residente no Brasil, em regra, também compõem a base de cálculo do IRPF.', true),
          mc('A principal diferença entre o modelo completo e o simplificado está:', ['Na forma de calcular a dedução da base de cálculo','No valor da alíquota máxima aplicável','No prazo de entrega da declaração','No órgão responsável pela declaração'], 0)
        ]}
      ],
      quiz:[
        { q:'No modelo simplificado, as deduções legais são substituídas por:', opts:['Um desconto fixo de R$ 5.000,00','Um desconto de 20% dos rendimentos tributáveis, limitado a um teto anual','Isenção total do imposto','Dedução integral da previdência privada'], correct:1,
          explain:'O desconto simplificado é de 20% dos rendimentos tributáveis, respeitado um teto anual definido em lei.' },
        { q:'A contribuição à previdência social oficial é dedutível no modelo completo:', opts:['Com limite de 12%','Sem limite','Não é dedutível','Apenas para autônomos'], correct:1,
          explain:'A previdência oficial é dedutível integralmente, sem limite percentual (diferente da previdência privada PGBL).' },
        { q:'Quando o IR retido na fonte durante o ano é maior que o IR devido apurado na declaração, o resultado é:', opts:['Imposto a pagar','Restituição','Multa','Isenção retroativa'], correct:1,
          explain:'Se o retido supera o devido, o contribuinte recebe a diferença de volta como restituição.' },
        { q:'A previdência privada do tipo PGBL é dedutível, no modelo completo, até qual limite?', opts:['5% da renda bruta','12% da renda bruta tributável','20% da renda bruta','Sem limite'], correct:1,
          explain:'O PGBL é dedutível até 12% da renda bruta tributável anual, desde que o contribuinte também contribua para a previdência oficial ou regime próprio.' },
        { q:'Rendimentos sujeitos à tributação exclusiva na fonte, como o 13º salário:', opts:['Entram na base de cálculo mensal normal','São somados aos rendimentos tributáveis do ajuste anual','São informados separadamente e não compõem a base de cálculo do ajuste','Ficam isentos de qualquer tributação'], correct:2,
          explain:'Por já terem sido tributados de forma exclusiva e definitiva na fonte, não se somam à base de cálculo do ajuste anual.' }
      ],
      recovery:[
        { q:'O desconto padrão do modelo simplificado é de:', opts:['10%','15%','20%','25%'], correct:2,
          explain:'O desconto simplificado é de 20% dos rendimentos tributáveis, limitado a um teto.' },
        { q:'O 13º salário é tributado, em regra, de forma:', opts:['Exclusiva na fonte','Normal na base de cálculo anual','Isenta','Progressiva mensal, junto do salário'], correct:0,
          explain:'O 13º salário sofre tributação exclusiva na fonte, não compondo a base do ajuste.' },
        { q:'Se o imposto devido é menor que o retido, o resultado é:', opts:['Saldo a pagar','Restituição','Multa','Nenhum efeito'], correct:1,
          explain:'O excesso retido é devolvido ao contribuinte como restituição.' },
        { q:'A previdência privada PGBL é dedutível até:', opts:['5% da renda bruta','12% da renda bruta','20% da renda bruta','Sem limite'], correct:1,
          explain:'O limite legal de dedução do PGBL é de 12% da renda bruta tributável.' },
        { q:'O carnê-leão é usado para:', opts:['Rendimentos com retenção automática na fonte','Rendimentos sem retenção na fonte (ex.: aluguel de pessoa física)','Apenas para empresas','Nunca é utilizado'], correct:1,
          explain:'Serve para o recolhimento mensal de IR sobre rendimentos recebidos sem retenção.' }
      ]
    },

    // =====================================================================
    // MODULE 5
    // =====================================================================
    {
      id:'m5', num:5, color:'#5C4A8A',
      title:'Ganho de Capital da Pessoa Física',
      subtitle:'Apuração, alíquotas e isenções',
      content:`
        <h4>Conceito</h4>
        <p>Ganho de capital é a diferença positiva entre o valor de alienação de um bem ou direito e o seu custo de aquisição. Aplica-se a imóveis, veículos, participações societárias, criptoativos e outros bens do patrimônio da pessoa física.</p>

        <h4>Alíquotas progressivas</h4>
        <p>Desde a Lei 13.259/2016, o ganho de capital de pessoa física é tributado de forma progressiva:</p>
        <table class="ledger">
          <tr><th>Faixa do ganho de capital</th><th class="num">Alíquota</th></tr>
          <tr><td>Até R$ 5.000.000,00</td><td class="num">15%</td></tr>
          <tr><td>De R$ 5.000.000,01 até R$ 10.000.000,00</td><td class="num">17,5%</td></tr>
          <tr><td>De R$ 10.000.000,01 até R$ 30.000.000,00</td><td class="num">20%</td></tr>
          <tr><td>Acima de R$ 30.000.000,00</td><td class="num">22,5%</td></tr>
        </table>

        <h4>Principais isenções</h4>
        <ul>
          <li>Venda do único imóvel do contribuinte por valor até R$ 440.000,00, desde que não tenha vendido outro imóvel nos últimos 5 anos;</li>
          <li>Venda de imóvel residencial cujo produto seja integralmente aplicado na compra de outro imóvel residencial no país, em até 180 dias;</li>
          <li>Alienação de bens de pequeno valor: até R$ 35.000,00 para bens em geral e R$ 20.000,00 para ações negociadas fora de bolsa.</li>
        </ul>

        <h4>Apuração e recolhimento</h4>
        <p>O ganho de capital é apurado através do programa GCAP da Receita Federal e o imposto é recolhido via DARF (código 4600), até o último dia útil do mês seguinte ao do recebimento (ou de cada parcela, em vendas parceladas). O resultado da apuração é depois importado para a Declaração de Ajuste Anual.</p>

        <h4>Exemplo</h4>
        <table class="ledger">
          <tr><th>Item</th><th class="num">Valor</th></tr>
          <tr><td>Valor de venda do imóvel (2024)</td><td class="num">R$ 700.000,00</td></tr>
          <tr><td>(−) Custo de aquisição (2010)</td><td class="num">R$ 300.000,00</td></tr>
          <tr><td><b>Ganho de capital</b></td><td class="num"><b>R$ 400.000,00</b></td></tr>
          <tr><td>Alíquota aplicável (faixa até R$5 milhões)</td><td class="num">15%</td></tr>
          <tr><td><b>Imposto devido (DARF 4600)</b></td><td class="num"><b>R$ 60.000,00</b></td></tr>
        </table>
        <p>Nesse exemplo não há isenção, pois o valor de venda excede o limite de R$440.000,00 e não há informação de reinvestimento em outro imóvel em 180 dias.</p>
      `,
      exerciseLists: [
        { title:'Lista 1 — Conceitos gerais', items:[
          vf('O ganho de capital é a diferença positiva entre o valor de venda e o custo de aquisição do bem.', true),
          mc('O ganho de capital pode incidir sobre, EXCETO:', ['Imóveis','Veículos','Salário mensal','Participações societárias'], 2),
          vf('A alíquota do ganho de capital de pessoa física é fixa em 15%, sem progressividade.', false),
          mc('A primeira faixa da tabela progressiva do ganho de capital tem alíquota de:', ['10%','15%','20%','25%'], 1),
          vf('O ganho de capital é apurado por meio do programa GCAP da Receita Federal.', true),
          mc('O imposto sobre o ganho de capital é recolhido via:', ['GPS','DARF','GRU','DAS'], 1),
          vf('O código de receita utilizado no DARF do ganho de capital é o 4600.', true),
          mc('O prazo de recolhimento do imposto sobre o ganho de capital é:', ['Até o último dia útil do mês da venda','Até o último dia útil do mês seguinte à venda','Até 90 dias após a venda','Somente na declaração anual'], 1),
          vf('O resultado da apuração do ganho de capital é posteriormente informado na Declaração de Ajuste Anual.', true),
          mc('O custo de aquisição de um imóvel corresponde, em regra, a:', ['Apenas o valor venal usado no IPTU','O valor efetivamente pago na aquisição, mais custos legais incorporáveis','O valor de mercado atual do imóvel','Sempre zero'], 1)
        ]},
        { title:'Lista 2 — Alíquotas progressivas (cálculo)', items:[
          mc('Ganho de capital de R$ 2.000.000,00: alíquota aplicável:', ['15%','17,5%','20%','22,5%'], 0),
          mc('Imposto devido sobre o ganho de capital de R$ 2.000.000,00 (alíquota de 15%, dentro da 1ª faixa):', ['R$ 250.000,00','R$ 300.000,00','R$ 350.000,00','R$ 400.000,00'], 1),
          vf('Ganhos de capital acima de R$ 30.000.000,00 são tributados a 22,5%.', true),
          mc('Ganho de capital de R$ 8.000.000,00: alíquota aplicável à faixa correspondente:', ['15%','17,5%','20%','22,5%'], 1),
          vf('A tributação do ganho de capital é sempre uma alíquota única sobre o valor total, nunca por faixas.', false, 'É progressiva por faixas, de forma semelhante à tabela do IRPF.'),
          mc('Ganho de capital de R$ 6.000.000,00: imposto devido, aplicando 15% até R$5 milhões e 17,5% sobre o excedente:', ['R$ 900.000,00','R$ 925.000,00','R$ 950.000,00','R$ 1.000.000,00'], 1, '5.000.000×15% = 750.000; 1.000.000×17,5% = 175.000; total = 925.000.'),
          vf('A faixa de R$ 10.000.000,01 até R$ 30.000.000,00 é tributada a 20%.', true),
          mc('Ganho de capital de R$ 12.000.000,00: maior alíquota marginal aplicada (sobre a última faixa alcançada):', ['15%','17,5%','20%','22,5%'], 2),
          vf('As alíquotas progressivas do ganho de capital de pessoa física foram instituídas pela Lei 13.259/2016.', true),
          mc('Ganho de capital de R$ 4.000.000,00: imposto devido:', ['R$ 500.000,00','R$ 600.000,00','R$ 650.000,00','R$ 700.000,00'], 1)
        ]},
        { title:'Lista 3 — Isenções', items:[
          mc('A isenção da venda do único imóvel se aplica a vendas de até:', ['R$ 220.000,00','R$ 350.000,00','R$ 440.000,00','R$ 600.000,00'], 2),
          vf('A isenção do único imóvel exige que o contribuinte não tenha vendido outro imóvel nos últimos 5 anos.', true),
          mc('A isenção por reinvestimento exige que o valor da venda seja aplicado em outro imóvel residencial no país em até:', ['30 dias','90 dias','180 dias','360 dias'], 2),
          vf('A isenção por reinvestimento também se aplica caso o novo imóvel adquirido seja comercial.', false, 'O novo imóvel precisa ser residencial.'),
          mc('O limite de isenção para bens de pequeno valor em geral é:', ['R$ 20.000,00','R$ 35.000,00','R$ 50.000,00','R$ 100.000,00'], 1),
          vf('O limite de isenção para ações negociadas fora de bolsa é de R$ 20.000,00.', true),
          mc('Se um contribuinte vende seu único imóvel por R$ 500.000,00, ele:', ['Está isento integralmente','Não está isento, pois o valor excede R$440.000,00','Tem isenção parcial automática','Paga apenas 5% de imposto'], 1),
          vf('As isenções do ganho de capital de imóveis buscam, entre outros objetivos, não penalizar a compra da moradia própria.', true),
          mc('Um contribuinte vende imóvel por R$ 900.000,00 e reinveste apenas R$ 600.000,00 em outro imóvel residencial em 90 dias. O restante (R$300.000,00):', ['Fica integralmente isento','Sofre tributação proporcional sobre a parcela não reinvestida','É automaticamente devolvido ao Fisco','Não precisa ser declarado'], 1),
          vf('As isenções do ganho de capital dependem de comprovação e declaração correta ao Fisco.', true)
        ]},
        { title:'Lista 4 — Apuração prática', items:[
          mc('Imóvel comprado por R$ 250.000,00 e vendido por R$ 600.000,00: ganho de capital:', ['R$ 250.000,00','R$ 300.000,00','R$ 350.000,00','R$ 400.000,00'], 2),
          mc('Imposto devido sobre o ganho acima (alíquota de 15%):', ['R$ 50.000,00','R$ 52.500,00','R$ 55.000,00','R$ 60.000,00'], 1),
          vf('Despesas com corretagem na venda do imóvel podem, em regra, ser deduzidas na apuração do ganho de capital.', true),
          mc('Imóvel comprado por R$ 400.000,00 e vendido por R$ 400.000,00: ganho de capital:', ['R$ 0,00','R$ 4.000,00','R$ 40.000,00','R$ 400.000,00'], 0),
          vf('Não havendo ganho de capital, não há imposto a pagar.', true),
          mc('Bem adquirido por R$ 100.000,00 e vendido por R$ 130.000,00: ganho de capital:', ['R$ 15.000,00','R$ 30.000,00','R$ 100.000,00','R$ 130.000,00'], 1),
          vf('Bens de pequeno valor, dentro do limite legal, ficam isentos mesmo havendo ganho de capital.', true),
          mc('Ações vendidas fora de bolsa por R$ 18.000,00 (limite de isenção de R$20.000,00): situação tributária:', ['Isenta, pois está dentro do limite','Tributada normalmente pela tabela progressiva','Tributada a 22,5%','Depende apenas do custo de aquisição'], 0),
          vf('A apuração do ganho de capital deve considerar eventuais fatores de redução aplicáveis a imóveis adquiridos antes de 1988.', true),
          mc('O principal documento utilizado para apurar e depois importar o ganho de capital para a declaração anual é o:', ['GCAP','DARF','DIRF','GFIP'], 0)
        ]},
        { title:'Lista 5 — Revisão geral', items:[
          vf('O ganho de capital de pessoa física segue tabela progressiva desde a Lei 13.259/2016.', true),
          mc('A isenção do único imóvel tem como objetivo principal:', ['Beneficiar grandes investidores','Não penalizar a venda de imóveis de menor valor destinados à moradia','Isentar sempre qualquer venda de imóvel','Beneficiar apenas empresas'], 1),
          vf('O prazo de recolhimento do DARF de ganho de capital é, em regra, até o último dia útil do mês seguinte ao da venda (ou de cada parcela recebida).', true),
          mc('Em uma venda parcelada, o imposto sobre o ganho de capital deve ser recolhido:', ['De uma só vez, ao final do contrato','Proporcionalmente, a cada parcela recebida','Apenas na declaração anual','Nunca é devido em vendas parceladas'], 1),
          vf('O ganho de capital de pessoa física e o de pessoa jurídica seguem exatamente as mesmas regras e alíquotas.', false),
          mc('Um dos objetivos das isenções e limites de pequeno valor é:', ['Desonerar operações de menor relevância econômica','Beneficiar apenas grandes patrimônios','Eliminar toda tributação sobre imóveis','Aumentar a arrecadação sobre pequenos contribuintes'], 0),
          vf('O valor do imposto apurado no GCAP deve ser informado posteriormente na Declaração de Ajuste Anual do IRPF.', true),
          mc('A tributação progressiva do ganho de capital busca, principalmente:', ['Tributar mais fortemente grandes ganhos','Isentar todos os ganhos, independentemente do valor','Tributar igualmente todos os valores','Beneficiar apenas pessoas jurídicas'], 0),
          vf('As regras de isenção do ganho de capital de imóveis exigem atenção ao histórico de vendas dos últimos 5 anos do contribuinte.', true),
          mc('A correta apuração do ganho de capital é importante, principalmente, para:', ['Evitar autuação fiscal e recolher corretamente o imposto devido','Aumentar artificialmente o lucro contábil','Reduzir o capital social','Eliminar a necessidade de declarar o IRPF'], 0)
        ]}
      ],
      quiz:[
        { q:'O ganho de capital de pessoa física é calculado como:', opts:['Valor de venda menos despesas de manutenção','Valor de venda menos o custo de aquisição','Valor de venda menos o IPTU pago','Valor de venda menos a inflação do período'], correct:1,
          explain:'É a diferença positiva entre o valor de alienação e o custo de aquisição do bem.' },
        { q:'Qual a alíquota aplicável à faixa de ganho de capital até R$ 5.000.000,00?', opts:['10%','15%','20%','27,5%'], correct:1,
          explain:'A primeira faixa da tabela progressiva do ganho de capital é tributada a 15%.' },
        { q:'A isenção da venda do único imóvel se aplica até qual valor de venda?', opts:['R$ 220.000,00','R$ 350.000,00','R$ 440.000,00','R$ 1.000.000,00'], correct:2,
          explain:'O limite de isenção para venda do único imóvel do contribuinte é R$440.000,00.' },
        { q:'Para gozar da isenção por reinvestimento, o produto da venda de imóvel residencial deve ser aplicado em outro imóvel residencial no país em até:', opts:['30 dias','90 dias','180 dias','360 dias'], correct:2,
          explain:'O prazo legal para o reinvestimento integral é de 180 dias contados da venda.' },
        { q:'O imposto sobre o ganho de capital é recolhido através de qual documento e código?', opts:['GPS, código 2100','DARF, código 4600','GRU, código 0250','DAS, código 4600'], correct:1,
          explain:'O recolhimento é feito via DARF com o código de receita 4600.' }
      ],
      recovery:[
        { q:'A alíquota da primeira faixa do ganho de capital é:', opts:['10%','15%','20%','25%'], correct:1,
          explain:'Ganhos de até R$5 milhões são tributados a 15%.' },
        { q:'A isenção do único imóvel vale para vendas até:', opts:['R$ 220.000,00','R$ 350.000,00','R$ 440.000,00','R$ 600.000,00'], correct:2,
          explain:'O limite legal de isenção é R$440.000,00.' },
        { q:'O prazo de reinvestimento para a isenção é de:', opts:['90 dias','120 dias','180 dias','365 dias'], correct:2,
          explain:'O reinvestimento integral deve ocorrer em até 180 dias.' },
        { q:'O imposto sobre ganho de capital é recolhido via:', opts:['GPS','DARF','GRU','DAS'], correct:1,
          explain:'O recolhimento é feito por meio de DARF.' },
        { q:'O código de receita do DARF de ganho de capital é:', opts:['1708','4600','0220','5952'], correct:1,
          explain:'O código de receita utilizado é o 4600.' }
      ]
    }
  ];

  // ---- State & persistence ----
  let state = {
    view: 'loading', // loading | login | dashboard | module | professor
    user: null, // {name, role}
    activeModuleId: null,
    activeTab: 'conteudo',
    activeExerciseList: 0,
    authError: '',
    signupRole: 'aluno',
    masterCode: '',
    loginMatricula: '', // confirmação obrigatória do aluno em todo login
    progress: null, // current student's progress object
    roster: null, // for professor view (students who logged in)

    // ---- Turmas (professor) ----
    professorTab: 'acompanhamento', // 'acompanhamento' | 'turmas'
    turmas: [], // list of turmas created by this professor
    activeTurmaId: null,
    creatingTurma: false,
    newTurmaName: '',
    newStudentNome: '',
    newStudentMatricula: '',
    pdfStatus: '', // '' | 'loading' | 'ready' | 'error'
    pdfStatusMsg: '',
    pdfRawText: '',
    pdfPreview: null, // array of {nome, matricula} pending confirmation

    // ---- Suporte (aluno/professor/admin) ----
    suporteTab: null, // aluno: 'professor'|'admin' | professor: 'alunos'|'admin' | admin: 'alunos'|'professores'
    suporteThread: null, // {participantName, messages:[...]} for "own thread" contexts
    suporteInbox: null, // array of threads for inbox contexts (professor->alunos, admin->*)
    suporteActiveThreadKey: null, // selected participant name in inbox mode
    suporteNewMessage: '',

    // ---- Auditoria / Correções pendentes (professor) ----
    auditLog: [],
    correcoesPendentes: { incompletos: [], mensagensPendentes: [], modulosPendentes: [] },
    usuarios: [],
    reportTurmaFilter: '',
    accessPendingMessage: '',
    studentTurma: null,
    accessAuditOnly: false,

    // ---- Planejamento docente ----
    planningSubtab: 'semester', // semester | lesson
    planningRecords: { semester: [], lesson: [] },
    planningEditing: null,
    planningMessage: ''
  };

  function emptyProgress(name){
    const modules = {};
    MODULES.forEach(m => {
      modules[m.id] = {
        contentRead:false,
        exerciseListsDone: new Array(m.exerciseLists.length).fill(false),
        exerciseScores: new Array(m.exerciseLists.length).fill(null),
        quizScore:null, quizTotal: m.quiz.length,
        recoveryScore:null, recoveryTotal: m.recovery.length,
        correction:{ status:'liberado', submittedAt:null, reviewedAt:null, feedback:'', finalGrade:null, released:false, history:[] }
      };
    });
    return { name, updatedAt: Date.now(), modules };
  }

  async function loadProgress(name){
    try {
      const r = await kvGet('student:' + name);
      if (r && r.value) {
        const parsed = JSON.parse(r.value);
        // Backfill in case module structure grew since the student last saved
        MODULES.forEach(m => {
          if (!parsed.modules[m.id]) {
            parsed.modules[m.id] = {
              contentRead:false, exerciseListsDone: new Array(m.exerciseLists.length).fill(false),
              exerciseScores:new Array(m.exerciseLists.length).fill(null),
              quizScore:null, quizTotal:m.quiz.length, recoveryScore:null, recoveryTotal:m.recovery.length,
              correction:{ status:'liberado', submittedAt:null, reviewedAt:null, feedback:'', finalGrade:null, released:false, history:[] }
            };
          } else {
            const mp = parsed.modules[m.id];
            if (!Array.isArray(mp.exerciseListsDone)) mp.exerciseListsDone = new Array(m.exerciseLists.length).fill(false);
            while (mp.exerciseListsDone.length < m.exerciseLists.length) mp.exerciseListsDone.push(false);
            if (!Array.isArray(mp.exerciseScores)) mp.exerciseScores = new Array(m.exerciseLists.length).fill(null);
            while (mp.exerciseScores.length < m.exerciseLists.length) mp.exerciseScores.push(null);
            if (mp.quizTotal === undefined) mp.quizTotal = m.quiz.length;
            if (mp.recoveryScore === undefined) mp.recoveryScore = null;
            if (mp.recoveryTotal === undefined) mp.recoveryTotal = m.recovery.length;
            if (!mp.correction) mp.correction = { status:'liberado', submittedAt:null, reviewedAt:null, feedback:'', finalGrade:null, released:false, history:[] };
            if (!Array.isArray(mp.correction.history)) mp.correction.history = [];
            if (mp.correction.released === undefined) mp.correction.released = mp.correction.status === 'corrigido';
          }
        });
        return parsed;
      }
    } catch(e){}
    return emptyProgress(name);
  }
  async function saveProgress(p){
    p.updatedAt = Date.now();
    try { await kvSet('student:' + p.name, JSON.stringify(p)); } catch(e){ console.error('storage error', e); }
  }
  async function loadRoster(){
    try {
      const list = await kvList('student:');
      if (!list || !list.keys) return [];
      const out = [];
      for (const k of list.keys){
        try {
          const r = await kvGet(k);
          if (r && r.value) out.push(JSON.parse(r.value));
        } catch(e){}
      }
      return out;
    } catch(e){ return []; }
  }

  // ---- Turmas persistence ----
  function newTurmaId(){
    return 'turma_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2,7);
  }
  async function saveTurma(t){
    t.updatedAt = Date.now();
    try { await kvSet('turma:' + t.id, JSON.stringify(t)); } catch(e){ console.error('storage error', e); }
  }
  async function loadTurmasForProfessor(professorName){
    try {
      const list = await kvList('turma:');
      if (!list || !list.keys) return [];
      const out = [];
      for (const k of list.keys){
        try {
          const r = await kvGet(k);
          if (r && r.value){
            const t = JSON.parse(r.value);
            if (t.professor === professorName) out.push(t);
          }
        } catch(e){}
      }
      out.sort((a,b)=> (b.createdAt||0) - (a.createdAt||0));
      return out;
    } catch(e){ return []; }
  }

  async function loadStudentTurma(studentName){
    try {
      const list = await kvList('turma:');
      if (!list || !list.keys) return null;
      const target=(studentName||'').trim().toLocaleLowerCase('pt-BR');
      const matches=[];
      for (const k of list.keys){
        try {
          const r=await kvGet(k); if(!r||!r.value) continue;
          const t=JSON.parse(r.value);
          if ((t.students||[]).some(s=>(s.nome||'').trim().toLocaleLowerCase('pt-BR')===target)) matches.push(t);
        } catch(e){}
      }
      matches.sort((a,b)=>(b.updatedAt||b.createdAt||0)-(a.updatedAt||a.createdAt||0));
      return matches[0]||null;
    } catch(e){ return null; }
  }

  function normalizeMatricula(value){
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

  // ---- PDF import (pdf.js loaded on demand from cdnjs) ----
  let pdfJsLoadPromise = null;
  function loadPdfJs(){
    if (window.pdfjsLib) return Promise.resolve(window.pdfjsLib);
    if (pdfJsLoadPromise) return pdfJsLoadPromise;
    pdfJsLoadPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
      script.onload = () => {
        try {
          window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
          resolve(window.pdfjsLib);
        } catch(e){ reject(e); }
      };
      script.onerror = () => reject(new Error('Não foi possível carregar o leitor de PDF.'));
      document.head.appendChild(script);
    });
    return pdfJsLoadPromise;
  }
  async function extractLinesFromPdf(file){
    const pdfjsLib = await loadPdfJs();
    const buf = await file.arrayBuffer();
    const doc = await pdfjsLib.getDocument({ data: buf }).promise;
    const lines = [];
    for (let p = 1; p <= doc.numPages; p++){
      const page = await doc.getPage(p);
      const content = await page.getTextContent();
      const rows = {};
      content.items.forEach(item => {
        const y = Math.round(item.transform[5]);
        if (!rows[y]) rows[y] = [];
        rows[y].push(item);
      });
      const ys = Object.keys(rows).map(Number).sort((a,b) => b - a);
      ys.forEach(y => {
        const line = rows[y].sort((a,b) => a.transform[4] - b.transform[4]).map(i => i.str).join(' ').replace(/\s+/g,' ').trim();
        if (line) lines.push(line);
      });
    }
    return lines;
  }
  // Parses "Nome ... 12345678" or "12345678 ... Nome" style lines into {nome, matricula}.
  function parseStudentLine(line){
    line = (line || '').trim();
    if (!line) return null;
    const digitMatches = line.match(/\d{4,20}/g);
    let matricula = '';
    if (digitMatches && digitMatches.length){
      matricula = digitMatches.reduce((a,b) => b.length >= a.length ? b : a, digitMatches[0]);
    }
    let nome = matricula ? line.replace(matricula, ' ') : line;
    nome = nome.replace(/[-–—._,;:|#º°]+/g, ' ').replace(/\s+/g,' ').trim();
    if (!nome && !matricula) return null;
    return { nome: nome || '(nome não identificado)', matricula: matricula || '' };
  }

  // ---- Suporte persistence ----
  // Threads are keyed by "support:<kind>:<participantKey>", kind in:
  //   'aluno-professor'  (participantKey = aluno name)
  //   'aluno-admin'      (participantKey = aluno name)
  //   'professor-admin'  (participantKey = professor name)
  const SUPPORT_STATUSES = [
    ['aberto','Aberto'],['em_analise','Em análise'],['aguardando_resposta','Aguardando resposta'],
    ['encaminhado_desenvolvimento','Encaminhado para desenvolvimento'],['aprovado_desenvolvimento','Aprovado para desenvolvimento'],
    ['resolvido','Resolvido'],['encerrado','Encerrado']
  ];
  function supportStatusLabel(status){ const x=SUPPORT_STATUSES.find(i=>i[0]===status); return x?x[1]:'Aberto'; }
  function normalizeThread(t, participantKey){
    t=t||{}; t.participantName=t.participantName||participantKey; t.protocol=t.protocol||''; t.status=t.status||'aberto';
    t.createdAt=t.createdAt||null; t.updatedAt=t.updatedAt||null; t.responseDueAt=t.responseDueAt||null;
    t.closedAt=t.closedAt||null; t.reopenUntil=t.reopenUntil||null; t.messages=Array.isArray(t.messages)?t.messages:[];
    t.history=Array.isArray(t.history)?t.history:[]; return t;
  }
  function canReopenThread(t){ return !!(t && t.status==='encerrado' && (!t.reopenUntil || Date.now()<=Number(t.reopenUntil))); }
  async function loadThread(kind, participantKey){
    try {
      const r = await kvGet('support:' + kind + ':' + participantKey);
      if (r && r.value) return normalizeThread(JSON.parse(r.value), participantKey);
    } catch(e){}
    return normalizeThread(null, participantKey);
  }
  async function saveThread(kind, thread){
    try { await kvSet('support:' + kind + ':' + thread.participantName, JSON.stringify(thread)); }
    catch(e){ console.error('storage error', e); }
  }
  async function listThreads(kind){
    try {
      const list = await kvList('support:' + kind + ':');
      if (!list || !list.keys) return [];
      const out = [];
      for (const k of list.keys){
        try {
          const r = await kvGet(k);
          if (r && r.value) out.push(JSON.parse(r.value));
        } catch(e){}
      }
      out.sort((a,b) => {
        const la = a.messages.length ? a.messages[a.messages.length-1].ts : 0;
        const lb = b.messages.length ? b.messages[b.messages.length-1].ts : 0;
        return lb - la;
      });
      return out;
    } catch(e){ return []; }
  }

  function suporteInboxKind(){
    const role = state.user.role;
    if (role === 'professor') return 'aluno-professor';
    if (role === 'admin') return state.suporteTab === 'alunos' ? 'aluno-admin' : 'professor-admin';
    return null;
  }

  async function loadSuporteForCurrentTab(){
    const role = state.user.role;
    state.suporteActiveThreadKey = null;
    state.suporteThread = null;
    state.suporteInbox = null;
    if (role === 'aluno'){
      const kind = state.suporteTab === 'professor' ? 'aluno-professor' : 'aluno-admin';
      state.suporteThread = await loadThread(kind, state.user.name);
    } else if (role === 'professor'){
      if (state.suporteTab === 'alunos'){
        state.suporteInbox = await listThreads('aluno-professor');
      } else {
        state.suporteThread = await loadThread('professor-admin', state.user.name);
      }
    } else { // admin
      state.suporteInbox = await listThreads(suporteInboxKind());
    }
  }

  async function openSuporte(){
    const role = state.user.role;
    if (!state.suporteTab){
      state.suporteTab = role === 'professor' ? 'alunos' : (role === 'admin' ? 'alunos' : 'professor');
    }
    state.view = 'suporte';
    await loadSuporteForCurrentTab();
    render();
  }

  async function selectSuporteThread(participantKey){
    state.suporteActiveThreadKey = participantKey;
    state.suporteThread = await loadThread(suporteInboxKind(), participantKey);
    render();
  }

  async function sendSuporteMessage(){
    const text = (state.suporteNewMessage || '').trim();
    if (!text) return;
    const role = state.user.role;
    let kind, participantKey;
    if (role === 'aluno'){
      kind = state.suporteTab === 'professor' ? 'aluno-professor' : 'aluno-admin';
      participantKey = state.user.name;
    } else if (role === 'professor'){
      if (state.suporteTab === 'alunos'){
        if (!state.suporteActiveThreadKey) return;
        kind = 'aluno-professor'; participantKey = state.suporteActiveThreadKey;
      } else {
        kind = 'professor-admin'; participantKey = state.user.name;
      }
    } else { // admin
      if (!state.suporteActiveThreadKey) return;
      kind = suporteInboxKind(); participantKey = state.suporteActiveThreadKey;
    }
    const thread = state.suporteThread || { participantName: participantKey, protocol:'', status:'aberto', createdAt:null, updatedAt:null, messages: [] };
    thread.participantName = participantKey;
    if (!thread.protocol){ const d=new Date(); thread.protocol='SUP-'+d.toISOString().slice(0,10).replace(/-/g,'')+'-'+Math.random().toString(36).slice(2,7).toUpperCase(); thread.createdAt=Date.now(); thread.history=thread.history||[]; thread.history.push({type:'abertura',ts:Date.now(),by:state.user.name}); }
    if (thread.status === 'encerrado') return;
    thread.updatedAt=Date.now();
    thread.messages.push({ from: role, name: state.user.name, text, ts: Date.now() });
    await saveThread(kind, thread);
    state.suporteThread = thread;
    state.suporteNewMessage = '';
    await logAudit('mensagem_suporte', `${state.user.name} (${roleLabelFor(role)}) enviou uma mensagem de suporte — canal ${kind}.`);
    render();
  }

  // ---- Auditoria (professor) ----
  function roleLabelFor(role){
    return role === 'professor' ? 'professor' : (role === 'admin' ? 'usuário mestre' : 'aluno');
  }
  async function logAudit(type, detail){
    const entry = {
      type, detail,
      actor: (state.user && state.user.name) || 'Sistema',
      role: (state.user && state.user.role) || '',
      email: (state.user && state.user.email) || '',
      ts: Date.now()
    };
    try {
      const key = 'audit:' + Date.now() + '_' + Math.random().toString(36).slice(2,8);
      await kvSet(key, JSON.stringify(entry));
    } catch(e){ console.error('audit log error', e); }
  }
  async function loadAuditoria(){
    try {
      const list = await kvList('audit:');
      if (!list || !list.keys) { state.auditLog = []; return; }
      const out = [];
      for (const k of list.keys){
        try { const r = await kvGet(k); if (r && r.value) out.push(JSON.parse(r.value)); } catch(e){}
      }
      out.sort((a,b) => (b.ts||0) - (a.ts||0));
      state.auditLog = out.slice(0, 150);
    } catch(e){ state.auditLog = []; }
  }

  // ---- Planejamento docente (professor) ----
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

  // ---- Correções pendentes (professor) ----
  async function loadCorrecoesPendentes(){
    const incompletos = [];
    (state.turmas || []).forEach(t => {
      t.students.forEach((s, i) => {
        const nomeVazio = !s.nome || !s.nome.trim() || s.nome === '(nome não identificado)';
        const matriculaVazia = !s.matricula || !s.matricula.trim();
        if (nomeVazio || matriculaVazia){
          incompletos.push({ turmaId: t.id, turmaName: t.name, index: i, nome: s.nome, matricula: s.matricula });
        }
      });
    });
    let mensagensPendentes = [];
    try {
      const threads = await listThreads('aluno-professor');
      mensagensPendentes = threads.filter(t => t.status !== 'encerrado' && t.messages.length && t.messages[t.messages.length-1].from === 'aluno');
    } catch(e){}
    const modulosPendentes = [];
    const allRoster = await loadRoster();
    const roster = professorRoster(allRoster);
    roster.forEach(st => MODULES.forEach(m => {
      const mp = st.modules && st.modules[m.id]; const c = correctionState(mp);
      if (moduleReadyForSubmission(mp,m) && !c.released) modulosPendentes.push({ student:st, module:m, mp, correction:c });
    }));
    state.roster = roster;
    state.correcoesPendentes = { incompletos, mensagensPendentes, modulosPendentes };
  }

  function correctionState(mp){
    if (!mp) return { status:'liberado', submittedAt:null, reviewedAt:null, feedback:'', finalGrade:null, released:false, history:[], firstSubmittedAt:null, late:false, latePenalty:0 };
    if(!mp.correction) mp.correction={ status:'liberado', submittedAt:null, reviewedAt:null, feedback:'', finalGrade:null, released:false, history:[], firstSubmittedAt:null, late:false, latePenalty:0 };
    const c=mp.correction; if(!Array.isArray(c.history))c.history=[]; if(c.firstSubmittedAt===undefined)c.firstSubmittedAt=null; if(c.late===undefined)c.late=false; if(c.latePenalty===undefined)c.latePenalty=0;
    // Compatibilidade: versões anteriores liberavam o módulo automaticamente.
    // Preservamos liberações humanas legadas (aprovação) e as novas liberações pedagógicas;
    // somente liberações automáticas voltam a aguardar decisão explícita do professor.
    const hasHumanRelease=c.history.some(h=>h&&['aprovacao','liberacao_pedagogica'].includes(h.type));
    const hasAutoRelease=c.history.some(h=>h&&h.type==='conclusao_automatica');
    if(c.released && hasAutoRelease && !hasHumanRelease){ c.released=false; c.status='aguardando_liberacao'; c.reviewedAt=null; }
    return c;
  }
  function statusLabel(status){
    return ({ liberado:'Em desenvolvimento', em_correcao:'Enviado para correção', ajustes:'Ajustes solicitados', aguardando_liberacao:'Aguardando liberação', corrigido:'Concluído / Liberado' })[status] || 'Em desenvolvimento';
  }
  function score10(score,total){
    if (score === null || score === undefined || !total) return null;
    return Math.round((Number(score)/Number(total))*100)/10;
  }
  function effectiveAssessmentScores10(mp){
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
  function effectiveExerciseScores10(mp){
    return effectiveAssessmentScores10(mp).exercises;
  }
  function exerciseAverage10(mp){
    const vals = effectiveAssessmentScores10(mp).exercises.filter(v => v !== null && v !== undefined).map(Number);
    if (!vals.length) return null;
    return Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*10)/10;
  }
  function baseAutomaticModuleGrade(mp){
    if (!mp) return null;
    const adjusted = effectiveAssessmentScores10(mp).values.filter(v => v !== null && v !== undefined).map(Number);
    if (!adjusted.length) return null;
    return Math.round((adjusted.reduce((a,b)=>a+b,0)/adjusted.length)*10)/10;
  }
  function effectiveModuleGrade(mp){
    const base=baseAutomaticModuleGrade(mp); if(base===null) return null;
    const c=correctionState(mp); const penalty=Number(c.latePenalty||0);
    return Math.max(0,Math.round((base-penalty)*10)/10);
  }
  function scheduleForModule(m){
    const t=state.studentTurma; return (t&&t.moduleSettings&&t.moduleSettings[m.id])||{};
  }
  function toTs(v){ if(!v) return null; const ts=new Date(v).getTime(); return Number.isFinite(ts)?ts:null; }
  function moduleAccess(m){
    const idx=MODULES.findIndex(x=>x.id===m.id);
    if(idx>0){ const prevModule=MODULES[idx-1], prev=state.progress&&state.progress.modules[prevModule.id], pc=correctionState(prev); if(!moduleReadyForSubmission(prev,prevModule)) return {locked:true,reason:'Conclua as 5 listas, o Quiz e a Recuperação do módulo anterior.'}; if(!pc.released) return {locked:true,reason:'Aguarde a liberação do professor para avançar ao próximo módulo.'}; }
    const s=scheduleForModule(m), deadline=toTs(s.deadline), original=toTs(s.originalDeadline)||deadline, now=Date.now();
    if(deadline && now>deadline && !s.allowLate) return {locked:true,reason:'Prazo encerrado. Aguarde a reabertura pelo professor.',deadline,late:true};
    return {locked:false,deadline,late:!!(original&&now>original),allowLate:!!s.allowLate};
  }
  function moduleDeadlineText(m){ const a=moduleAccess(m); if(!a.deadline) return 'Prazo não definido'; return 'Prazo: '+new Date(a.deadline).toLocaleString('pt-BR')+(a.late?' · entrega em atraso':''); }

  function exerciseListDone(mp, index){


    return !!(mp && Array.isArray(mp.exerciseScores) && mp.exerciseScores[index] !== null && mp.exerciseScores[index] !== undefined);


  }


  function nextExerciseListIndex(mp, m){


    for (let i=0; i<m.exerciseLists.length; i++) if (!exerciseListDone(mp,i)) return i;


    return m.exerciseLists.length;


  }


  function exerciseListLocked(mp, m, index){


    if (exerciseListDone(mp,index)) return false;


    return index !== nextExerciseListIndex(mp,m);


  }


  function moduleReadyForSubmission(mp, m){
    return !!(mp && Array.isArray(mp.exerciseScores) && mp.exerciseScores.length >= m.exerciseLists.length && mp.exerciseScores.slice(0,m.exerciseLists.length).every(v => v !== null && v !== undefined) && mp.quizScore !== null && mp.quizScore !== undefined && mp.recoveryScore !== null && mp.recoveryScore !== undefined);
  }
  function moduleCompleted(mp){
    return !!(mp && Array.isArray(mp.exerciseScores) && mp.exerciseScores.slice(0,5).length === 5 && mp.exerciseScores.slice(0,5).every(v => v !== null && v !== undefined) && mp.quizScore !== null && mp.quizScore !== undefined && mp.recoveryScore !== null && mp.recoveryScore !== undefined);
  }
  function fmtGrade(v){ return (v === null || v === undefined || Number.isNaN(Number(v))) ? '—' : Number(v).toFixed(1).replace('.',','); }
  function moduleStatusLabel(mp, m){
    if (m){
      const access=moduleAccess(m);
      if (access.locked) return 'Bloqueado — aguardando liberação';
    }
    if (!moduleCompleted(mp)) return 'Em andamento';
    return correctionState(mp).released ? 'Concluído / Liberado' : 'Aguardando liberação';
  }
  function correctionBadge(mp){
    const done = moduleCompleted(mp), released = done && correctionState(mp).released;
    const cls = released ? 'ok' : (done ? 'info' : 'neutral');
    const label = released ? 'Concluído / Liberado' : (done ? 'Aguardando liberação' : 'Em andamento');
    return `<span class="status-badge ${cls}">${label}</span>`;
  }

  function pctModule(mp, m){
    if (!mp) return 0;
    const listsTotal = m ? m.exerciseLists.length : (mp.exerciseListsDone ? mp.exerciseListsDone.length : 5);
    const totalWeight = 1 /*content*/ + listsTotal + 1 /*quiz*/ + 1 /*recuperação*/;
    let score = 0;
    if (mp.contentRead) score += 1;
    if (Array.isArray(mp.exerciseListsDone)) score += mp.exerciseListsDone.filter(Boolean).length;
    if (mp.quizScore !== null && mp.quizScore !== undefined) score += 1;
    if (mp.recoveryScore !== null && mp.recoveryScore !== undefined) score += 1;
    return Math.round((score/totalWeight)*100);
  }
  function overallPct(progress){
    if (!progress) return 0;
    const vals = MODULES.map(m => pctModule(progress.modules[m.id], m));
    return Math.round(vals.reduce((a,b)=>a+b,0)/vals.length);
  }
  function professorRoster(roster){
    const source = roster || state.roster || [];
    if (!state.user || state.user.role !== 'professor') return source;
    const names = new Set();
    (state.turmas || []).forEach(t => (t.students || []).forEach(a => {
      const n = (a.nome || '').trim().toLocaleLowerCase('pt-BR');
      if (n) names.add(n);
    }));
    return source.filter(st => names.has((st.name || '').trim().toLocaleLowerCase('pt-BR')));
  }

  function esc(s){ return (s||'').toString().replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

  // ---- Render ----
  function render(){
    if (state.view === 'loading') { root.innerHTML = `<div class="empty-state">Carregando…</div>`; return; }
    if (state.view === 'login') { renderLogin(); return; }
    if (state.view === 'access-pending') { renderAccessPending(); return; }

    const roleLabel = state.user.role === 'professor' ? 'Professor' : (state.user.role === 'admin' ? 'Usuário Mestre' : 'Aluno');
    let inner = `<div class="masthead"><div class="masthead-row">
      <div>
        <h1 class="serif">Contabilidade Avançada</h1>
        <div class="kicker">Sala de aula — provisões, resultado, destinações, IRPF e ganho de capital</div>
      </div>
      <div class="userbadge">${roleLabel}: <b>${esc(state.user.name)}</b>
        <button id="btn-logout">sair</button>
      </div>
    </div>
    ${renderNav()}
    </div>
    <div class="wrap">`;

    if (state.view === 'dashboard') inner += renderDashboard();
    else if (state.view === 'module') inner += renderModule();
    else if (state.view === 'professor') inner += renderProfessor();
    else if (state.view === 'manual') inner += renderManual();
    else if (state.view === 'suporte') inner += renderSuporte();
    else if (state.view === 'notas') inner += renderMinhasNotas();
    else if (state.view === 'usuarios') inner += renderUsuarios();

    inner += `</div>`;
    root.innerHTML = inner;
    attachHandlers();
  }

  function renderNav(){
    const role = state.user.role;
    let items;
    if (role === 'aluno') items = [['dashboard','Início'],['notas','Minhas Notas'],['manual','Manual do Aluno'],['suporte','Suporte']];
    else if (role === 'professor') items = [['professor:turmas','Turmas'],['professor:planejamento','Planejamento'],['professor:acompanhamento','Notas da Turma'],['professor:correcoes','Pendências'],['professor:relatorios','Relatórios'],['professor:backup','Backup'],['professor:auditoria','Auditoria'],['professor:operacional','Manual Operacional'],['professor:checklist','Checklist'],['professor:guia','Guia Pedagógico'],['manual','Manual do Professor'],['suporte','Suporte']];
    else items = [['suporte','Suporte'],['usuarios','Usuários']];

    return `<div class="topnav">` + items.map(([key,label]) => {
      let active = false;
      if (key.startsWith('professor:')){
        active = state.view === 'professor' && state.professorTab === key.split(':')[1];
      } else {
        active = state.view === key;
      }
      return `<div class="nav-item ${active?'active':''}" data-nav="${key}">${esc(label)}</div>`;
    }).join('') + `</div>`;
  }

  function renderAccessPending(){
    root.innerHTML = `<div class="auth-shell"><div class="auth-left">
      <div class="auth-brand"><div class="auth-logo">✓</div><div><div class="auth-kicker">CEDUP HERMANN HERING</div><div class="auth-sub">Contabilidade Avançada</div></div></div>
      <h1>Acesso de Professor<br/>aguardando aprovação</h1>
      <p class="auth-desc">Sua conta Google foi autenticada, mas o acesso como Professor(a) precisa ser liberado por um Usuário Mestre antes da entrada na plataforma.</p>
    </div><div class="auth-right"><div class="auth-card">
      <div class="auth-lockrow">⏳ Solicitação de acesso enviada</div>
      <p class="auth-hint"><b>Conta:</b> ${esc(state.user && state.user.email ? state.user.email : '')}</p>
      <p class="auth-hint">Status: <b>Aguardando aprovação</b></p>
      <button class="auth-gbtn" id="btn-check-access" style="margin-bottom:10px">Verificar liberação</button><button class="auth-gbtn" id="btn-pending-logout">Sair</button>
    </div></div></div>`;
    const chk=document.getElementById('btn-check-access'); if(chk) chk.addEventListener('click',async()=>{chk.disabled=true; const snap=await getDoc(doc(db,'users',state.user.uid)); const profile=snap.exists()?snap.data():null; if(profile&&profile.role==='professor'){state.user.role='professor'; state.roster=await loadRoster(); state.turmas=await loadTurmasForProfessor(profile.name); state.professorTab='acompanhamento'; state.view='professor'; render();} else {chk.disabled=false; alert('A solicitação ainda está aguardando aprovação.');}});
    const b=document.getElementById('btn-pending-logout');
    if (b) b.addEventListener('click', async()=>{ await signOut(auth); });
  }

  function friendlyAuthError(e){
    const code = e && e.code ? e.code : '';
    const map = {
      'auth/popup-closed-by-user': 'A janela de login foi fechada antes de concluir. Tente novamente.',
      'auth/cancelled-popup-request': 'Só é possível uma janela de login por vez. Tente novamente.',
      'auth/popup-blocked': 'O navegador bloqueou a janela de login. Permita pop-ups para este site e tente novamente.',
      'auth/network-request-failed': 'Falha de conexão. Verifique sua internet e tente novamente.',
      'auth/too-many-requests': 'Muitas tentativas. Aguarde um pouco e tente novamente.'
    };
    return map[code] || 'Não foi possível concluir o login. Tente novamente.';
  }

  function renderLogin(){
    root.innerHTML = `
      <div class="auth-shell">
        <div class="auth-left">
          <div class="auth-brand">
            <div class="auth-logo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3 2 8l10 5 10-5-10-5Z"/><path d="M6 10.5V16c0 1.5 2.7 3 6 3s6-1.5 6-3v-5.5"/></svg></div>
            <div>
              <div class="auth-kicker">CEDUP HERMANN HERING</div>
              <div class="auth-sub">Curso Técnico em Administração e Contabilidade</div>
            </div>
          </div>
          <h1>Contabilidade<br/>Avançada</h1>
          <p class="auth-desc">Provisões da folha, apuração do resultado, participações, IRPF e ganho de capital — módulo a módulo, com prática guiada e correção na hora.</p>
          <div class="auth-bars">
            <div style="height:20%"></div><div style="height:28%"></div><div style="height:34%"></div>
            <div style="height:42%"></div><div style="height:50%"></div><div style="height:58%"></div>
            <div style="height:66%"></div><div style="height:76%"></div><div style="height:86%"></div><div style="height:100%"></div>
          </div>
          <div class="auth-feat"><div class="auth-feat-ic"></div>5 módulos guiados, do provisionamento à declaração do IRPF</div>
          <div class="auth-feat"><div class="auth-feat-ic"></div>Correção automática do quiz e recuperação paralela</div>
          <div class="auth-feat"><div class="auth-feat-ic"></div>Acompanhamento do professor atualizado em tempo real</div>
        </div>

        <div class="auth-right">
          <div class="auth-card">
            <div class="auth-lockrow">🔒 Entrar no sistema</div>
            <p class="auth-hint">Entre com sua conta Google para acessar a plataforma.</p>
            ${state.authError ? `<div class="auth-error">${esc(state.authError)}</div>` : ''}

            <label class="auth-label">Perfil de acesso</label>
            <div class="auth-role-choice">
              <button type="button" id="role-aluno" class="auth-role ${state.signupRole==='aluno'?'on':''}">Aluno(a)</button>
              <button type="button" id="role-professor" class="auth-role ${state.signupRole==='professor'?'on':''}">Professor(a)</button>
            </div>
            <p class="auth-hint2">Só é usado na primeira vez que esta conta entra no sistema. Depois disso, o perfil só pode ser alterado por um Usuário Mestre, no painel de Usuários.</p>

            ${state.signupRole==='aluno' ? `<label class="auth-label" for="student-matricula">Matrícula do aluno</label>
            <input type="text" id="student-matricula" inputmode="numeric" autocomplete="off" placeholder="Informe sua matrícula" value="${esc(state.loginMatricula)}" />
            <p class="auth-hint2">Obrigatória em todo acesso do Aluno. A matrícula precisa constar em uma turma criada pelo Professor, por importação PDF ou cadastro individual.</p>` : ''}

            <label class="auth-label" for="master-code">Código de Mestre (opcional)</label>
            <div class="auth-code-input">
              <input type="password" id="master-code" placeholder="Deixe em branco se não tiver" value="${esc(state.masterCode)}" />
              <button type="button" id="toggle-master-code" title="Mostrar/ocultar">👁</button>
            </div>
            <p class="auth-hint2">Só preencha se você recebeu um código de Usuário Mestre. Deixe em branco para entrar com o perfil escolhido acima.</p>

            <button class="auth-gbtn" id="btn-google-signin">
              <svg width="18" height="18" viewBox="0 0 18 18"><path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.874 2.684-6.615z"/><path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z"/><path fill="#FBBC05" d="M3.964 10.706A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.706V4.962H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.038l3.007-2.332z"/><path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.962L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"/></svg>
              Continuar com o Google
            </button>
            <p class="auth-foot">Autenticado via Firebase Authentication — somente conta Google.</p>
          </div>
        </div>
      </div>
    `;
    document.getElementById('role-aluno').addEventListener('click', () => { state.signupRole='aluno'; render(); });
    document.getElementById('role-professor').addEventListener('click', () => { state.signupRole='professor'; render(); });
    const sm = document.getElementById('student-matricula');
    if (sm) sm.addEventListener('input', e => { state.loginMatricula = e.target.value; });
    const mc = document.getElementById('master-code');
    mc.addEventListener('input', e => { state.masterCode = e.target.value; });
    document.getElementById('toggle-master-code').addEventListener('click', () => {
      mc.type = mc.type === 'password' ? 'text' : 'password';
    });
    document.getElementById('btn-google-signin').addEventListener('click', onGoogleSignIn);
  }

  async function onGoogleSignIn(){
    state.authError = '';
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      // onAuthStateChanged cuida da criação do perfil (se for a primeira vez)
      // e do redirecionamento a partir daqui.
    } catch(e){
      state.authError = friendlyAuthError(e);
      render();
    }
  }

  function renderDashboard(){
    let html = `<div class="note">Seu progresso é salvo automaticamente e fica visível para o professor da turma acompanhar. Cada módulo tem conteúdo, 5 listas de exercícios (10 questões cada), um quiz avaliativo e uma recuperação paralela.</div>`;
    html += `<div class="section-title">Módulos da disciplina</div>`;
    MODULES.forEach(m => {
      const mp = state.progress.modules[m.id];
      const pct = pctModule(mp, m); const access=moduleAccess(m);
      html += `<div class="module-row ${access.locked?'locked':''}" style="--mcolor:${m.color}" data-module="${m.id}" data-locked="${access.locked?'1':'0'}">
        <div class="module-num serif">${String(m.num).padStart(2,'0')}</div>
        <div class="module-info">
          <h3>${esc(m.title)} ${access.locked?'<span class="status-badge neutral">🔒 Bloqueado — aguardando liberação</span>':''}</h3>
          <p>${esc(m.subtitle)}</p><div class="deadline-text">${esc(access.locked?access.reason:moduleDeadlineText(m))}</div>
        </div>
        <div class="module-progress">
          ${pct}% concluído<br>${correctionBadge(mp)}
          <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
        </div>
      </div>`;
    });
    return html;
  }

  // ---- Minhas Notas (aluno) ----
  function renderMinhasNotas(){
    let html = `<div class="section-title">Minhas notas</div>`;
    html += `<div class="note">Os <b>5 exercícios e o Quiz valem 10,0 pontos cada</b> e têm o mesmo peso. A <b>Recuperação não é uma 7ª nota</b>: sua nota é comparada individualmente com cada exercício e com o Quiz e substitui toda nota inferior. Quando houver substituição, aparece <b>nota original → nota considerada</b>. A <b>Nota do Módulo</b> é calculada automaticamente após as 5 listas, o Quiz e a Recuperação obrigatória; o avanço ao próximo módulo depende da liberação do professor.</div>`;
    html += `<div class="table-scroll"><table class="roster"><tr><th>Módulo</th><th class="num">Ex. 1</th><th class="num">Ex. 2</th><th class="num">Ex. 3</th><th class="num">Ex. 4</th><th class="num">Ex. 5</th><th class="num">Quiz</th><th class="num">Recuperação</th><th class="num">Nota do Módulo</th><th>Situação</th></tr>`;
    MODULES.forEach(m => {
      const mp = state.progress.modules[m.id]; const c=correctionState(mp);
      const quizTxt = score10(mp.quizScore,mp.quizTotal); const recTxt=score10(mp.recoveryScore,mp.recoveryTotal);
      const adjusted = effectiveAssessmentScores10(mp);
      const exerciseCells = Array.from({length:5}, (_,i) => {
        const original = Array.isArray(mp.exerciseScores) ? mp.exerciseScores[i] : null;
        const effective = adjusted.exercises[i]; const replaced = !!(adjusted.replaced && adjusted.replaced[i]);
        if (effective === null || effective === undefined) return `<td class="num">—</td>`;
        const shown = replaced ? `${fmtGrade(Number(original))} → <b>${fmtGrade(effective)}</b>` : fmtGrade(effective);
        return `<td class="num">${shown}</td>`;
      }).join('');
      const quizReplaced = !!(adjusted.replaced && adjusted.replaced[5]);
      const quizCell = adjusted.quiz === null || adjusted.quiz === undefined ? '—' : (quizReplaced ? `${fmtGrade(quizTxt)} → <b>${fmtGrade(adjusted.quiz)}</b>` : fmtGrade(adjusted.quiz));
      const grade = moduleReadyForSubmission(mp,m) ? effectiveModuleGrade(mp) : null;
      const access=moduleAccess(m);
      const situation=access.locked ? `<span class="status-badge neutral">Bloqueado</span><div class="cell-status">Aguardando liberação do professor</div>` : moduleStatusLabel(mp,m);
      html += `<tr><td>${esc(m.num+'. '+m.title)}${access.locked?' <span class="status-badge neutral">🔒 Bloqueado</span>':''}</td>${exerciseCells}<td class="num">${quizCell}</td><td class="num">${fmtGrade(recTxt)}</td><td class="num"><b>${fmtGrade(grade)}</b></td><td>${situation}</td></tr>`;
      if (c.feedback) html += `<tr><td colspan="10"><div class="feedback-box"><b>Registro anterior do professor:</b> ${esc(c.feedback)}</div></td></tr>`;
    });
    html += `</table></div>`;
    return html;
  }

  // ---- Manual ----
  const MANUAL_ALUNO_HTML = `
    <h4>Como acessar</h4>
    <p>Entre com sua conta Google e informe sua <b>matrícula em todo acesso</b>. A entrada somente é liberada quando a matrícula estiver cadastrada em uma turma criada pelo Professor, por importação PDF ou inclusão individual. O nome acadêmico da turma passa a identificar seu progresso na plataforma.</p>
    <h4>Módulos</h4>
    <p>No menu "Início" você encontra os 5 módulos da disciplina. O avanço é sequencial: o próximo módulo é liberado somente após a correção e liberação do anterior. Os prazos definidos pelo professor aparecem nos cartões. Cada módulo tem quatro abas:</p>
    <ul>
      <li><b>Conteúdo</b> — teoria, exemplos numéricos e lançamentos contábeis;</li>
      <li><b>Exercícios</b> — 5 listas de 10 questões cada, realizadas obrigatoriamente em sequência. Após corrigir uma lista, a nota fica registrada, ela passa a constar como "Feita" e não pode ser refeita; somente então a lista seguinte é liberada;</li>
      <li><b>Quiz</b> — avaliação única que vale nota, corrigida na hora;</li>
      <li><b>Recuperação</b> — avaliação paralela que não entra como 7ª nota. Sua nota é comparada com cada um dos 5 exercícios e com o Quiz; sempre que for superior, substitui aquela nota inferior para compor a média das 6 atividades.</li>
    </ul>
    <h4>Minhas Notas</h4>
    <p>No menu superior, "Minhas Notas" mostra as notas dos 5 exercícios, Quiz, Recuperação, Nota do Módulo e situação. Os 5 exercícios e o Quiz possuem o mesmo peso. A Recuperação substitui individualmente todas as notas dessas 6 atividades que forem inferiores à nota obtida na Recuperação. Quando houver substituição, a tela apresenta a nota original → nota considerada, inclusive no Quiz.</p><h4>Conclusão do módulo</h4><p>Depois de realizar obrigatoriamente as 5 listas, o Quiz e a Recuperação, o sistema calcula automaticamente a Nota do Módulo. O próximo módulo permanece bloqueado até a liberação individual do professor. A leitura do conteúdo compõe o progresso de estudo, mas não impede o fechamento da nota.</p>
    <h4>Suporte</h4>
    <p>No menu "Suporte" você pode abrir chamados ao professor ou à administração. Cada chamado recebe protocolo, histórico, status administrativo, prazo de resposta e período de reabertura. Chamados e listas podem ser impressos ou salvos em PDF.</p>
  `;
  const MANUAL_PROFESSOR_HTML = `
    <h4>Turmas</h4>
    <p>No menu "Turmas" você cria turmas informando apenas um nome. <b>Somente alunos com matrícula cadastrada em uma dessas turmas conseguem entrar na plataforma.</b> A matrícula é confirmada obrigatoriamente em todo login do Aluno. Dentro de cada turma é possível montar a lista de alunos de duas formas:</p>
    <ul>
      <li>Enviando um arquivo PDF com nome e matrícula — o texto é extraído automaticamente e fica disponível para revisão e correção antes de confirmar;</li>
      <li>Adicionando um aluno por vez, informando nome e matrícula.</li>
    </ul>
    <h4>Planejamento</h4><p>O menu "Planejamento" reúne o Planejamento Semestral e o Plano de Aula conforme os modelos institucionais. É possível salvar, editar e imprimir/salvar em PDF. No Plano de Aula, informe obrigatoriamente data de início e fim; cada período pode ter no máximo 30 dias e não pode se sobrepor a outro plano da mesma turma.</p>
    <h4>Notas da Turma</h4>
    <p>O menu "Notas da Turma" mostra a Nota do Módulo e permite abrir o detalhamento de cada aluno, com Ex. 1 a Ex. 5, Quiz, Recuperação e identificação de toda substituição no formato nota original → nota considerada. As notas são calculadas automaticamente.</p><h4>Pendências</h4><p>A área "Pendências" reúne alunos que concluíram o ciclo avaliativo e aguardam liberação individual do próximo módulo, além de cadastros incompletos e mensagens aguardando resposta. As notas permanecem automáticas; o professor controla apenas a progressão pedagógica.</p><h4>Relatórios e Backup</h4><p>"Relatórios" apresenta o Relatório de Desempenho com resumo da turma, progresso e detalhamento por atividade, com CSV e impressão/PDF. "Backup" gera arquivo JSON das turmas e dados pedagógicos vinculados.</p>
    <h4>Suporte</h4>
    <p>No menu "Suporte" há duas áreas: <b>Alunos</b>, com chamados identificados por protocolo e status, onde você pode responder, encerrar ou reabrir cada atendimento; e <b>Administração</b>, seu canal direto com a administração da plataforma.</p>
  `;
  function renderManual(){
    const role = state.user.role;
    const title = role === 'aluno' ? 'Manual do Aluno' : 'Manual do Professor';
    const content = role === 'aluno' ? MANUAL_ALUNO_HTML : MANUAL_PROFESSOR_HTML;
    return `<div class="section-title">${title}</div><div class="panel">${content}</div>`;
  }

  // ---- Suporte (aluno/professor/admin) ----
  function renderThreadConversation(thread, myRole){
    thread=normalizeThread(thread,thread&&thread.participantName); const messages=thread.messages||[]; const closed=thread.status==='encerrado';
    let html=`<div class="support-meta"><div><b>${esc(thread.protocol||'Protocolo gerado no primeiro envio')}</b><span class="status-badge ${closed?'neutral':thread.status==='resolvido'?'ok':'info'}">${esc(supportStatusLabel(thread.status))}</span></div><button class="btn-outline small" id="btn-print-support">Imprimir / Salvar PDF</button></div>`;
    html+=`<div class="support-dates">Prazo de resposta: <b>${thread.responseDueAt?new Date(Number(thread.responseDueAt)).toLocaleString('pt-BR'):'não definido'}</b>${thread.reopenUntil?` · Reabertura até: <b>${new Date(Number(thread.reopenUntil)).toLocaleString('pt-BR')}</b>`:''}</div>`;
    if(state.user&&state.user.role!=='aluno'&&thread.protocol){ html+=`<div class="support-controls"><div><label>Status</label><select id="support-status">${SUPPORT_STATUSES.map(([v,l])=>`<option value="${v}" ${thread.status===v?'selected':''}>${esc(l)}</option>`).join('')}</select></div><div><label>Prazo de resposta</label><input type="datetime-local" id="support-due" value="${thread.responseDueAt?new Date(Number(thread.responseDueAt)-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16):''}"></div><div><label>Reabertura permitida até</label><input type="datetime-local" id="support-reopen" value="${thread.reopenUntil?new Date(Number(thread.reopenUntil)-new Date().getTimezoneOffset()*60000).toISOString().slice(0,16):''}"></div><button class="btn-brass" id="btn-save-support-control">Salvar atendimento</button></div>`; }
    if(closed&&canReopenThread(thread)) html+=`<button class="btn-outline" id="btn-reopen-support">Reabrir chamado</button>`;
    html+=`<div class="chat-box">`;
    if(!messages.length) html+=`<div class="empty-state" style="padding:24px">Nenhuma mensagem ainda. Envie a primeira mensagem abaixo.</div>`;
    else messages.forEach(m=>{const mine=m.from===myRole; html+=`<div class="chat-msg ${mine?'mine':''}"><div class="chat-meta">${esc(m.name)} · ${new Date(m.ts).toLocaleString('pt-BR')}</div><div class="chat-bubble">${esc(m.text)}</div></div>`;});
    html+=`</div><div class="chat-input-row"><textarea id="suporte-msg" placeholder="${closed?'Chamado encerrado. Reabra para enviar nova mensagem.':'Escreva sua mensagem...'}" ${closed?'disabled':''}>${esc(state.suporteNewMessage)}</textarea><button class="btn-brass" id="btn-send-suporte" ${closed?'disabled':''}>Enviar</button></div>`;
    return html;
  }

  function renderInboxList(list){
    if (!list || !list.length) return `<div class="empty-state">Nenhuma conversa ainda.</div>`;
    let html = '';
    list.forEach(t => {
      const last = t.messages.length ? t.messages[t.messages.length-1] : null;
      html += `<div class="thread-row" data-thread="${esc(t.participantName)}">
        <div>
          <b>${esc(t.participantName)}</b> <span class="status-badge ${t.status==='encerrado'?'neutral':t.status==='resolvido'?'ok':'info'}">${esc(supportStatusLabel(t.status))}</span>
          <div class="thread-preview">${t.protocol?esc(t.protocol)+' · ':''}${last ? esc(last.text.slice(0,70)) : 'Sem mensagens ainda'}</div>
        </div>
        <span class="back-link">Abrir →</span>
      </div>`;
    });
    return html;
  }

  // ---- Usuários (painel do Usuário Mestre) ----
  async function loadUsuarios(){
    try {
      const snap = await getDocs(collection(db, 'users'));
      const out = [];
      snap.forEach(d => out.push({ id: d.id, ...d.data() }));
      out.sort((a,b) => (a.name||'').localeCompare(b.name||''));
      state.usuarios = out;
    } catch(e){ state.usuarios = []; }
  }

  function renderUsuarios(){
    let html = `<div class="section-title">Usuários</div>`;
    html += `<div class="note">Como Usuário Mestre, você pode alterar o perfil de qualquer conta. A troca é salva automaticamente ao selecionar uma nova opção.</div>`;
    const usuarios = state.usuarios || [];
    if (!usuarios.length){
      html += `<div class="empty-state">Nenhum usuário encontrado ainda.</div>`;
      return html;
    }
    html += `<table class="roster"><tr><th>Nome</th><th>E-mail</th><th>Perfil</th><th>Status</th><th>Ação</th></tr>`;
    usuarios.forEach(u => {
      html += `<tr>
        <td>${esc(u.name || '—')}</td>
        <td>${esc(u.email || '—')}</td>
        <td>
          <select data-user-role="${esc(u.id)}">
            <option value="aluno" ${u.role==='aluno'?'selected':''}>Aluno(a)</option>
            <option value="pending_professor" ${u.role==='pending_professor'?'selected':''}>Professor(a) — pendente</option>
            <option value="professor" ${u.role==='professor'?'selected':''}>Professor(a)</option>
            <option value="admin" ${u.role==='admin'?'selected':''}>Usuário Mestre</option>
          </select>
        </td>
        <td>${u.role==='pending_professor'?'<span class="status-badge warn">Aguardando aprovação</span>':'<span class="status-badge ok">Ativo</span>'}</td>
        <td>${u.role==='pending_professor'?`<button class="btn-outline small" data-approve-prof="${esc(u.id)}">Aprovar Professor</button>`:'—'}</td>
      </tr>`;
    });
    html += `</table>`;
    return html;
  }

  function renderSuporte(){
    const role = state.user.role;
    let tabs;
    if (role === 'aluno') tabs = [['professor','Professor'],['admin','Administração']];
    else if (role === 'professor') tabs = [['alunos','Alunos'],['admin','Administração']];
    else tabs = [['alunos','Alunos'],['professores','Professores']];

    let html = `<div class="note">Use este canal para tirar dúvidas, relatar problemas ou conversar com a equipe da disciplina.</div>`;
    html += `<div class="ptabs">` + tabs.map(([k,l]) => `<div class="ptab ${state.suporteTab===k?'active':''}" data-suporte-tab="${k}">${esc(l)}</div>`).join('') + `</div>`;

    const inboxMode = (role === 'professor' && state.suporteTab === 'alunos') || role === 'admin';
    if (inboxMode){
      if (state.suporteActiveThreadKey){
        html += `<span class="back-link" id="back-suporte-thread">← Voltar às conversas</span>`;
        html += `<h4 style="margin:6px 0 14px">${esc(state.suporteActiveThreadKey)}</h4>`;
        html += renderThreadConversation(state.suporteThread, role);
      } else {
        html += `<div class="toolbar"><button class="btn-outline" id="btn-print-support-list">Relatório / Salvar PDF</button></div>` + renderInboxList(state.suporteInbox);
      }
    } else {
      html += renderThreadConversation(state.suporteThread, role);
    }
    return html;
  }

  function renderProfessor(){
    // Top navigation already controls state.professorTab
    if (state.professorTab === 'turmas') return renderTurmasSection();
    if (state.professorTab === 'planejamento') return renderPlanning();
    if (state.professorTab === 'auditoria') return renderAuditoria();
    if (state.professorTab === 'correcoes') return renderCorrecoesPendentes();
    if (state.professorTab === 'relatorios') return renderRelatorios();
    if (state.professorTab === 'backup') return renderBackup();
    if (state.professorTab === 'operacional') return renderManualOperacional();
    if (state.professorTab === 'checklist') return renderChecklistStatus();
    if (state.professorTab === 'guia') return renderGuiaPedagogico();
    return renderAcompanhamento();
  }

  function renderAuditoria(){
    let html = `<div class="section-title">Auditoria</div>`;
    html += `<div class="note">Registro cronológico das ações e dos acessos à plataforma. Entradas e saídas registram data/hora, usuário, perfil e e-mail disponível.</div><div class="toolbar"><button class="btn-outline ${!state.accessAuditOnly?'active':''}" id="audit-all">Todos os eventos</button><button class="btn-outline ${state.accessAuditOnly?'active':''}" id="audit-access">Somente acessos</button></div>`;
    const log = (state.auditLog || []).filter(e=>!state.accessAuditOnly || e.type==='login' || e.type==='logout');
    if (!log.length){ html += `<div class="empty-state">Nenhum evento registrado ainda.</div>`; return html; }
    html += `<div class="table-scroll"><table class="roster"><tr><th>Quando</th><th>Usuário</th><th>Perfil</th><th>Evento</th></tr>`;
    log.forEach(e => { const date=e.ts?new Date(e.ts).toLocaleString('pt-BR'):'—'; html+=`<tr><td style="white-space:nowrap">${esc(date)}</td><td>${esc(e.actor||'Sistema')}${e.email?`<div class="cell-status">${esc(e.email)}</div>`:''}</td><td>${esc(roleLabelFor(e.role||''))}</td><td>${esc(e.detail)}</td></tr>`; });
    html += `</table></div>`; return html;
  }

  function renderCorrecoesPendentes(){
    const data = state.correcoesPendentes || { incompletos: [], mensagensPendentes: [], modulosPendentes: [] };
    let html = `<div class="section-title">Pendências</div>`;
    html += `<div class="note">Esta área reúne situações que exigem atuação do professor. As notas são calculadas automaticamente; a liberação do próximo módulo é uma decisão pedagógica individual do professor.</div>`;
    html += `<h4 style="margin:18px 0 8px">Alunos aguardando liberação de módulo (${data.modulosPendentes.length})</h4>`;
    if (!data.modulosPendentes.length) html += `<div class="empty-state">Nenhum aluno aguardando liberação no momento.</div>`;
    else data.modulosPendentes.forEach((it,idx)=>{ const next=MODULES.find(m=>m.num===it.module.num+1); html += `<div class="review-card"><div class="review-head"><div><b>${esc(it.student.name)}</b><div class="thread-preview">M${it.module.num} — ${esc(it.module.title)}</div></div><span class="status-badge info">Aguardando liberação</span></div><div class="review-grid"><div><span>Nota do Módulo</span><b>${fmtGrade(effectiveModuleGrade(it.mp))}</b></div><div><span>Próxima etapa</span><b>${next?'M'+next.num:'Conclusão da disciplina'}</b></div></div><div class="review-actions"><button class="btn-brass" data-release-module="${idx}">${next?'Liberar M'+next.num:'Concluir disciplina'}</button></div></div>`; });
    html += `<h4 style="margin:24px 0 8px">Cadastros a regularizar (${data.incompletos.length})</h4>`;
    if (!data.incompletos.length) html += `<div class="empty-state">Nenhum cadastro pendente no momento.</div>`;
    else data.incompletos.forEach(it=>{ html += `<div class="thread-row" data-fix-turma="${esc(it.turmaId)}"><div><b>${esc(it.nome||'(nome não identificado)')}</b><div class="thread-preview">Turma: ${esc(it.turmaNome||it.turmaName||'—')} · ${!it.nome?'Nome ausente · ':''}${!it.matricula?'Matrícula ausente':''}</div></div><span class="back-link">Regularizar →</span></div>`; });
    html += `<h4 style="margin:24px 0 8px">Mensagens aguardando resposta (${data.mensagensPendentes.length})</h4>`;
    if (!data.mensagensPendentes.length) html += `<div class="empty-state">Nenhuma mensagem pendente.</div>`;
    else data.mensagensPendentes.forEach(t=>{const last=t.messages[t.messages.length-1]; html += `<div class="thread-row" data-goto-thread="${esc(t.participantName)}"><div><b>${esc(t.participantName)}</b><div class="thread-preview">${esc(last.text.slice(0,70))}</div></div><span class="back-link">Responder →</span></div>`;});
    return html;
  }

  function renderAcompanhamento(){
    const roster = professorRoster(state.roster || []).slice().sort((a,b)=>(a.name||'').localeCompare(b.name||''));
    let html = `<div class="note">As notas são calculadas automaticamente pelo sistema. Clique em <b>Ver detalhes</b> para visualizar as notas originais, substituições pela Recuperação e a Nota do Módulo.</div>`;
    html += `<div class="section-title">Notas da Turma (${roster.length} aluno${roster.length===1?'':'s'})</div>`;
    html += `<div class="toolbar"><button class="btn-outline" id="btn-print-report">Imprimir / Salvar PDF</button><button class="btn-brass" id="btn-export-grades">Exportar CSV</button></div>`;
    if (!roster.length) return html + `<div class="empty-state">Nenhum aluno entrou na plataforma ainda.</div>`;
    html += `<div class="table-scroll"><table class="roster"><tr><th>Aluno</th>${MODULES.map(m=>`<th class="num">M${m.num}</th>`).join('')}<th class="num">Média</th><th class="num">Ação</th></tr>`;
    roster.forEach((st,idx)=>{
      const grades=[]; html += `<tr><td><b>${esc(st.name)}</b></td>`;
      MODULES.forEach(m=>{const mp=st.modules[m.id]; const v=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null; if(v!==null) grades.push(Number(v)); html += `<td class="num"><b>${fmtGrade(v)}</b><div class="cell-status">${moduleStatusLabel(mp)}</div></td>`;});
      const avg=grades.length?grades.reduce((a,b)=>a+b,0)/grades.length:null;
      html += `<td class="num"><b>${fmtGrade(avg)}</b></td><td class="num"><button class="btn-brass" data-toggle-student-details="${idx}">Ver detalhes</button></td></tr>`;
      html += `<tr data-student-detail="${idx}" style="display:none"><td colspan="8"><div class="card-box"><h4>${esc(st.name)} — Detalhamento das avaliações</h4><div class="table-scroll"><table class="roster"><tr><th>Módulo</th><th class="num">Ex. 1</th><th class="num">Ex. 2</th><th class="num">Ex. 3</th><th class="num">Ex. 4</th><th class="num">Ex. 5</th><th class="num">Quiz</th><th class="num">Recuperação</th><th class="num">Nota do Módulo</th><th>Situação</th></tr>`;
      MODULES.forEach(m=>{
        const mp=st.modules[m.id], adjusted=effectiveAssessmentScores10(mp), rec=score10(mp.recoveryScore,mp.recoveryTotal), quizOrig=score10(mp.quizScore,mp.quizTotal);
        const exCells=Array.from({length:5},(_,i)=>{const orig=Array.isArray(mp.exerciseScores)?mp.exerciseScores[i]:null, eff=adjusted.exercises[i], rep=!!(adjusted.replaced&&adjusted.replaced[i]); if(eff===null||eff===undefined)return '<td class="num">—</td>'; return `<td class="num">${rep?`${fmtGrade(orig)} → <b>${fmtGrade(eff)}</b>`:fmtGrade(eff)}</td>`;}).join('');
        const qRep=!!(adjusted.replaced&&adjusted.replaced[5]); const qCell=adjusted.quiz===null||adjusted.quiz===undefined?'—':(qRep?`${fmtGrade(quizOrig)} → <b>${fmtGrade(adjusted.quiz)}</b>`:fmtGrade(adjusted.quiz));
        const grade=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null;
        html += `<tr><td><b>M${m.num}</b></td>${exCells}<td class="num">${qCell}</td><td class="num">${fmtGrade(rec)}</td><td class="num"><b>${fmtGrade(grade)}</b></td><td>${moduleStatusLabel(mp)}</td></tr>`;
      });
      html += `</table></div><div class="note" style="margin-top:12px"><b>Legenda:</b> quando a Recuperação substitui uma nota inferior, é exibido <b>original → considerada</b>. A Recuperação não é uma 7ª nota.</div></div></td></tr>`;
    });
    html += `</table></div>`; return html;
  }

  function csvEscape(v){ return '"'+String(v===null||v===undefined?'':v).replace(/"/g,'""')+'"'; }
  function downloadText(filename,text,type){ const blob=new Blob([text],{type:type||'text/plain;charset=utf-8'}); const u=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=u; a.download=filename; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(u); }
  function gradesCsv(){
    const rows=[['Aluno','Módulo','Ex1 Original','Ex1 Considerada','Ex2 Original','Ex2 Considerada','Ex3 Original','Ex3 Considerada','Ex4 Original','Ex4 Considerada','Ex5 Original','Ex5 Considerada','Quiz Original','Quiz Considerado','Recuperação','Nota do Módulo','Situação','Progresso Geral']];
    professorRoster(state.roster||[]).slice().sort((a,b)=>(a.name||'').localeCompare(b.name||'')).forEach(st=>{
      MODULES.forEach(m=>{
        const mp=st.modules[m.id], a=effectiveAssessmentScores10(mp), ex=[];
        for(let i=0;i<5;i++){const orig=Array.isArray(mp.exerciseScores)?mp.exerciseScores[i]:null; ex.push(fmtGrade(orig),fmtGrade(a.exercises[i]));}
        const qOrig=score10(mp.quizScore,mp.quizTotal), rec=score10(mp.recoveryScore,mp.recoveryTotal), grade=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null;
        rows.push([st.name,'M'+m.num,...ex,fmtGrade(qOrig),fmtGrade(a.quiz),fmtGrade(rec),fmtGrade(grade),moduleStatusLabel(mp),overallPct(st)+'%']);
      });
    });
    return '\ufeff'+rows.map(r=>r.map(csvEscape).join(';')).join('\n');
  }
  function renderRelatorios(){
    const roster=professorRoster(state.roster||[]).slice().sort((a,b)=>(a.name||'').localeCompare(b.name||''));
    let html=`<div class="section-title">Relatório de Desempenho</div><div class="note">Visão geral e detalhada das notas e do progresso da turma. As notas são calculadas automaticamente e as substituições pela Recuperação permanecem identificadas.</div><div class="toolbar"><button class="btn-outline" id="btn-print-report">Imprimir / Salvar PDF</button><button class="btn-brass" id="btn-export-grades">Exportar CSV</button></div>`;
    if(!roster.length) return html+`<div class="empty-state">Nenhum aluno entrou na plataforma ainda.</div>`;
    html+=`<h4 style="margin:18px 0 8px">Resumo da Turma</h4><div class="table-scroll"><table class="roster"><tr><th>Aluno</th>${MODULES.map(m=>`<th class="num">M${m.num}</th>`).join('')}<th class="num">Média Geral</th><th class="num">Progresso</th></tr>`;
    roster.forEach(st=>{const vals=[]; html+=`<tr><td><b>${esc(st.name)}</b></td>`; MODULES.forEach(m=>{const mp=st.modules[m.id],v=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null;if(v!==null)vals.push(Number(v));html+=`<td class="num">${fmtGrade(v)}</td>`;}); const avg=vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null; html+=`<td class="num"><b>${fmtGrade(avg)}</b></td><td class="num">${overallPct(st)}%</td></tr>`;});
    html+=`</table></div><h4 style="margin:24px 0 8px">Detalhamento por Atividade</h4><div class="table-scroll"><table class="roster"><tr><th>Aluno</th><th>Módulo</th><th class="num">Ex. 1</th><th class="num">Ex. 2</th><th class="num">Ex. 3</th><th class="num">Ex. 4</th><th class="num">Ex. 5</th><th class="num">Quiz</th><th class="num">Recuperação</th><th class="num">Nota do Módulo</th><th>Situação</th></tr>`;
    roster.forEach(st=>MODULES.forEach(m=>{const mp=st.modules[m.id],a=effectiveAssessmentScores10(mp),rec=score10(mp.recoveryScore,mp.recoveryTotal),qOrig=score10(mp.quizScore,mp.quizTotal),grade=moduleReadyForSubmission(mp,m)?effectiveModuleGrade(mp):null; const fmt=(orig,eff,rep)=>eff===null||eff===undefined?'—':(rep?`${fmtGrade(orig)} → <b>${fmtGrade(eff)}</b>`:fmtGrade(eff)); html+=`<tr><td>${esc(st.name)}</td><td><b>M${m.num}</b></td>${Array.from({length:5},(_,i)=>`<td class="num">${fmt(Array.isArray(mp.exerciseScores)?mp.exerciseScores[i]:null,a.exercises[i],!!(a.replaced&&a.replaced[i]))}</td>`).join('')}<td class="num">${fmt(qOrig,a.quiz,!!(a.replaced&&a.replaced[5]))}</td><td class="num">${fmtGrade(rec)}</td><td class="num"><b>${fmtGrade(grade)}</b></td><td>${moduleStatusLabel(mp)}</td></tr>`;}));
    html+=`</table></div>`; return html;
  }
  function renderBackup(){
    return `<div class="section-title">Backup</div><div class="note">Gera um arquivo JSON com as turmas deste professor e os registros pedagógicos dos alunos que constam nessas turmas. O arquivo não altera nem apaga dados do Firestore.</div><div class="card-box"><h4>Backup pedagógico</h4><p class="desc">Inclui turmas, alunos cadastrados, progresso/notas e os Planejamentos Semestrais e Planos de Aula do professor.</p><button class="btn-brass" id="btn-export-backup">Gerar backup JSON</button></div>`;
  }

  function docShell(title,body){ return `<div class="section-title">${esc(title)}</div><div class="toolbar"><button class="btn-outline" id="btn-print-doc">Imprimir / Salvar PDF</button></div><div class="panel doc-panel">${body}</div>`; }
  function renderManualOperacional(){ return docShell('Manual Operacional',`<h4>1. Acesso e perfis</h4><p>O acesso é realizado exclusivamente com conta Google. Alunos entram como Aluno(a); Professores novos aguardam aprovação do Usuário Mestre.</p><h4>2. Turmas e alunos</h4><p>Crie a turma, cadastre alunos individualmente ou importe PDF, confira nome e matrícula e salve os prazos dos cinco módulos.</p><h4>3. Prazos e módulos</h4><p>O Módulo 1 inicia liberado. Os demais são liberados somente após a realização obrigatória das 5 listas, do Quiz e da Recuperação do módulo anterior e a liberação individual do professor. Após o prazo, o módulo bloqueia; quando o professor autoriza entrega em atraso, aplica-se desconto automático de 2,0 pontos na primeira conclusão fora do prazo original.</p><h4>4. Avaliação e notas</h4><p>Listas, Quiz e Recuperação são autocorrigidos e a Recuperação é obrigatória. Ela substitui todas as notas inferiores entre as 6 atividades avaliativas. A Nota do Módulo é calculada automaticamente; o professor não corrige a nota, mas libera individualmente a progressão para o módulo seguinte.</p><h4>5. Planejamento docente</h4><p>O menu Planejamento possui os submenus Planejamento Semestral e Plano de Aula. Os registros podem ser criados, editados, impressos ou salvos em PDF. O Plano de Aula exige data de início e fim, tem periodicidade máxima de 30 dias e não permite sobreposição de períodos para a mesma turma.</p><h4>6. Pendências, relatórios e suporte</h4><p>Pendências reúne alunos aguardando liberação de módulo, cadastros a regularizar e mensagens aguardando resposta. Relatórios apresentam resumo e detalhamento por atividade; Auditoria, Backup e Suporte permanecem disponíveis no painel do Professor.</p>`); }
  function renderGuiaPedagogico(){ return docShell('Guia Pedagógico do Professor',`<h4>Organização didática</h4><p>A disciplina está estruturada em cinco módulos progressivos. O estudante conclui o ciclo avaliativo após realizar as cinco listas, o Quiz e a Recuperação obrigatória; o avanço ocorre somente após a liberação individual do professor.</p><h4>Estrutura de cada módulo</h4><ul><li>Conteúdo teórico e exemplos;</li><li>5 listas autocorrigidas de 10 questões;</li><li>Quiz avaliativo autocorrigido;</li><li>Recuperação obrigatória e autocorrigida;</li><li>Nota do Módulo calculada automaticamente.</li></ul><h4>Avaliação</h4><p>Os 5 exercícios e o Quiz têm o mesmo peso. A Recuperação não é uma 7ª nota: substitui individualmente todas as notas inferiores entre essas 6 atividades. Entrega após o prazo original, quando autorizada, recebe desconto automático de 2,0 pontos.</p><h4>Intervenção pedagógica</h4><p>Use Notas da Turma e Relatórios para acompanhar o desempenho detalhado; Pendências para liberar individualmente o avanço dos alunos, regularizar cadastros e responder mensagens; Auditoria para rastreabilidade e Suporte para dúvidas e ocorrências.</p><h4>Boas práticas</h4><p>Defina os prazos antes da abertura da turma, acompanhe o progresso e as notas por atividade, trate as pendências operacionais e gere backup periódico.</p>`); }

  function renderTurmaList(){
    let html = `<div class="note">Crie turmas e monte a lista de alunos (nome e matrícula) enviando um PDF ou adicionando um a um.</div>`;
    html += `<div class="section-title" style="display:flex;justify-content:space-between;align-items:center;border-bottom:none;">
      <span>Minhas turmas (${state.turmas.length})</span>
      <button class="btn-brass" id="btn-new-turma">+ Nova turma</button>
    </div>`;

    if (state.creatingTurma){
      html += `<div class="card-box">
        <h4>Criar nova turma</h4>
        <div class="inline-form">
          <div class="field">
            <label for="new-turma-name">Nome da turma</label>
            <input type="text" id="new-turma-name" placeholder="Ex.: Contabilidade Avançada — Noturno 2026" value="${esc(state.newTurmaName)}" />
          </div>
          <button class="btn-brass" id="btn-confirm-turma">Criar</button>
          <button class="btn-outline" id="btn-cancel-turma">Cancelar</button>
        </div>
      </div>`;
    }

    if (state.turmas.length === 0 && !state.creatingTurma){
      html += `<div class="empty-state">Nenhuma turma criada ainda.<br>Clique em "+ Nova turma" para começar.</div>`;
    } else {
      state.turmas.forEach(t => {
        const date = t.createdAt ? new Date(t.createdAt).toLocaleDateString('pt-BR') : '';
        html += `<div class="turma-card" data-turma="${esc(t.id)}">
          <div>
            <h3>${esc(t.name)}</h3>
            <p>${t.students.length} aluno${t.students.length===1?'':'s'} matriculado${t.students.length===1?'':'s'}${date ? ' · criada em ' + date : ''}</p>
          </div>
          <span class="back-link">Abrir →</span>
        </div>`;
      });
    }
    return html;
  }

  function renderTurmaDetail(turma){
    let html = `<span class="back-link" id="back-turmas">← Voltar às turmas</span>`;
    html += `<div class="module-header" style="--mcolor:#A87C3F">
      <h2 class="serif">${esc(turma.name)}</h2>
      <div class="subtitle">${turma.students.length} aluno${turma.students.length===1?'':'s'} matriculado${turma.students.length===1?'':'s'}</div>
    </div>`;

    // Individual add
    html += `<div class="card-box">
      <h4>Adicionar aluno individualmente</h4>
      <p class="desc">Informe o nome completo e a matrícula do aluno.</p>
      <div class="inline-form">
        <div class="field">
          <label for="ind-nome">Nome do aluno</label>
          <input type="text" id="ind-nome" placeholder="Ex.: João da Silva" value="${esc(state.newStudentNome)}" />
        </div>
        <div class="field">
          <label for="ind-matricula">Matrícula</label>
          <input type="text" id="ind-matricula" placeholder="Ex.: 2026001234" value="${esc(state.newStudentMatricula)}" />
        </div>
        <button class="btn-brass" id="btn-add-individual">Adicionar aluno</button>
      </div>
    </div>`;

    // PDF import
    html += `<div class="card-box">
      <h4>Importar lista de alunos (PDF)</h4>
      <p class="desc">Envie um PDF contendo o nome e a matrícula dos alunos (um por linha, ou em tabela). O texto extraído aparece abaixo para conferência antes de adicionar a lista à turma.</p>
      <div class="pdf-box">
        <input type="file" id="pdf-file" accept="application/pdf" />
        ${state.pdfStatus === 'loading' ? '<div class="pdf-status">Lendo o PDF…</div>' : ''}
        ${state.pdfStatus === 'error' ? `<div class="pdf-status err">${esc(state.pdfStatusMsg)}</div>` : ''}
      </div>`;

    if (state.pdfRawText){
      html += `<label style="margin-top:14px">Texto extraído — revise e corrija se necessário antes de converter</label>
        <textarea class="pdf-text" id="pdf-text">${esc(state.pdfRawText)}</textarea>
        <button class="btn-outline" id="btn-parse-pdf" style="margin-top:10px">Converter em lista de alunos</button>`;
    }

    if (state.pdfPreview && state.pdfPreview.length){
      html += `<h4 style="margin-top:20px">Pré-visualização (${state.pdfPreview.length} aluno${state.pdfPreview.length===1?'':'s'})</h4>
        <p class="desc">Confira e corrija nome e matrícula antes de confirmar. Remova linhas que não correspondem a alunos.</p>
        <table class="preview"><tr><th>Nome</th><th>Matrícula</th><th></th></tr>`;
      state.pdfPreview.forEach((row,i) => {
        html += `<tr>
          <td><input type="text" data-prev-nome="${i}" value="${esc(row.nome)}" /></td>
          <td><input type="text" data-prev-matricula="${i}" value="${esc(row.matricula)}" style="width:130px" /></td>
          <td class="rm"><button class="link-btn" data-prev-remove="${i}">remover</button></td>
        </tr>`;
      });
      html += `</table>
        <button class="btn-brass" id="btn-confirm-pdf" style="margin-top:14px">Adicionar ${state.pdfPreview.length} aluno${state.pdfPreview.length===1?'':'s'} à turma</button>
        <button class="btn-outline" id="btn-cancel-pdf" style="margin-top:14px">Cancelar</button>`;
    }
    html += `</div>`;

    // Prazos dos módulos
    turma.moduleSettings=turma.moduleSettings||{};
    html += `<div class="card-box"><h4>Prazos e liberação dos módulos</h4><p class="desc">Defina o prazo de cada módulo. Após o vencimento o módulo é bloqueado automaticamente. Marque "Permitir atraso" para reabrir a entrega; a primeira entrega após o prazo original recebe desconto automático de 2,0 pontos.</p><div class="deadline-grid">`;
    MODULES.forEach(m=>{const s=turma.moduleSettings[m.id]||{}; html+=`<div class="deadline-card"><b>M${m.num} — ${esc(m.title)}</b><label>Prazo</label><input type="datetime-local" data-deadline-module="${m.id}" value="${esc(s.deadline||'')}"><label class="checkline"><input type="checkbox" data-late-module="${m.id}" ${s.allowLate?'checked':''}> Permitir entrega em atraso</label></div>`;});
    html += `</div><button class="btn-brass" id="btn-save-deadlines">Salvar prazos</button></div>`;

    // Roster table
    html += `<div class="section-title">Alunos matriculados</div>`;
    if (turma.students.length === 0){
      html += `<div class="empty-state">Nenhum aluno cadastrado nesta turma ainda.</div>`;
    } else {
      html += `<table class="students"><tr><th>Nome</th><th>Matrícula</th><th></th></tr>`;
      turma.students.forEach((s,i) => {
        html += `<tr>
          <td>${esc(s.nome)}</td>
          <td>${esc(s.matricula || '—')}</td>
          <td class="rm"><button class="link-btn" data-student-remove="${i}">remover</button></td>
        </tr>`;
      });
      html += `</table>`;
    }
    return html;
  }

  function renderExerciseItem(it, idx){
    let optsHtml = '';
    if (it.type === 'mc'){
      optsHtml = `<div class="exercise-choices">` + it.opts.map((o,i)=>`<label class="quiz-opt"><input type="radio" name="e${idx}" value="${i}" required> <span>${String.fromCharCode(97+i)}) ${esc(o)}</span></label>`).join('') + `</div>`;
    } else {
      optsHtml = `<div class="exercise-choices"><label class="quiz-opt"><input type="radio" name="e${idx}" value="1" required> Verdadeiro</label><label class="quiz-opt"><input type="radio" name="e${idx}" value="0" required> Falso</label></div>`;
    }
    return `<div class="exercise"><div class="stmt"><span class="tag">${it.type==='mc'?'Múltipla escolha':'V / F'}</span><b>${idx+1}.</b> ${esc(it.q)}</div>${optsHtml}</div>`;
  }

  function renderModule(){
    const m = MODULES.find(x => x.id === state.activeModuleId);
    const mp = state.progress.modules[m.id];
    const access=moduleAccess(m);
    if(access.locked) return `<span class="back-link" id="back-dash">← Voltar aos módulos</span><div class="panel"><div class="empty-state"><b>Módulo bloqueado.</b><br>${esc(access.reason)}</div></div>`;
    let html = `<span class="back-link" id="back-dash">← Voltar aos módulos</span>
      <div class="module-header" style="--mcolor:${m.color}">
        <h2 class="serif">${String(m.num).padStart(2,'0')}. ${esc(m.title)}</h2>
        <div class="subtitle">${esc(m.subtitle)}</div>
        <div class="deadline-text">${esc(moduleDeadlineText(m))}${access.late?' · <b>Será aplicado desconto de 2,0 pontos na primeira entrega.</b>':''}</div>
      </div>
      <div class="tabs">
        <div class="tab ${state.activeTab==='conteudo'?'active':''}" data-tab="conteudo">Conteúdo</div>
        <div class="tab ${state.activeTab==='exercicios'?'active':''}" data-tab="exercicios">Exercícios</div>
        <div class="tab ${state.activeTab==='quiz'?'active':''}" data-tab="quiz">Quiz</div>
        <div class="tab ${state.activeTab==='recuperacao'?'active':''}" data-tab="recuperacao">Recuperação</div>
      </div>
      <div class="panel">`;

    if (state.activeTab === 'conteudo'){
      html += m.content;
      html += `<button class="mark-btn" id="btn-read" ${mp.contentRead?'disabled':''}>${mp.contentRead ? '✓ Conteúdo marcado como lido' : 'Marcar conteúdo como lido'}</button>`;

    } else if (state.activeTab === 'exercicios'){
  const nextList = nextExerciseListIndex(mp,m);
  if (!exerciseListDone(mp,state.activeExerciseList) && exerciseListLocked(mp,m,state.activeExerciseList)) {
    state.activeExerciseList = nextList < m.exerciseLists.length ? nextList : Math.max(0,m.exerciseLists.length-1);
  }
  let sub = `<div class="sublist-tabs">`;
  m.exerciseLists.forEach((l,i) => {
    const done = exerciseListDone(mp,i);
    const locked = exerciseListLocked(mp,m,i);
    const label = done ? `Lista ${i+1} ✓ Feita` : (locked ? `Lista ${i+1} 🔒` : `Lista ${i+1}`);
    sub += `<div class="sub-tab ${state.activeExerciseList===i?'active':''} ${done?'done':''} ${locked?'locked':''}" data-list="${i}" data-locked="${locked?'1':'0'}">${label}</div>`;
  });
  sub += `</div>`;
  html += sub;
  const list = m.exerciseLists[state.activeExerciseList];
  const listScore = mp.exerciseScores[state.activeExerciseList];
  const currentLocked = exerciseListLocked(mp,m,state.activeExerciseList);
  html += `<h4 style="margin-top:0">${esc(list.title)} <span style="font-weight:400;color:var(--ink-soft);font-size:13px">— 10 questões · autocorreção</span></h4>`;
  if (listScore !== null && listScore !== undefined){
    html += `<div class="quiz-score"><b>✓ Exercício feito.</b> Nota registrada: <b>${fmtGrade(listScore)} / 10,0</b>.<br><span class="thread-preview">Esta lista já foi concluída e não pode ser refeita.</span></div>`;
    if (nextList < m.exerciseLists.length) html += `<p class="thread-preview">Próxima atividade liberada: <b>Lista ${nextList+1}</b>.</p>`;
  } else if (currentLocked){
    html += `<div class="empty-state">Esta lista ainda está bloqueada. Conclua primeiro a lista anterior.</div>`;
  } else {
    html += `<div class="note">Esta é a próxima lista disponível. Após a correção, a nota ficará registrada e esta lista não poderá ser refeita.</div>`;
    html += `<form id="exercise-form">`;
    list.items.forEach((it,idx) => { html += renderExerciseItem(it, idx); });
    html += `<button class="mark-btn" type="submit">Corrigir e finalizar lista</button></form>`;
  }

    } else if (state.activeTab === 'quiz'){
      if (mp.quizScore !== null){
        html += `<div class="quiz-score">Você já concluiu este quiz. Resultado: <b>${mp.quizScore} de ${mp.quizTotal}</b> acertos.</div>`;
      } else {
        html += `<form id="quiz-form" data-kind="quiz">`;
        m.quiz.forEach((q,qi) => {
          html += `<div class="quiz-q"><p class="q">${qi+1}. ${esc(q.q)}</p>`;
          q.opts.forEach((opt,oi) => {
            html += `<label class="quiz-opt"><input type="radio" name="q${qi}" value="${oi}" required> <span>${esc(opt)}</span></label>`;
          });
          html += `</div>`;
        });
        html += `<button type="submit" class="mark-btn">Corrigir quiz</button></form>`;
      }

    } else if (state.activeTab === 'recuperacao'){
      html += `<div class="recovery-intro">A recuperação é obrigatória em todos os módulos e não é uma 7ª nota da média. Os 5 exercícios e o Quiz valem 10,0 pontos cada e têm o mesmo peso. A nota da Recuperação é comparada individualmente com as 6 atividades e substitui todas as notas inferiores, inclusive a do Quiz.</div>`;
      if (mp.recoveryScore !== null){
        html += `<div class="quiz-score">Recuperação já realizada. Resultado: <b>${mp.recoveryScore} de ${mp.recoveryTotal}</b> acertos.</div>`;
      } else {
        html += `<form id="quiz-form" data-kind="recovery">`;
        m.recovery.forEach((q,qi) => {
          html += `<div class="quiz-q"><p class="q">${qi+1}. ${esc(q.q)}</p>`;
          q.opts.forEach((opt,oi) => {
            html += `<label class="quiz-opt"><input type="radio" name="q${qi}" value="${oi}" required> <span>${esc(opt)}</span></label>`;
          });
          html += `</div>`;
        });
        html += `<button type="submit" class="mark-btn">Corrigir recuperação</button></form>`;
      }
    }
    const corr = correctionState(mp);
    html += `<div class="module-correction"><h4>Situação do módulo</h4><div style="margin-bottom:8px">${correctionBadge(mp)}</div>`;
    if (corr.feedback) html += `<div class="feedback-box"><b>Registro anterior do professor:</b> ${esc(corr.feedback)}</div>`;
    if (moduleReadyForSubmission(mp,m) && corr.released) html += `<div class="quiz-score">Módulo concluído e liberado. Nota do Módulo: <b>${fmtGrade(effectiveModuleGrade(mp))} / 10,0</b></div><p class="thread-preview">O próximo módulo está liberado, respeitando o prazo definido pelo professor.</p>`;
    else if (moduleReadyForSubmission(mp,m)) html += `<div class="quiz-score">Ciclo avaliativo concluído. Nota do Módulo: <b>${fmtGrade(effectiveModuleGrade(mp))} / 10,0</b></div><p class="thread-preview">Aguarde a liberação individual do professor para avançar ao próximo módulo.</p>`;
    else html += `<p class="thread-preview">Para concluir o ciclo avaliativo, realize obrigatoriamente as 5 listas, o Quiz e a Recuperação. A leitura do conteúdo compõe o progresso de estudo, mas não bloqueia o cálculo da nota.</p>`;
    html += `</div>`;
    html += `</div>`;
    return html;
  }

  function attachHandlers(){
    const logout = document.getElementById('btn-logout');
    if (logout) logout.addEventListener('click', async () => {
      state.professorTab = 'acompanhamento'; state.turmas = []; state.activeTurmaId = null;
      state.creatingTurma = false; state.newTurmaName = ''; state.newStudentNome = ''; state.newStudentMatricula = '';
      state.pdfStatus = ''; state.pdfStatusMsg = ''; state.pdfRawText = ''; state.pdfPreview = null;
      state.suporteTab = null; state.suporteThread = null; state.suporteInbox = null;
      state.suporteActiveThreadKey = null; state.suporteNewMessage = '';
      state.authError = ''; state.masterCode = ''; state.loginMatricula = ''; state.signupRole = 'aluno';
      await logAudit('logout', `${state.user ? state.user.name : 'Usuário'} saiu da plataforma.`);
      await signOut(auth);
      // onAuthStateChanged cuida de limpar state.user e voltar para a tela de login.
    });

    document.querySelectorAll('.module-row').forEach(row => {
      row.addEventListener('click', () => {
        if(row.getAttribute('data-locked')==='1') return;
        state.activeModuleId = row.getAttribute('data-module');
        state.activeTab = 'conteudo';
        state.activeExerciseList = 0;
        state.view = 'module';
        render();
      });
    });

    const back = document.getElementById('back-dash');
    if (back) back.addEventListener('click', () => { state.view = 'dashboard'; render(); });

    document.querySelectorAll('.tab').forEach(t => {
      t.addEventListener('click', () => { state.activeTab = t.getAttribute('data-tab'); render(); });
    });

    document.querySelectorAll('.sub-tab').forEach(t => {
      t.addEventListener('click', () => { if (t.getAttribute('data-locked') === '1') return; state.activeExerciseList = parseInt(t.getAttribute('data-list'),10); render(); });
    });

    const btnRead = document.getElementById('btn-read');
    if (btnRead) btnRead.addEventListener('click', async () => {
      state.progress.modules[state.activeModuleId].contentRead = true;
      await saveProgress(state.progress);
      render();
    });

    const exerciseForm = document.getElementById('exercise-form');
if (exerciseForm) exerciseForm.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const m=MODULES.find(x=>x.id===state.activeModuleId);
  const mp=state.progress.modules[state.activeModuleId];
  const current=state.activeExerciseList;
  if (exerciseListDone(mp,current)) { render(); return; }
  if (exerciseListLocked(mp,m,current)) { state.activeExerciseList=nextExerciseListIndex(mp,m); render(); return; }
  const list=m.exerciseLists[current], fd=new FormData(exerciseForm); let score=0;
  list.items.forEach((it,i)=>{const raw=fd.get('e'+i); let ok=false; if(it.type==='mc'){const chosen=raw===null?-1:parseInt(raw,10); ok=chosen===it.correct;} else {const chosen=raw==='1'; ok=chosen===it.correct;} if(ok) score++;});
  mp.exerciseScores[current]=score; mp.exerciseListsDone[current]=true;
  await saveProgress(state.progress);
  await logAudit('lista_autocorrigida',`${state.user.name} concluiu a Lista ${current+1} do módulo "${m.title}" — ${score}/10. Lista encerrada sem possibilidade de refazer.`);
  render();
});


    const quizForm = document.getElementById('quiz-form');
    if (quizForm) quizForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const kind = quizForm.getAttribute('data-kind'); // 'quiz' or 'recovery'
      const m = MODULES.find(x => x.id === state.activeModuleId);
      const bank = kind === 'quiz' ? m.quiz : m.recovery;
      const fd = new FormData(quizForm);
      let score = 0;
      const results = [];
      bank.forEach((q,qi) => {
        const val = fd.get('q'+qi);
        const chosen = val === null ? -1 : parseInt(val,10);
        const ok = chosen === q.correct;
        if (ok) score++;
        results.push({ok, explain:q.explain, correctText:q.opts[q.correct]});
      });
      const activeMp = state.progress.modules[state.activeModuleId];
      if (kind === 'quiz') activeMp.quizScore = score;
      else activeMp.recoveryScore = score;
      if (moduleReadyForSubmission(activeMp,m)){
        const c = correctionState(activeMp); const now = Date.now();
        if (!c.firstSubmittedAt){
          const access = moduleAccess(m); c.firstSubmittedAt = now; c.late = !!access.late; c.latePenalty = access.late ? 2 : 0;
          c.history.push({type:'ciclo_avaliativo_concluido',ts:now,late:c.late,latePenalty:c.latePenalty});
        }
        c.status='aguardando_liberacao'; c.reviewedAt=null; c.released=false; c.finalGrade=effectiveModuleGrade(activeMp); activeMp.correction=c;
      }
      await saveProgress(state.progress);
      await logAudit(
        kind === 'quiz' ? 'quiz_concluido' : 'recuperacao_concluida',
        `${state.user.name} concluiu ${kind === 'quiz' ? 'o quiz' : 'a recuperação'} do módulo "${m.title}" — nota ${score}/${bank.length}.`
      );
      const panel = quizForm.parentElement;
      let html = `<div class="quiz-score">Resultado: <b>${score} de ${bank.length}</b> acertos.</div>`;
      bank.forEach((q,qi) => {
        const r = results[qi];
        html += `<div class="quiz-q"><p class="q">${qi+1}. ${esc(q.q)}</p>
          <div class="quiz-result ${r.ok?'ok':'bad'}">${r.ok ? '✓ Correto.' : '✗ Resposta correta: ' + esc(r.correctText) + '.'} ${esc(r.explain)}</div>
        </div>`;
      });
      panel.innerHTML = html;
    });

    // ---- Top navigation ----
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', async () => {
        const key = item.getAttribute('data-nav');
        if (key === 'suporte'){ await openSuporte(); return; }
        if (key === 'manual'){ state.view = 'manual'; render(); return; }
        if (key === 'notas'){ state.view = 'notas'; render(); return; }
        if (key === 'usuarios'){ state.view = 'usuarios'; await loadUsuarios(); render(); return; }
        if (key === 'dashboard'){ state.studentTurma=await loadStudentTurma(state.user.name); state.view = 'dashboard'; render(); return; }
        if (key.indexOf('professor:') === 0){
          const tab = key.split(':')[1];
          state.professorTab = tab;
          state.view = 'professor';
          if (tab === 'auditoria') await loadAuditoria();
          else if (tab === 'correcoes') await loadCorrecoesPendentes();
          else if (tab === 'planejamento') await loadPlanningAll();
          render();
          return;
        }
      });
    });

    // ---- Turmas: list / creation ----
    const btnNewTurma = document.getElementById('btn-new-turma');
    if (btnNewTurma) btnNewTurma.addEventListener('click', () => { state.creatingTurma = true; state.newTurmaName = ''; render(); });

    const newTurmaName = document.getElementById('new-turma-name');
    if (newTurmaName) newTurmaName.addEventListener('input', e => { state.newTurmaName = e.target.value; });

    const btnCancelTurma = document.getElementById('btn-cancel-turma');
    if (btnCancelTurma) btnCancelTurma.addEventListener('click', () => { state.creatingTurma = false; render(); });

    const btnConfirmTurma = document.getElementById('btn-confirm-turma');
    if (btnConfirmTurma) btnConfirmTurma.addEventListener('click', async () => {
      const name = state.newTurmaName.trim();
      if (!name) return;
      const turma = { id: newTurmaId(), name, professor: state.user.name, students: [], createdAt: Date.now() };
      await saveTurma(turma);
      state.turmas.unshift(turma);
      state.creatingTurma = false; state.newTurmaName = '';
      state.activeTurmaId = turma.id;
      await logAudit('turma_criada', `Turma "${turma.name}" criada por ${state.user.name}.`);
      render();
    });

    document.querySelectorAll('.turma-card').forEach(card => {
      card.addEventListener('click', () => {
        state.activeTurmaId = card.getAttribute('data-turma');
        state.pdfStatus = ''; state.pdfStatusMsg = ''; state.pdfRawText = ''; state.pdfPreview = null;
        state.newStudentNome = ''; state.newStudentMatricula = '';
        render();
      });
    });

    const backTurmas = document.getElementById('back-turmas');
    if (backTurmas) backTurmas.addEventListener('click', () => {
      state.activeTurmaId = null;
      state.pdfStatus = ''; state.pdfStatusMsg = ''; state.pdfRawText = ''; state.pdfPreview = null;
      render();
    });

    const btnSaveDeadlines=document.getElementById('btn-save-deadlines');
    if(btnSaveDeadlines) btnSaveDeadlines.addEventListener('click',async()=>{
      const turma=state.turmas.find(t=>t.id===state.activeTurmaId); if(!turma)return; turma.moduleSettings=turma.moduleSettings||{};
      MODULES.forEach(m=>{const inp=document.querySelector(`[data-deadline-module="${m.id}"]`), chk=document.querySelector(`[data-late-module="${m.id}"]`); const deadline=(inp&&inp.value)||''; const prev=turma.moduleSettings[m.id]||{}; turma.moduleSettings[m.id]={deadline,originalDeadline:deadline?(prev.originalDeadline||deadline):'',allowLate:!!(chk&&chk.checked)};});
      await saveTurma(turma); await logAudit('prazos_atualizados',`${state.user.name} atualizou os prazos da turma "${turma.name}".`); alert('Prazos salvos.'); render();
    });

    // ---- Turma detail: individual add ----
    const indNome = document.getElementById('ind-nome');
    if (indNome) indNome.addEventListener('input', e => { state.newStudentNome = e.target.value; });
    const indMatricula = document.getElementById('ind-matricula');
    if (indMatricula) indMatricula.addEventListener('input', e => { state.newStudentMatricula = e.target.value; });

    const btnAddIndividual = document.getElementById('btn-add-individual');
    if (btnAddIndividual) btnAddIndividual.addEventListener('click', async () => {
      const nome = state.newStudentNome.trim();
      const matricula = state.newStudentMatricula.trim();
      if (!nome) return;
      const turma = state.turmas.find(t => t.id === state.activeTurmaId);
      if (!turma) return;
      turma.students.push({ nome, matricula });
      await saveTurma(turma);
      state.newStudentNome = ''; state.newStudentMatricula = '';
      await logAudit('aluno_adicionado', `${nome} adicionado individualmente à turma "${turma.name}".`);
      render();
    });

    // ---- Turma detail: PDF import ----
    const pdfFile = document.getElementById('pdf-file');
    if (pdfFile) pdfFile.addEventListener('change', async (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      state.pdfStatus = 'loading'; state.pdfStatusMsg = ''; state.pdfRawText = ''; state.pdfPreview = null;
      render();
      try {
        const lines = await extractLinesFromPdf(file);
        state.pdfRawText = lines.join('\n');
        state.pdfStatus = lines.length ? 'ready' : 'error';
        state.pdfStatusMsg = lines.length ? '' : 'Não foi possível extrair texto deste PDF. Tente colar a lista manualmente ou adicionar alunos individualmente.';
      } catch(err){
        state.pdfStatus = 'error';
        state.pdfStatusMsg = 'Erro ao ler o PDF: ' + (err && err.message ? err.message : 'formato não suportado.');
      }
      render();
    });

    const pdfText = document.getElementById('pdf-text');
    if (pdfText) pdfText.addEventListener('input', e => { state.pdfRawText = e.target.value; });

    const btnParsePdf = document.getElementById('btn-parse-pdf');
    if (btnParsePdf) btnParsePdf.addEventListener('click', () => {
      const lines = state.pdfRawText.split('\n');
      const parsed = lines.map(parseStudentLine).filter(Boolean);
      state.pdfPreview = parsed;
      render();
    });

    document.querySelectorAll('[data-prev-nome]').forEach(inp => {
      inp.addEventListener('input', e => {
        const i = parseInt(e.target.getAttribute('data-prev-nome'),10);
        state.pdfPreview[i].nome = e.target.value;
      });
    });
    document.querySelectorAll('[data-prev-matricula]').forEach(inp => {
      inp.addEventListener('input', e => {
        const i = parseInt(e.target.getAttribute('data-prev-matricula'),10);
        state.pdfPreview[i].matricula = e.target.value;
      });
    });
    document.querySelectorAll('[data-prev-remove]').forEach(btn => {
      btn.addEventListener('click', () => {
        const i = parseInt(btn.getAttribute('data-prev-remove'),10);
        state.pdfPreview.splice(i,1);
        render();
      });
    });

    const btnCancelPdf = document.getElementById('btn-cancel-pdf');
    if (btnCancelPdf) btnCancelPdf.addEventListener('click', () => {
      state.pdfStatus = ''; state.pdfStatusMsg = ''; state.pdfRawText = ''; state.pdfPreview = null;
      render();
    });

    const btnConfirmPdf = document.getElementById('btn-confirm-pdf');
    if (btnConfirmPdf) btnConfirmPdf.addEventListener('click', async () => {
      const turma = state.turmas.find(t => t.id === state.activeTurmaId);
      if (!turma || !state.pdfPreview) return;
      let addedCount = 0;
      state.pdfPreview.forEach(row => {
        const nome = (row.nome || '').trim();
        const matricula = (row.matricula || '').trim();
        if (!nome) return;
        const exists = turma.students.some(s =>
          (matricula && s.matricula === matricula) || (!matricula && s.nome.toLowerCase() === nome.toLowerCase())
        );
        if (!exists) { turma.students.push({ nome, matricula }); addedCount++; }
      });
      await saveTurma(turma);
      state.pdfStatus = ''; state.pdfStatusMsg = ''; state.pdfRawText = ''; state.pdfPreview = null;
      if (addedCount > 0) await logAudit('importacao_pdf', `${addedCount} aluno(s) importado(s) via PDF para a turma "${turma.name}".`);
      render();
    });

    // ---- Turma detail: remove enrolled student ----
    document.querySelectorAll('[data-student-remove]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const i = parseInt(btn.getAttribute('data-student-remove'),10);
        const turma = state.turmas.find(t => t.id === state.activeTurmaId);
        if (!turma) return;
        const removed = turma.students[i];
        turma.students.splice(i,1);
        await saveTurma(turma);
        if (removed) await logAudit('aluno_removido', `${removed.nome} removido da turma "${turma.name}".`);
        render();
      });
    });

    // ---- Planejamento docente ----
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

    // ---- Suporte: tabs, inbox, conversation ----
    document.querySelectorAll('[data-suporte-tab]').forEach(t => {
      t.addEventListener('click', async () => {
        state.suporteTab = t.getAttribute('data-suporte-tab');
        await loadSuporteForCurrentTab();
        render();
      });
    });

    document.querySelectorAll('.thread-row[data-thread]').forEach(row => {
      row.addEventListener('click', async () => {
        const name = row.getAttribute('data-thread');
        await selectSuporteThread(name);
      });
    });

    document.querySelectorAll('[data-release-module]').forEach(btn=>{
      btn.addEventListener('click', async()=>{
        const idx=parseInt(btn.getAttribute('data-release-module'),10), it=(state.correcoesPendentes.modulosPendentes||[])[idx];
        if(!it) return;
        const c=correctionState(it.mp); const now=Date.now();
        c.status='corrigido'; c.released=true; c.reviewedAt=now; c.finalGrade=effectiveModuleGrade(it.mp);
        c.history.push({type:'liberacao_pedagogica',ts:now,by:state.user.name,grade:c.finalGrade});
        it.mp.correction=c;
        await saveProgress(it.student);
        await logAudit('modulo_liberado',`${state.user.name} liberou o avanço após o módulo "${it.module.title}" de ${it.student.name}. Nota do Módulo ${fmtGrade(c.finalGrade)}.`);
        await loadCorrecoesPendentes();
        render();
      });
    });

    // ---- Correções pendentes: jump to a turma or a pending support thread ----
    document.querySelectorAll('[data-fix-turma]').forEach(el => {
      el.addEventListener('click', () => {
        state.professorTab = 'turmas';
        state.activeTurmaId = el.getAttribute('data-fix-turma');
        state.view = 'professor';
        render();
      });
    });

    document.querySelectorAll('[data-goto-thread]').forEach(el => {
      el.addEventListener('click', async () => {
        const name = el.getAttribute('data-goto-thread');
        state.view = 'suporte';
        state.suporteTab = 'alunos';
        await selectSuporteThread(name);
      });
    });

    const backSuporteThread = document.getElementById('back-suporte-thread');
    if (backSuporteThread) backSuporteThread.addEventListener('click', () => {
      state.suporteActiveThreadKey = null;
      state.suporteThread = null;
      render();
    });

    const suporteMsg = document.getElementById('suporte-msg');
    if (suporteMsg) suporteMsg.addEventListener('input', e => { state.suporteNewMessage = e.target.value; });

    const btnSendSuporte = document.getElementById('btn-send-suporte');
    if (btnSendSuporte) btnSendSuporte.addEventListener('click', async () => { await sendSuporteMessage(); });

    document.querySelectorAll('[data-approve-module]').forEach(btn=>btn.addEventListener('click',async()=>{
      const idx=parseInt(btn.getAttribute('data-approve-module'),10), it=(state.correcoesPendentes.modulosPendentes||[])[idx]; if(!it)return;
      const gi=document.querySelector(`[data-grade-input="${idx}"]`), fi=document.querySelector(`[data-feedback-input="${idx}"]`); const grade=Math.max(0,Math.min(10,parseFloat((gi&&gi.value)||effectiveModuleGrade(it.mp)||0))); const feedback=(fi&&fi.value||'').trim();
      const c=correctionState(it.mp); c.status='corrigido'; c.reviewedAt=Date.now(); c.feedback=feedback; c.finalGrade=Math.round(grade*10)/10; c.released=true; c.history.push({type:'aprovacao',ts:Date.now(),grade:c.finalGrade,feedback}); it.mp.correction=c; await saveProgress(it.student); await logAudit('modulo_aprovado',`${state.user.name} aprovou o módulo "${it.module.title}" de ${it.student.name} — Nota Final ${fmtGrade(c.finalGrade)}.`); await loadCorrecoesPendentes(); render();
    }));
    document.querySelectorAll('[data-return-module]').forEach(btn=>btn.addEventListener('click',async()=>{
      const idx=parseInt(btn.getAttribute('data-return-module'),10), it=(state.correcoesPendentes.modulosPendentes||[])[idx]; if(!it)return; const fi=document.querySelector(`[data-feedback-input="${idx}"]`); const feedback=(fi&&fi.value||'').trim()||'Revise o módulo e realize novamente as atividades avaliativas indicadas.';
      const c=correctionState(it.mp); c.status='ajustes'; c.reviewedAt=Date.now(); c.feedback=feedback; c.released=false; c.finalGrade=null; c.history.push({type:'devolucao',ts:Date.now(),feedback}); it.mp.exerciseScores=new Array(it.module.exerciseLists.length).fill(null); it.mp.exerciseListsDone=new Array(it.module.exerciseLists.length).fill(false); it.mp.quizScore=null; it.mp.recoveryScore=null; it.mp.correction=c; await saveProgress(it.student); await logAudit('modulo_devolvido',`${state.user.name} devolveu o módulo "${it.module.title}" de ${it.student.name} para ajustes.`); await loadCorrecoesPendentes(); render();
    }));
    document.querySelectorAll('[data-toggle-student-details]').forEach(btn=>btn.addEventListener('click',()=>{const idx=btn.getAttribute('data-toggle-student-details'), row=document.querySelector(`[data-student-detail="${idx}"]`); if(!row)return; const open=row.style.display!=='none'; row.style.display=open?'none':'table-row'; btn.textContent=open?'Ver detalhes':'Ocultar detalhes';}));
    const exportGrades=document.getElementById('btn-export-grades'); if(exportGrades) exportGrades.addEventListener('click',()=>downloadText('notas_contabilidade_avancada.csv',gradesCsv(),'text/csv;charset=utf-8'));
    const printReport=document.getElementById('btn-print-report'); if(printReport) printReport.addEventListener('click',()=>window.print());
    const exportBackup=document.getElementById('btn-export-backup'); if(exportBackup) exportBackup.addEventListener('click',async()=>{await loadPlanningAll(); const names=new Set(); (state.turmas||[]).forEach(t=>(t.students||[]).forEach(a=>names.add((a.nome||'').trim()))); const alunos=(state.roster||[]).filter(r=>names.has((r.name||'').trim())); const payload={plataforma:'Contabilidade Avançada',geradoEm:new Date().toISOString(),professor:state.user.name,turmas:state.turmas,alunos,planejamentos:state.planningRecords}; downloadText(`backup_contabilidade_avancada_${new Date().toISOString().slice(0,10)}.json`,JSON.stringify(payload,null,2),'application/json;charset=utf-8'); logAudit('backup_exportado',`${state.user.name} gerou backup pedagógico incluindo planejamentos.`);});

    const auditAll=document.getElementById('audit-all'); if(auditAll) auditAll.addEventListener('click',()=>{state.accessAuditOnly=false;render();});
    const auditAccess=document.getElementById('audit-access'); if(auditAccess) auditAccess.addEventListener('click',()=>{state.accessAuditOnly=true;render();});
    const printDoc=document.getElementById('btn-print-doc'); if(printDoc) printDoc.addEventListener('click',()=>window.print());
    const printSupport=document.getElementById('btn-print-support'); if(printSupport) printSupport.addEventListener('click',()=>window.print());
    const printSupportList=document.getElementById('btn-print-support-list'); if(printSupportList) printSupportList.addEventListener('click',()=>window.print());
    const saveSupport=document.getElementById('btn-save-support-control'); if(saveSupport) saveSupport.addEventListener('click',async()=>{const t=state.suporteThread;if(!t)return;const old=t.status;const st=document.getElementById('support-status'),due=document.getElementById('support-due'),reo=document.getElementById('support-reopen');t.status=st?st.value:t.status;t.responseDueAt=due&&due.value?new Date(due.value).getTime():null;t.reopenUntil=reo&&reo.value?new Date(reo.value).getTime():null;t.updatedAt=Date.now();if(t.status==='encerrado'&&old!=='encerrado')t.closedAt=Date.now();if(t.status!=='encerrado')t.closedAt=null;t.history.push({type:'status',from:old,to:t.status,ts:Date.now(),by:state.user.name});const kind=state.user.role==='professor'?(state.suporteTab==='alunos'?'aluno-professor':'professor-admin'):suporteInboxKind();await saveThread(kind,t);await logAudit('status_suporte',`${state.user.name} alterou o chamado ${t.protocol||''} para ${supportStatusLabel(t.status)}.`);render();});
    const reopenSupport=document.getElementById('btn-reopen-support'); if(reopenSupport) reopenSupport.addEventListener('click',async()=>{const t=state.suporteThread;if(!t||!canReopenThread(t))return;t.history.push({type:'reabertura',ts:Date.now(),by:state.user.name});t.status='aberto';t.closedAt=null;t.updatedAt=Date.now();const kind=state.user.role==='aluno'?(state.suporteTab==='professor'?'aluno-professor':'aluno-admin'):(state.user.role==='professor'?(state.suporteTab==='alunos'?'aluno-professor':'professor-admin'):suporteInboxKind());await saveThread(kind,t);await logAudit('suporte_reaberto',`${state.user.name} reabriu o chamado ${t.protocol||''}.`);render();});

    // ---- Usuários (painel do Usuário Mestre) ----
    document.querySelectorAll('[data-user-role]').forEach(sel => {
      sel.addEventListener('change', async (e) => {
        const uid = sel.getAttribute('data-user-role');
        const newRole = e.target.value;
        sel.disabled = true;
        try {
          await updateDoc(doc(db, 'users', uid), { role: newRole });
          const u = (state.usuarios || []).find(x => x.id === uid);
          if (u) u.role = newRole;
        } catch(err){
          alert('Não foi possível atualizar esse usuário: ' + (err && err.message ? err.message : 'erro desconhecido'));
        }
        sel.disabled = false;
      });
    });
    document.querySelectorAll('[data-approve-prof]').forEach(btn => btn.addEventListener('click', async()=>{
      const uid=btn.getAttribute('data-approve-prof'); btn.disabled=true;
      try { await updateDoc(doc(db,'users',uid),{role:'professor',status:'approved',approvedAt:Date.now(),approvedBy:state.user.uid}); await logAudit('professor_aprovado',`${state.user.name} aprovou um novo acesso de Professor.`); await loadUsuarios(); render(); }
      catch(err){ alert('Não foi possível aprovar: '+(err&&err.message?err.message:'erro desconhecido')); btn.disabled=false; }
    }));
  }

  // ---- Init ----
  // ---- Firebase Auth drives the whole app lifecycle ----
  onAuthStateChanged(auth, async (fbUser) => {
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
  });
})();

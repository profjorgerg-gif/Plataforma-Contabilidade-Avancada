from pathlib import Path
p=Path('public/app.js')
s=p.read_text(encoding='utf-8')
old='A nota automática do módulo considera 50% da média das 5 listas já ajustadas e 50% do melhor resultado entre Quiz e Recuperação.'
new='A nota automática do módulo considera 50% da média das 5 listas já ajustadas e 50% da nota do Quiz. A Recuperação não compõe a média diretamente; ela apenas substitui notas de listas que sejam inferiores à sua nota.'
if old not in s:
    raise SystemExit('Texto residual não encontrado')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

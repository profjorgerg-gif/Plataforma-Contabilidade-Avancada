from pathlib import Path

p=Path('public/app.js')
s=p.read_text(encoding='utf-8')

old="""    const c=mp.correction; if(!Array.isArray(c.history))c.history=[]; if(c.firstSubmittedAt===undefined)c.firstSubmittedAt=null; if(c.late===undefined)c.late=false; if(c.latePenalty===undefined)c.latePenalty=0; return c;
"""
new="""    const c=mp.correction; if(!Array.isArray(c.history))c.history=[]; if(c.firstSubmittedAt===undefined)c.firstSubmittedAt=null; if(c.late===undefined)c.late=false; if(c.latePenalty===undefined)c.latePenalty=0;
    // Compatibilidade: versões anteriores liberavam o módulo automaticamente.
    // Preservamos liberações humanas legadas (aprovação) e as novas liberações pedagógicas;
    // somente liberações automáticas voltam a aguardar decisão explícita do professor.
    const hasHumanRelease=c.history.some(h=>h&&['aprovacao','liberacao_pedagogica'].includes(h.type));
    const hasAutoRelease=c.history.some(h=>h&&h.type==='conclusao_automatica');
    if(c.released && hasAutoRelease && !hasHumanRelease){ c.released=false; c.status='aguardando_liberacao'; c.reviewedAt=null; }
    return c;
"""
if old not in s:
    raise SystemExit('Bloco correctionState não encontrado para compatibilidade')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')

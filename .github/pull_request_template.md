## O que muda

<!-- Uma frase. Se for refatoração: qual code smell e onde ele estava. -->

## Tipo

- [ ] `feat` — funcionalidade nova
- [ ] `refactor` — muda estrutura, não muda comportamento
- [ ] `fix` / `test` / `docs` / `ci` / `chore`

## Como verificar

```bash
pytest
```

## Checklist de revisão (preenchido por quem REVISA, não por quem escreveu)

- [ ] **Clareza:** nomes seguem o glossário do CP1 (Trecho, Medição, Ordem de Serviço...)?
- [ ] **Duplicação:** alguma regra aparece em mais de um lugar?
- [ ] **Tratamento de erro:** caminhos inválidos falham com erro de negócio claro?
- [ ] **Testes:** os mesmos testes passam antes e depois? Há teste para o caso negativo e de limite?
- [ ] **Fronteiras:** o domínio continua sem importar aplicação, adaptadores ou o outro contexto?
- [ ] **CI verde** neste PR.

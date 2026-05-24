# Diagrama do Fluxo de Proteção

Este diagrama resume o que acontece com os dados em cada técnica do laboratório.

```mermaid
flowchart LR
    A["Tabela original<br/>funcionarios<br/>dados sensiveis em texto plano"]

    A --> B["Mascaramento<br/>vw_funcionarios_mascarados<br/>protege a exibicao"]
    A --> C["Anonimizacao<br/>funcionarios_anonimizados<br/>remove/generaliza identificadores"]
    A --> D["Pseudo-anonimizacao<br/>funcionarios_pseudo<br/>troca identidade por pseudonimo"]
    D --> E["Mapa secreto<br/>mapa_pseudonimos<br/>permite reidentificacao"]
    A --> F["TDE simulado<br/>funcionarios_tde_simulado<br/>campos cifrados em repouso"]
    F --> G["Rotina autorizada Python<br/>descriptografa em runtime"]
```

## Leitura do diagrama

- A tabela `funcionarios` representa o risco inicial: dados sensíveis em texto plano.
- A view `vw_funcionarios_mascarados` mostra dados protegidos sem alterar a tabela original.
- A tabela `funcionarios_anonimizados` remove ou generaliza identificadores.
- A tabela `funcionarios_pseudo` usa pseudonimos; a reversao depende de `mapa_pseudonimos`.
- A tabela `funcionarios_tde_simulado` armazena campos cifrados; a descriptografia autorizada acontece no Python.

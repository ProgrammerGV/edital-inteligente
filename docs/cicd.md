# Integração e publicação contínuas

O GitHub Actions executa os testes em Python 3.12 em pushes e pull requests para `main`. Uma falha bloqueia a aprovação do check. Pull requests não publicam serviços de demonstração.

## Publicação no Render

A configuração prevista é **Settings → Auto-Deploy → After CI Checks Pass**, no serviço Free já existente. O Render aguarda a aprovação dos checks do GitHub Actions antes de publicar a branch `main`. Não é necessário compartilhar deploy hooks ou criar chaves de API.

**Ativação pendente de confirmação no painel.** O workflow de CI não dispara deploy por conta própria. Verifique a configuração antes de considerar o CD ativo.

Após uma publicação, o endpoint de saúde inclui `commit`, obtido de `RENDER_GIT_COMMIT`, permitindo comparar a versão em execução com o commit aprovado. Para reverter, use um commit de reversão no Git e aguarde os testes e a publicação.

## Recursos usados

GitHub Actions em runner Linux padrão do repositório público e serviço Render Free existente. Nenhum serviço adicional, plano pago, cartão, disco pago ou API de IA é necessário. O serviço gratuito pode suspender por inatividade ou pelos limites da hospedagem.

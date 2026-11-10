# Como ativar o agente do Instagram do Tonho

É o mesmo agente da @bolsodesenhado, separado: outro repositório, outro app da Meta e outro token. Assim, um problema em uma conta não afeta a outra. É tudo grátis.

**Nunca cole o token ou a senha em uma conversa.** Eles vão direto nos campos indicados abaixo.

Os nomes dos botões da Meta e do GitHub mudam com o tempo. Se algum estiver diferente, me avise e eu te guio pela tela.

---

## Parte 1: GitHub

Use a mesma conta do GitHub da @bolsodesenhado.

1. No GitHub, toque no **+**, no alto da página, e depois em **New repository**.
2. Em **Repository name**, escreva `tonho-fila`.
3. Marque **Public** e não marque nenhuma outra opção.
4. Toque em **Create repository** e **me avise**. Eu envio os arquivos para lá.

Depois que eu enviar os arquivos:

5. No repositório, abra **Settings** e depois **Pages**.
6. Em **Source**, escolha **Deploy from a branch**. Em **Branch**, escolha **main** e a pasta **/ (root)**. Toque em **Save**.

## Parte 2: Meta (token do Instagram do Tonho)

A conta @deuruimtonho já é profissional e já está no portfólio **Deu ruim, Tonho**.

1. Em **developers.facebook.com**, crie o app `Tonho Fila` com o caso de uso **Gerenciar mensagens e conteúdo no Instagram**.
2. Em **Casos de uso**, **Personalizar**, **API setup with Unified login**, ligue o app ao portfólio **Deu ruim, Tonho**. Não use o portfólio helo_gois.
3. Em **Funções do app**, adicione **deuruimtonho** como **Testador do Instagram**. Depois aceite o convite entrando no Instagram do Tonho, em `instagram.com/accounts/manage_access/`.
4. De volta ao login unificado, no passo 1, toque em **Criar nova configuração** e depois em **Criar do modelo**. O token dessa configuração **nunca expira**.
5. No passo 2, toque em **Gerar token** na linha da **deuruimtonho** e autorize. Se pedir uma Página do Facebook, escolha a **Deu Ruim, Tonho**.

## Parte 3: guardar o token no GitHub

No repositório `tonho-fila`, abra **Settings**, **Secrets and variables**, **Actions** e toque em **New repository secret**.

- **Name:** `IG_TOKEN`. **Secret:** cole o token da Meta. Salve.

Para conferir sem publicar nada: em **Actions**, abra **Conferir token** e toque em **Run workflow**. O registro deve mostrar `token OK em https://graph.facebook.com: conta @deuruimtonho`. Se mostrar outra conta ou um erro, me mande o texto do registro, sem o token.

---

## Como funciona depois de ativado

1. Eu gero o episódio e você aprova o roteiro e as imagens.
2. Depois do vídeo aprovado, eu coloco na fila com a data e o horário: `python agente-tonho/adicionar.py tonho02 2026-11-12T18:00:00-03:00`.
3. O agente confere a fila a cada 15 minutos e publica o Reel com legenda e capa. O post pode sair de 5 a 30 minutos depois do horário marcado.

## O que continua na sua mão

- **Comentário fixado:** a API não fixa comentários.
- **Stories com adesivo** (a partir do Ep 4): enquete, quiz e contagem.
- **TikTok:** sem a auditoria do TikTok, a API só publica em modo privado.
- **Episódios com produto** (Ep 5, 12, 19, 26): a legenda leva o #publi no início, como combinado. Confira o vídeo e a legenda antes de eu colocar na fila.

## Quando algo der errado

O GitHub manda um e-mail avisando. Na fila (`fila.json`), o status mostra o que houve:

| Status | O que significa | O que fazer |
|---|---|---|
| `publicado` | Saiu certo | Nada |
| `conferir` | O Instagram não confirmou | Veja no perfil se saiu. O agente não repete sozinho, para não postar duas vezes |
| `atrasado` | Passou de 6 horas do horário | Escolha outra data |
| `erro` | Falhou 3 vezes | Me mande o e-mail do GitHub |

## Bom saber

- O repositório é **público**: quem tiver o endereço vê os vídeos da fila antes da hora.
- O GitHub desliga agendamentos em repositórios sem nenhum commit por **60 dias**. Se a fila ficar parada esse tempo, reative em **Actions**.
- O token não vence. Ele só para de funcionar se você remover o app **Tonho Fila** ou tirar a @deuruimtonho dele. Nesse caso, gere outro e substitua o `IG_TOKEN`.

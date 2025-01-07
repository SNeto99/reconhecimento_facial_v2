# Configura��o do SDK ZKTeco

Este diret�rio deve conter os arquivos do SDK de reconhecimento facial da ZKTeco.

## Arquivos Necess�rios

1. `libzkfaceid.dll` - Biblioteca principal do SDK
2. Outros arquivos de suporte que acompanham o SDK

## Como Configurar

1. Copie todos os arquivos do SDK ZKTeco para este diret�rio
2. Certifique-se de que a DLL principal (`libzkfaceid.dll`) est� presente
3. Se houver arquivos de depend�ncia adicionais, copie-os tamb�m para este diret�rio

## Estrutura do Diret�rio

```
sdk/
  ??? libzkfaceid.dll
  ??? [outros arquivos do SDK]
  ??? README.md
```

## Observa��es

- O SDK deve ser obtido diretamente da ZKTeco
- Certifique-se de usar a vers�o correta do SDK compat�vel com seu dispositivo
- Mantenha este diret�rio organizado e apenas com os arquivos necess�rios do SDK 
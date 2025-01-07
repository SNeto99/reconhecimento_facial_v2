# Configuração do SDK ZKTeco

Este diretório deve conter os arquivos do SDK de reconhecimento facial da ZKTeco.

## Arquivos Necessários

1. `libzkfaceid.dll` - Biblioteca principal do SDK
2. Outros arquivos de suporte que acompanham o SDK

## Como Configurar

1. Copie todos os arquivos do SDK ZKTeco para este diretório
2. Certifique-se de que a DLL principal (`libzkfaceid.dll`) está presente
3. Se houver arquivos de dependência adicionais, copie-os também para este diretório

## Estrutura do Diretório

```
sdk/
  ??? libzkfaceid.dll
  ??? [outros arquivos do SDK]
  ??? README.md
```

## Observações

- O SDK deve ser obtido diretamente da ZKTeco
- Certifique-se de usar a versão correta do SDK compatível com seu dispositivo
- Mantenha este diretório organizado e apenas com os arquivos necessários do SDK 
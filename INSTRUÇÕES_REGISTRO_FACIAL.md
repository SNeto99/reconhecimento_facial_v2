# Instruções para Registro Facial no Dispositivo ZKTeco

## Visão Geral

Este documento explica como utilizar o novo método de registro facial implementado no sistema. 
A nova implementação corrige problemas anteriores onde o dispositivo abria a tela de cadastro de impressões digitais em vez da câmera para captura facial.

## Problema Anterior

Anteriormente, ao tentar registrar faces no dispositivo ZKTeco, o comando iniciava o registro de impressões digitais em vez de ativar a câmera para captura facial.

## Solução Implementada

Foi implementada uma nova sequência de comandos baseada no SDK oficial em C# da ZKTeco, seguindo exatamente esta ordem:

1. **REG_START**: Inicia o processo de registro
2. **DETECT_FACE_REG**: Ativa a câmera e detecta a face para o registro
3. **ADD_FACE_REG**: Adiciona a face detectada (executado automaticamente pelo dispositivo)
4. **REG_END**: Finaliza o processo de registro

A implementação agora inclui:
- Pausas mais longas entre os comandos para dar tempo ao dispositivo processar
- Métodos alternativos em caso de falha no método principal
- Reconexão automática em caso de perda de conexão
- Verificação após o registro para confirmar que a face foi cadastrada corretamente

## Como Usar

### Método 1: Script Dedicado (Recomendado)

1. Execute o arquivo `registrar_face.bat` com um duplo clique
2. Siga as instruções na tela para:
   - Informar o ID do usuário
   - Criar um novo usuário (se necessário)
   - Posicionar a face na frente da câmera
   - Verificar o reconhecimento após o registro

### Método 2: Demo de Conexão

1. Execute o programa demo_zk_connection.py:
   ```
   python demo_zk_connection.py
   ```

2. No menu principal, selecione a opção **9. Registro Facial Automático (Método Recomendado)**

3. Digite o ID do usuário para o registro facial
   - Se o usuário não existir, será solicitado que você forneça um nome para criar o usuário
   
4. Posicione o rosto na frente da câmera do dispositivo
   - O dispositivo deve mostrar a interface da câmera automaticamente
   - Siga as instruções exibidas na tela do dispositivo para posicionar o rosto corretamente
   
5. Após a captura bem-sucedida, o dispositivo processará e armazenará a face automaticamente

6. Você pode optar por monitorar os eventos do dispositivo durante o processo

## Importante

- Garanta que o usuário esteja posicionado corretamente na frente da câmera
- A iluminação do ambiente deve ser adequada
- Mantenha uma expressão facial neutra durante o registro
- Siga todas as instruções exibidas na tela do dispositivo
- **Se encontrar problemas, tente reiniciar o dispositivo físico antes de tentar novamente**
- Aguarde todo o processo terminar antes de interrompê-lo

## Troubleshooting

Se você encontrar problemas:

1. **Reinicie o dispositivo físico** - Esta é uma das soluções mais eficazes
2. Verifique se o dispositivo está conectado corretamente à rede
3. Confirme se o endereço IP (192.168.50.11) está correto
4. Verifique se o dispositivo tem recursos de reconhecimento facial habilitados
5. Garanta que o dispositivo não esteja bloqueado por outra aplicação
6. Se o registro falhar, verifique no próprio dispositivo se é possível registrar uma face manualmente

## Suporte

Para mais informações ou suporte, entre em contato com a equipe de desenvolvimento. 
# Instru��es para Registro Facial no Dispositivo ZKTeco

## Vis�o Geral

Este documento explica como utilizar o novo m�todo de registro facial implementado no sistema. 
A nova implementa��o corrige problemas anteriores onde o dispositivo abria a tela de cadastro de impress�es digitais em vez da c�mera para captura facial.

## Problema Anterior

Anteriormente, ao tentar registrar faces no dispositivo ZKTeco, o comando iniciava o registro de impress�es digitais em vez de ativar a c�mera para captura facial.

## Solu��o Implementada

Foi implementada uma nova sequ�ncia de comandos baseada no SDK oficial em C# da ZKTeco, seguindo exatamente esta ordem:

1. **REG_START**: Inicia o processo de registro
2. **DETECT_FACE_REG**: Ativa a c�mera e detecta a face para o registro
3. **ADD_FACE_REG**: Adiciona a face detectada (executado automaticamente pelo dispositivo)
4. **REG_END**: Finaliza o processo de registro

A implementa��o agora inclui:
- Pausas mais longas entre os comandos para dar tempo ao dispositivo processar
- M�todos alternativos em caso de falha no m�todo principal
- Reconex�o autom�tica em caso de perda de conex�o
- Verifica��o ap�s o registro para confirmar que a face foi cadastrada corretamente

## Como Usar

### M�todo 1: Script Dedicado (Recomendado)

1. Execute o arquivo `registrar_face.bat` com um duplo clique
2. Siga as instru��es na tela para:
   - Informar o ID do usu�rio
   - Criar um novo usu�rio (se necess�rio)
   - Posicionar a face na frente da c�mera
   - Verificar o reconhecimento ap�s o registro

### M�todo 2: Demo de Conex�o

1. Execute o programa demo_zk_connection.py:
   ```
   python demo_zk_connection.py
   ```

2. No menu principal, selecione a op��o **9. Registro Facial Autom�tico (M�todo Recomendado)**

3. Digite o ID do usu�rio para o registro facial
   - Se o usu�rio n�o existir, ser� solicitado que voc� forne�a um nome para criar o usu�rio
   
4. Posicione o rosto na frente da c�mera do dispositivo
   - O dispositivo deve mostrar a interface da c�mera automaticamente
   - Siga as instru��es exibidas na tela do dispositivo para posicionar o rosto corretamente
   
5. Ap�s a captura bem-sucedida, o dispositivo processar� e armazenar� a face automaticamente

6. Voc� pode optar por monitorar os eventos do dispositivo durante o processo

## Importante

- Garanta que o usu�rio esteja posicionado corretamente na frente da c�mera
- A ilumina��o do ambiente deve ser adequada
- Mantenha uma express�o facial neutra durante o registro
- Siga todas as instru��es exibidas na tela do dispositivo
- **Se encontrar problemas, tente reiniciar o dispositivo f�sico antes de tentar novamente**
- Aguarde todo o processo terminar antes de interromp�-lo

## Troubleshooting

Se voc� encontrar problemas:

1. **Reinicie o dispositivo f�sico** - Esta � uma das solu��es mais eficazes
2. Verifique se o dispositivo est� conectado corretamente � rede
3. Confirme se o endere�o IP (192.168.50.11) est� correto
4. Verifique se o dispositivo tem recursos de reconhecimento facial habilitados
5. Garanta que o dispositivo n�o esteja bloqueado por outra aplica��o
6. Se o registro falhar, verifique no pr�prio dispositivo se � poss�vel registrar uma face manualmente

## Suporte

Para mais informa��es ou suporte, entre em contato com a equipe de desenvolvimento. 
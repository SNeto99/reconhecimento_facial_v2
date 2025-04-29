from database import (
    get_unsynced_devices, mark_device_as_synced,
    get_unsynced_users, mark_user_as_synced,
    get_unsynced_logs, mark_log_as_synced
)
from core.api import enviar_dispositivos_batch, enviar_usuarios_batch, enviar_logs_batch
from datetime import datetime


def sync_all():
    """Sincroniza dispositivos, usuários e logs em batches, via API."""
    # Tamanho do lote (configurável via config 'sync_batch_size')
    try:
        from database import get_config_value
    except ImportError:
        batch_size = 100
    else:
        batch_size = int(get_config_value('sync_batch_size', '100'))

    # 1) Dispositivos em batch
    devices = get_unsynced_devices()
    for i in range(0, len(devices), batch_size):
        batch = devices[i:i+batch_size]
        enviar_dispositivos_batch(batch)
        for d in batch:
            mark_device_as_synced(d['id'])

    # 2) Usuários em batch
    users = get_unsynced_users()
    for i in range(0, len(users), batch_size):
        batch = users[i:i+batch_size]
        enviar_usuarios_batch(batch)
        for u in batch:
            mark_user_as_synced(u['id'])

    # 3) Logs em batch
    logs = get_unsynced_logs()
    for i in range(0, len(logs), batch_size):
        batch = logs[i:i+batch_size]
        enviar_logs_batch(batch)
        for l in batch:
            mark_log_as_synced(l['id'])

def sync_full(device):
    """
    Atualiza localmente dados do dispositivo (info, usuários, logs) e depois envia tudo ao cloud.
    """
    from database import init_db, add_device, save_device_info, synchronize_users, synchronize_logs, set_config_value
    # 1) Garante tabelas e colunas
    init_db()
    # 2) Dispositivo: info e reset synced
    info = device.get_device_info()
    # Armazena o MAC do dispositivo em config para envio nos headers da API
    set_config_value("device_mac", info.get("mac"))
    current_device_id = add_device(info.get('mac'))
    save_device_info(info)
    # 3) Usuários do dispositivo para o DB
    device_users = device.get_users()
    synchronize_users(device_users, current_device_id)
    # 4) Logs do dispositivo para o DB
    device_logs = device.get_attendance_logs()
    # Insere current_device_id em cada log
    for log in device_logs:
        log['device_id'] = current_device_id
    synchronize_logs(device_logs)
    # 5) Envia ao cloud em batches
    sync_all()
    # 6) Grava data/hora da última sincronização
    try:
        from database import set_config_value
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        set_config_value('last_sync', now_str)
    except Exception:
        pass
    
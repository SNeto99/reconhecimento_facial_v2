import sqlite3
import os

DB_FILENAME = "local_data.db"


def get_connection():
    """Retorna uma conexão com o banco de dados."""
    return sqlite3.connect(DB_FILENAME)


def init_db():
    """Inicializa o banco de dados e cria as tabelas necessárias, se não existirem."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Cria a tabela de dispositivos com todos os dados disponíveis da tela inicial
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispositivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT UNIQUE NOT NULL,
            firmware TEXT,
            platform TEXT,
            serial TEXT,
            face_algorithm TEXT,
            device_name TEXT,
            users INTEGER,
            faces INTEGER,
            records INTEGER
        )
    """)
    
    # Cria a tabela de usuários com referência ao dispositivo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_user_id TEXT,
            system_id TEXT,
            name TEXT,
            device_id INTEGER,
            synced INTEGER DEFAULT 0,
            UNIQUE(device_user_id, device_id),
            FOREIGN KEY(device_id) REFERENCES dispositivos(id)
        )
    """)
    
    # Cria a tabela de logs com referência ao dispositivo
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_id TEXT,
        status TEXT,
        device_id INTEGER,
        synced INTEGER DEFAULT 0,
        UNIQUE(timestamp, user_id, status, device_id),
        FOREIGN KEY(device_id) REFERENCES dispositivos(id)
    )''')
    
    # Cria a tabela de eventos para mapear códigos de eventos para nomes
    cursor.execute("""CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo INTEGER UNIQUE NOT NULL,
        nome TEXT
    )""")
    
    # Cria a tabela de configurações
    cursor.execute("""CREATE TABLE IF NOT EXISTS config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT
    )""")
    
    # Insere o evento 15 com o nome padrão 'Validação Facial', se não existir
    cursor.execute("INSERT OR IGNORE INTO eventos (codigo, nome) VALUES (?, ?)", (15, "Validação Facial"))
    
    conn.commit()
    conn.close()


def insert_or_update_user(device_user_id, system_id, name, device_id):
    """
    Insere um novo usuário ou atualiza o existente com referência ao dispositivo.
    Sempre marca o registro como não sincronizado (synced = 0).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE device_user_id = ? AND device_id = ?", (device_user_id, device_id))
    result = cursor.fetchone()
    if result:
        cursor.execute("""
            UPDATE usuarios
            SET system_id = ?, name = ?, synced = 0
            WHERE device_user_id = ? AND device_id = ?
        """, (system_id, name, device_user_id, device_id))
    else:
        cursor.execute("""
            INSERT INTO usuarios (device_user_id, system_id, name, device_id, synced)
            VALUES (?, ?, ?, ?, 0)
        """, (device_user_id, system_id, name, device_id))
    conn.commit()
    conn.close()


def mark_user_as_synced(device_user_id):
    """Marca o registro de um usuário como sincronizado."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET synced = 1
        WHERE device_user_id = ?
    """, (device_user_id,))
    conn.commit()
    conn.close()


def get_unsynced_users():
    """Retorna a lista de usuários que ainda não foram sincronizados com a API."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE synced = 0")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_users():
    """Retorna todos os registros de usuários."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    rows = cursor.fetchall()
    conn.close()
    return rows


def insert_logs(logs):
    conn = get_connection()
    cursor = conn.cursor()
    for log in logs:
        try:
            cursor.execute("INSERT OR IGNORE INTO logs (timestamp, user_id, status, device_id, synced) VALUES (?, ?, ?, ?, 0)",
                           (log['timestamp'], log['user_id'], log['status'], log['device_id']))
        except Exception as e:
            print(f"Erro ao inserir log: {e}")
    conn.commit()
    conn.close()


def get_all_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, user_id, status FROM logs")
    rows = cursor.fetchall()
    conn.close()
    logs = [{'timestamp': row[0], 'user_id': row[1], 'status': row[2]} for row in rows]
    return logs


def synchronize_logs(device_logs):
    """Sincroniza os logs do dispositivo com os logs armazenados localmente, considerando o dispositivo.
    Mantém apenas os registros que estão presentes tanto no dispositivo quanto no banco de dados.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Obter logs locais com id para referência, incluindo device_id
    cursor.execute("SELECT id, timestamp, user_id, status, device_id, synced FROM logs")
    rows = cursor.fetchall()
    # Cria um dicionário com chave (timestamp, user_id, status, device_id) e valor id
    local_logs = { (row[1], row[2], row[3], row[4]): row[0] for row in rows }

    # Cria um conjunto com as chaves dos logs do dispositivo
    device_keys = set()
    for log in device_logs:
        key = (log['timestamp'], log['user_id'], log['status'], log['device_id'])
        device_keys.add(key)

    # Deleta registros locais que não estão presentes no dispositivo
    for key, log_id in local_logs.items():
        if key not in device_keys:
            cursor.execute("DELETE FROM logs WHERE id = ?", (log_id,))

    # Insere registros do dispositivo que não existem no banco
    for key in device_keys:
        if key not in local_logs:
            cursor.execute("INSERT OR IGNORE INTO logs (timestamp, user_id, status, device_id, synced) VALUES (?, ?, ?, ?, 0)", key)

    conn.commit()
    conn.close()
    
    return get_all_logs()


def synchronize_users(device_users, current_device_id):
    """Sincroniza os usuários do dispositivo com os armazenados localmente, considerando o dispositivo.
    Remove os usuários que não estão mais presentes no dispositivo e insere/atualiza os que estão presentes.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, device_user_id, device_id FROM usuarios")
    rows = cursor.fetchall()
    # Cria um dicionário com chave (device_user_id, device_id)
    local_users = { (row[1], row[2]): row[0] for row in rows }

    # Usa current_device_id para associar todos os usuários vindos do dispositivo
    device_keys = set((str(u['user_id']), current_device_id) for u in device_users)

    # Remove usuários que estão no banco para esse device_id e que não estão mais presentes no dispositivo
    for key, user_id in local_users.items():
        if key[1] == current_device_id and key not in device_keys:
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))

    conn.commit()
    conn.close()

    # Insere ou atualiza os usuários presentes no dispositivo usando o current_device_id
    for user in device_users:
        insert_or_update_user(str(user['user_id']), user.get('system_id', ''), user['name'], current_device_id)

    return get_all_users()


def add_device(mac_address):
    """Adiciona um dispositivo com base no mac_address ou retorna o id se já existir."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO dispositivos (mac_address) VALUES (?)", (mac_address,))
        device_id = cursor.lastrowid
    except Exception as e:
        cursor.execute("SELECT id FROM dispositivos WHERE mac_address = ?", (mac_address,))
        result = cursor.fetchone()
        device_id = result[0] if result else None
    conn.commit()
    conn.close()
    return device_id


def get_devices():
    """Retorna a lista de dispositivos cadastrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, mac_address FROM dispositivos")
    rows = cursor.fetchall()
    conn.close()
    devices = [{'id': row[0], 'mac_address': row[1]} for row in rows]
    return devices


def save_device_info(info):
    """
    Salva ou atualiza as informações do dispositivo na tabela dispositivos.
    info: dicionário com as chaves: mac, firmware, platform, serial, face_algorithm, device_name, users, faces, records.
    Retorna o id do dispositivo.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM dispositivos WHERE mac_address = ?", (info.get("mac"),))
    row = cursor.fetchone()
    if row:
        device_id = row[0]
        cursor.execute("""
            UPDATE dispositivos SET
                firmware = ?,
                platform = ?,
                serial = ?,
                face_algorithm = ?,
                device_name = ?,
                users = ?,
                faces = ?,
                records = ?
            WHERE mac_address = ?
        """, (
            info.get("firmware"), info.get("platform"), info.get("serial"),
            info.get("face_algorithm"), info.get("device_name"),
            info.get("users"), info.get("faces"), info.get("records"),
            info.get("mac")
        ))
    else:
        cursor.execute("""
            INSERT INTO dispositivos (mac_address, firmware, platform, serial, face_algorithm, device_name, users, faces, records)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            info.get("mac"), info.get("firmware"), info.get("platform"), info.get("serial"),
            info.get("face_algorithm"), info.get("device_name"), info.get("users"),
            info.get("faces"), info.get("records")
        ))
        device_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return device_id


def get_event_map():
    """Retorna um dicionário mapeando códigos de eventos para seus nomes na tabela eventos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nome FROM eventos")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


def get_config_value(key, default_value=""):
    """Retorna o valor da configuração a partir da tabela config."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return default_value


def set_config_value(key, value):
    """Insere ou atualiza o valor da configuração na tabela config."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso.") 
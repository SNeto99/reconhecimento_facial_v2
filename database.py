import sqlite3
import os
import datetime

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
            records INTEGER,
            synced INTEGER DEFAULT 0
        )
    """)
    
    # Cria a tabela de usuários com referência ao dispositivo e campos adicionais
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_user_id TEXT,
            system_id TEXT UNIQUE,
            name TEXT,
            api_name TEXT,
            ra TEXT UNIQUE,
            serie TEXT,
            turma TEXT,
            device_id INTEGER,
            synced INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
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
    
    # Cria a tabela de logs de API para auditoria
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            method TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            request TEXT,
            response TEXT,
            status_code INTEGER,
            duration_ms INTEGER,
            error_msg TEXT
        )
    """)
    
    # Insere o evento 15 com o nome padrão 'Validação Facial', se não existir
    cursor.execute("INSERT OR IGNORE INTO eventos (codigo, nome) VALUES (?, ?)", (15, "Validação Facial"))
    
    # Adiciona coluna 'active' à tabela de usuários, ignorando se já existe
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN active INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass
    
    # Adiciona coluna 'synced' à tabela de dispositivos, ignorando se já exista
    try:
        cursor.execute("ALTER TABLE dispositivos ADD COLUMN synced INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()


def insert_or_update_user(device_user_id, system_id, alias_name, api_name, ra, serie, turma, device_id):
    """
    Insere um novo usuário ou atualiza o existente com referência ao dispositivo.
    Sempre marca o registro como não sincronizado (synced = 0).
    Aproveita as restrições UNIQUE do banco de dados para evitar duplicações.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Primeiro verifica se existe pelo device_user_id e device_id
    cursor.execute("SELECT id FROM usuarios WHERE device_user_id = ? AND device_id = ?", (device_user_id, device_id))
    result = cursor.fetchone()
    
    if result:
        # Atualiza o usuário existente
        cursor.execute("""
            UPDATE usuarios
            SET system_id = ?, name = ?, api_name = ?, ra = ?, serie = ?, turma = ?, synced = 0, active = 1
            WHERE device_user_id = ? AND device_id = ?
        """, (system_id, alias_name, api_name, ra, serie, turma, device_user_id, device_id))
    else:
        # Tenta inserir o novo usuário
        try:
            cursor.execute("""
                INSERT INTO usuarios (device_user_id, system_id, name, api_name, ra, serie, turma, device_id, synced, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 1)
            """, (device_user_id, system_id, alias_name, api_name, ra, serie, turma, device_id))
        except sqlite3.IntegrityError:
            # Se ocorrer erro de integridade (RA ou system_id duplicado), tenta atualizar o registro existente
            if ra and ra.strip():
                cursor.execute("""
                    UPDATE usuarios
                    SET device_user_id = ?, name = ?, api_name = ?, serie = ?, turma = ?, device_id = ?, synced = 0, active = 1
                    WHERE ra = ?
                """, (device_user_id, alias_name, api_name, serie, turma, device_id, ra))
            elif system_id and system_id.strip():
                cursor.execute("""
                    UPDATE usuarios
                    SET device_user_id = ?, name = ?, api_name = ?, ra = ?, serie = ?, turma = ?, device_id = ?, synced = 0, active = 1
                    WHERE system_id = ?
                """, (device_user_id, alias_name, api_name, ra, serie, turma, device_id, system_id))
    
    conn.commit()
    conn.close()


def mark_user_as_synced(user_record_id):
    """Marca o registro de um usuário como sincronizado, usando o ID da linha."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET synced = 1 WHERE id = ?",
        (user_record_id,)
    )
    conn.commit()
    conn.close()


def get_unsynced_users():
    """Retorna lista de usuários não sincronizados (synced = 0)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, device_user_id, system_id, name, api_name, ra, serie, turma, device_id"
        " FROM usuarios WHERE synced = 0"
    )
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def get_all_users(active_only=True):
    """Retorna todos os registros de usuários."""
    conn = get_connection()
    cursor = conn.cursor()
    if active_only:
        cursor.execute("SELECT * FROM usuarios WHERE active = 1")
    else:
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
    """Insere apenas logs novos (timestamp maior) do dispositivo, preservando o campo 'synced'."""
    conn = get_connection()
    cursor = conn.cursor()
    # Descobre o último timestamp salvo para este device_id
    last_ts = None
    if device_logs:
        device_id = device_logs[0]['device_id']
        cursor.execute("SELECT MAX(timestamp) FROM logs WHERE device_id = ?", (device_id,))
        last_ts = cursor.fetchone()[0]
    # Converte last_ts para datetime, se existir
    last_ts_dt = None
    if isinstance(last_ts, str):
        try:
            last_ts_dt = datetime.datetime.strptime(last_ts, "%Y-%m-%d %H:%M:%S")
        except:
            last_ts_dt = None
    # Insere apenas os logs com timestamp > last_ts_dt
    for log in device_logs:
        ts = log.get('timestamp')
        # Converte ts para datetime
        ts_dt = None
        if isinstance(ts, str):
            try:
                ts_dt = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except:
                continue
        elif isinstance(ts, datetime.datetime):
            ts_dt = ts
        else:
            continue
        # Verifica se é novo
        if last_ts_dt is None or ts_dt > last_ts_dt:
            ts_str = ts_dt.strftime("%Y-%m-%d %H:%M:%S")
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO logs (timestamp, user_id, status, device_id, synced) VALUES (?, ?, ?, ?, 0)",
                    (ts_str, log['user_id'], log['status'], log['device_id'])
                )
            except Exception as e:
                print(f"Erro ao sincronizar log: {e}")
    conn.commit()
    conn.close()
    # Retorna todos os logs para exibição, sem alterar synced
    return get_all_logs()


def synchronize_users(device_users, current_device_id):
    """Sincroniza os usuários do dispositivo com os armazenados localmente, considerando o dispositivo.
    Remove os usuários que não estão mais presentes no dispositivo e insere/atualiza os que estão presentes.
    Aproveita as restrições UNIQUE do banco de dados para evitar duplicações.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Obter todos os usuários para o dispositivo atual
    cursor.execute("SELECT id, device_user_id FROM usuarios WHERE device_id = ?", (current_device_id,))
    rows = cursor.fetchall()
    
    # Cria um conjunto com os device_user_ids existentes no dispositivo
    local_user_ids = {row[1] for row in rows}
    
    # Cria um conjunto com os device_user_ids vindos do dispositivo
    device_user_ids = {str(u['user_id']) for u in device_users}
    
    # Marca como inativo usuários que não estão mais presentes no dispositivo
    for user_id in local_user_ids:
        if user_id not in device_user_ids:
            cursor.execute("UPDATE usuarios SET active = 0 WHERE device_user_id = ? AND device_id = ?", 
                          (user_id, current_device_id))

    conn.commit()
    conn.close()

    # Insere ou reativa usuários presentes no dispositivo
    for user in device_users:
        device_user_id = str(user['user_id'])
        
        # Verifica se o usuário já existe localmente com o mesmo device_user_id
        if device_user_id in local_user_ids:
            # Reativa usuário previamente inativo
            conn2 = get_connection()
            cursor2 = conn2.cursor()
            cursor2.execute(
                "UPDATE usuarios SET active = 1 WHERE device_user_id = ? AND device_id = ?",
                (device_user_id, current_device_id)
            )
            conn2.commit()
            conn2.close()
        else:
            # Tenta inserir o usuário - a função insert_or_update_user já trata duplicidades por RA ou system_id
            insert_or_update_user(
                device_user_id,
                user.get('system_id', ''),
                user['name'],
                user.get('api_name', ''),
                user.get('ra', ''),
                user.get('serie', ''),
                user.get('turma', ''),
                current_device_id
            )

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
                records = ?,
                synced = 0
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


def get_user_info(device_user_id, device_id, ra=None, system_id=None):
    """
    Retorna um dicionário com todos os dados do usuário para o device_id indicado.
    Permite buscar o usuário pelo device_user_id, RA ou system_id.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    row = None
    
    # Primeiro tenta buscar pelo device_user_id
    if device_user_id:
        cursor.execute(
            "SELECT device_user_id, system_id, name, api_name, ra, serie, turma "
            "FROM usuarios WHERE device_user_id = ? AND device_id = ? AND active = 1",
            (str(device_user_id), device_id)
        )
        row = cursor.fetchone()
    
    # Se não encontrou e temos um RA, busca pelo RA
    if not row and ra and ra.strip():
        cursor.execute(
            "SELECT device_user_id, system_id, name, api_name, ra, serie, turma "
            "FROM usuarios WHERE ra = ? AND active = 1 LIMIT 1",
            (ra,)
        )
        row = cursor.fetchone()
    
    # Se ainda não encontrou e temos um system_id, busca pelo system_id
    if not row and system_id and system_id.strip():
        cursor.execute(
            "SELECT device_user_id, system_id, name, api_name, ra, serie, turma "
            "FROM usuarios WHERE system_id = ? AND active = 1 LIMIT 1",
            (system_id,)
        )
        row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            'user_id': row[0],
            'system_id': row[1],
            'name': row[2],
            'api_name': row[3],
            'ra': row[4],
            'serie': row[5],
            'turma': row[6]
        }
    return None


def get_logs_by_user(device_user_id, device_id):
    """Retorna lista de logs (timestamp e status) para o usuário e dispositivo indicados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, status FROM logs "
        "WHERE user_id = ? AND device_id = ? "
        "ORDER BY timestamp",
        (str(device_user_id), device_id)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{'timestamp': row[0], 'status': row[1]} for row in rows]


def get_unsynced_devices():
    """Retorna lista de dispositivos não sincronizados (synced = 0)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, mac_address, firmware, platform, serial, face_algorithm, device_name, users, faces, records FROM dispositivos WHERE synced = 0"
    )
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def mark_device_as_synced(device_id):
    """Marca um dispositivo como sincronizado (synced = 1)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE dispositivos SET synced = 1 WHERE id = ?", (device_id,))
    conn.commit()
    conn.close()


def get_unsynced_logs():
    """Retorna lista de logs não sincronizados (synced = 0)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, timestamp, user_id, status, device_id FROM logs WHERE synced = 0"
    )
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]


def mark_log_as_synced(log_id):
    """Marca um log como sincronizado (synced = 1)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE logs SET synced = 1 WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()


# Função para registrar chamadas à API
def log_api_call(timestamp, method, endpoint, request, status_code, duration_ms, error_msg=None):
    """Insere um registro na tabela api_logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO api_logs (timestamp, method, endpoint, request, response, status_code, duration_ms, error_msg) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (timestamp, method, endpoint, request, None, status_code, duration_ms, error_msg)
    )
    conn.commit()
    conn.close()


# Função para limpar logs antigos
def cleanup_api_logs(retention_days):
    """Remove registros de api_logs com mais de retention_days de idade."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM api_logs WHERE timestamp < datetime('now', ?)",
        (f'-{retention_days} days',)
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso.") 
# Ejemplo de Configuración para Gemini CLI

Este documento muestra cómo usar sync-mcp-cfg con Gemini CLI.

## Configuración Automática

El tool detecta automáticamente Gemini CLI si está instalado en el sistema y busca la configuración en:

```bash
# Global (usuario)
~/.gemini/settings.json

# Local (proyecto)
.gemini/settings.json
```

## Formato de Configuración

Gemini CLI utiliza un formato JSON específico en `settings.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/files"
      ],
      "env": {},
      "trust": true,
      "cwd": "./file-server",
      "timeout": 30000
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "$BRAVE_API_KEY"
      },
      "trust": true,
      "timeout": 15000
    },
    "postgres": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network",
        "host",
        "mcp/postgres",
        "postgresql://user:password@localhost/dbname"
      ],
      "env": {
        "DATABASE_URL": "$DB_CONNECTION"
      },
      "trust": false,
      "timeout": 60000
    },
    "http-server": {
      "httpUrl": "http://localhost:3000/mcp",
      "timeout": 5000,
      "trust": false
    }
  },
  "theme": "GitHub",
  "sandbox": false
}
```

## Uso con sync-mcp-cfg

### Listar servidores disponibles

```bash
sync-mcp-cfg list --client gemini-cli
```

### Sincronizar desde Claude Desktop a Gemini CLI (Completo)

```bash
# Sincronizar todos los servidores con backup automático
sync-mcp-cfg sync --from claude-desktop --to gemini-cli --backup

# Vista previa sin realizar cambios
sync-mcp-cfg sync --from claude-desktop --to gemini-cli --dry-run
```

### Sincronizar servidores específicos

```bash
# Sincronizar solo servidores específicos
sync-mcp-cfg sync --from claude-desktop --to gemini-cli --servers filesystem --servers brave-search

# Sobrescribir sin confirmación
sync-mcp-cfg sync --from claude-desktop --to gemini-cli --overwrite
```

### Sincronizar desde Gemini CLI a Claude Desktop

```bash
# Sincronizar en dirección contraria
sync-mcp-cfg sync --from gemini-cli --to claude-desktop --backup
```

### Agregar un servidor específicamente a Gemini CLI

```bash
sync-mcp-cfg add gemini-cli \
  --name "python-tools" \
  --command "python" \
  --args "-m" "mcp_server_python" \
  --env "PYTHON_PATH=/usr/local/bin/python3" \
  --description "Python code execution tools"
```

## Características Específicas de Gemini CLI

- **Campo `trust`**: Controla si el servidor requiere confirmación del usuario antes de ejecutar herramientas
- **Campo `cwd`**: Directorio de trabajo para servidores stdio
- **Campo `timeout`**: Tiempo límite en milisegundos para requests (default: 600,000ms = 10 min)
- **Campo `httpUrl`**: URL específica para servidores HTTP (diferente de `url` para SSE)
- **Configuración integrada**: Forma parte del archivo `settings.json` general de Gemini CLI
- **Validación**: Valida la configuración antes de guardar cambios

## Instalación de Gemini CLI

Si no tienes Gemini CLI instalado, puedes instalarlo con:

```bash
# Via npm (recomendado)
npm install -g @google-labs/gemini-cli

# O usando el comando directo
npm install -g gemini-cli
```

## Notas Importantes

1. Gemini CLI usa `.gemini/settings.json` (local) o `~/.gemini/settings.json` (global)
2. El comando para verificar disponibilidad es `gemini` (no `gemini-cli`)
3. Siempre se crea un backup automático antes de modificar la configuración
4. Los servidores HTTP requieren usar `httpUrl` en lugar de `url`
5. El campo `trust` controla la confirmación automática de herramientas

## Solución de Problemas

### Gemini CLI no detectado

Si el tool no detecta Gemini CLI automáticamente:

1. Verifica que `gemini` esté en tu PATH: `which gemini`
2. Asegúrate de que el directorio de configuración exista: `~/.gemini/`
3. Crea manualmente el archivo de configuración inicial si es necesario

### Errores de permisos

Si tienes problemas de permisos:

```bash
chmod 755 ~/.gemini/
chmod 644 ~/.gemini/settings.json
```

### Configuración corrupta

Si la configuración se corrompe, puedes restaurar desde un backup:

```bash
sync-mcp-cfg restore gemini-cli --backup ~/.gemini/backups/settings_20240630_120000.json
```

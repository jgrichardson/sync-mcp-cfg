# 🔒 Guía de Seguridad - sync-mcp-cfg

## ⚠️ IMPORTANTE: Datos Sensibles

Este proyecto **NO incluye** credenciales, API keys, ni datos personales en el repositorio público. Sin embargo, el tool trabaja con archivos de configuración locales que **SÍ contienen datos sensibles**.

## 🚫 Archivos que NUNCA deben subirse a GitHub

### Configuraciones personales:

- `~/.gemini/settings.json`
- `~/Library/Application Support/Claude/claude_desktop_config.json`
- `~/Library/Application Support/Code/User/settings.json`
- `~/.claude.json`
- `~/.cursor/mcp.json`

### Datos sensibles comunes en estos archivos:

- ✅ **API Keys**: Brave Search, Cloudflare, OpenAI, etc.
- ✅ **Credenciales**: Usernames, passwords, tokens
- ✅ **IPs privadas**: Direcciones de red local
- ✅ **Zone IDs**: Identificadores de servicios cloud
- ✅ **Rutas personales**: Directorios específicos del usuario

## 🛡️ Medidas de Protección Implementadas

### 1. .gitignore robusto

```gitignore
# Personal configurations (NEVER commit these)
**/settings.json
**/*_config.json
**/claude_desktop_config.json
**/.claude.json
**/.cursor/
**/.gemini/
**/Library/Application Support/Code/User/settings.json

# API Keys and sensitive data
*.key
*.pem
*.env.local
*.env.production
config/personal/
secrets/
credentials/
```

### 2. Ejemplos sanitizados

- Todos los ejemplos usan datos ficticios
- Rutas genéricas como `/Users/user/Documents`
- API keys con formato `$VARIABLE_NAME`

### 3. Código sin hardcoded values

- Uso de `Path.home()` en lugar de rutas específicas
- Variables de entorno para configuraciones
- Detección automática de sistemas

## 🧪 Antes de Hacer Commit

### Verificar que no hay datos sensibles:

```bash
# Buscar posibles datos personales
grep -r "gilberth" . --exclude-dir=.git
grep -r "/Users/gilberth" . --exclude-dir=.git
grep -r "impresora" . --exclude-dir=.git
grep -r "10.10.10" . --exclude-dir=.git

# Verificar archivos ignorados
git status --ignored

# Ver cambios antes del commit
git diff --cached
```

## 📋 Checklist de Seguridad

Antes de hacer `git push`:

- [ ] ✅ No hay API keys reales en el código
- [ ] ✅ No hay contraseñas en texto plano
- [ ] ✅ No hay rutas personales hardcoded
- [ ] ✅ No hay IPs privadas expuestas
- [ ] ✅ Los ejemplos usan datos ficticios
- [ ] ✅ .gitignore está actualizado
- [ ] ✅ `git status --ignored` muestra archivos sensibles ignorados

## 🆘 Si accidentalmente subes datos sensibles

1. **No hacer push adicionales**
2. **Cambiar las credenciales comprometidas inmediatamente**
3. **Limpiar el historial de git:**

   ```bash
   # Remover archivo específico del historial
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch ARCHIVO_SENSIBLE' \
     --prune-empty --tag-name-filter cat -- --all

   # Forzar push para sobrescribir el historial remoto
   git push origin --force --all
   ```

## 📚 Recursos Adicionales

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [GitGuardian: Git security best practices](https://blog.gitguardian.com/secrets-api-management/)
- [OWASP: Secrets Management](https://owasp.org/www-community/vulnerabilities/Insufficient_Cryptography)

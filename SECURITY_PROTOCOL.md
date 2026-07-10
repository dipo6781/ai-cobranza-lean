# 🛡️ PROTOCOLO DE SEGURIDAD - AI COBRANZA LEAN

**Versión:** 1.0  
**Fecha de creación:** 2026-07-09  
**Última actualización:** 2026-07-09  
**Responsable:** Equipo de Desarrollo  
**Estado:** ✅ ACTIVO

---

## 1. PRINCIPIOS FUNDAMENTALES

### 1.1 Seguridad First
- Toda decisión debe pasar primero el filtro de seguridad
- Si compromete seguridad, se rechaza automáticamente

### 1.2 Zero Trust Architecture
- Asumir que todo puede ser comprometido
- Verificar siempre, nunca confiar por defecto

### 1.3 Principio de Mínimo Privilegio
- Cada componente solo tendrá permisos estrictamente necesarios

### 1.4 Defense in Depth
- Múltiples capas de seguridad

---

## 2. GESTIÓN DE CREDENCIALES

### ❌ NUNCA HACER:
- Hardcodear claves en el código
- Subir .env a Git
- Compartir claves sin encriptar

### ✅ SIEMPRE HACER:
- Usar variables de entorno
- Rotar claves cada 90 días
- Documentar qué servicios usan cada clave

---

## 3. CONTROL DE ACCESO AL CÓDIGO

### Rama main (Producción):
- Requiere Pull Request
- Requiere 1 aprobación
- No permite force push
- No permite borrado

---

## 4. PROTECCIÓN DE DATOS

### Pseudonimización (Ley 1266):
- Nunca almacenar IDs reales en logs
- Usar hashes irreversibles
- Separar datos personales de datos de negocio

---

## 5. CHECKLISTS

### Pre-Deploy:
- [ ] No hay claves hardcodeadas
- [ ] .env está en .gitignore
- [ ] Variables configuradas en Vercel
- [ ] Tests pasan
- [ ] Code review aprobado

---

## 6. CUMPLIMIENTO LEGAL (COLOMBIA)

### Ley 1581 de 2012:
- Registro en RNBD (SIC)
- Política de tratamiento publicada
- Aviso de privacidad
- Consentimiento informado

### Ley 1266 de 2008:
- Consentimiento EXPLICITO
- Información clara sobre uso
- Derecho a conocer información

---

**Documento creado:** 2026-07-09  
**Próxima revisión:** 2026-10-09
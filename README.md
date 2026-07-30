# Bot Uniformes

Bot de Discord que, mediante un asistente por preguntas en un canal, genera y publica
un embed de uniforme (con el mismo formato de la imagen) en otro canal.

- **Canal de entrada** (donde el bot pregunta): `1530593580878663700`
- **Canal de salida** (donde el bot publica): `1457178591728242698`
- **Servidor**: `1297154053675159552`

Para cambiar estos canales, edita las constantes al principio de `bot.py`.

---

## 1. Crear la aplicación / bot

1. Entra en <https://discord.com/developers/applications> → **New Application**.
2. Ponle el nombre **`Ordenador`** (es el nombre que saldrá arriba del mensaje).
3. Menú lateral **Bot** → **Reset Token** → copia el token (no lo compartas con nadie).
4. En la misma página **Bot**, activa **Privileged Gateway Intents → MESSAGE CONTENT INTENT** ✅.

## 2. Invitar el bot al servidor

En **OAuth2 → URL Generator**:
- Scopes: `bot`
- Bot Permissions: `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`

Copia la URL generada, ábrela y añade el bot a tu servidor.
Asegúrate de que el bot **puede ver y escribir** en los dos canales (entrada y salida).

## 3. Configurar el token

1. Copia `.env.example` a `.env`.
2. Pega tu token:  `DISCORD_TOKEN=tu_token_aqui`

## 4. Instalar y ejecutar

```bash
pip install -r requirements.txt
python bot.py
```

Cuando veas `✅ Conectado como Ordenador CNP...` ya está funcionando.

---

## Cómo usarlo

En el **canal de entrada** escribe:

```
!uniforme
```

El bot te irá preguntando, uno por uno:

1. Título
2. Descripción
3–12. Cada prenda (Máscara, Bufandas y Cadenas, Chaquetas, Camisetas, Chalecos,
   Bolsas y Paracaídas, Brazos, Piernas, Zapatos, Calcomanías) → responde `actual/máximo`, ej: `0/367`
13. Código
14. Adjunta la **imagen** del uniforme

Al terminar, el bot publica el embed en el canal de salida.
Escribe `cancelar` en cualquier momento para abortar.

> El nombre **"Ordenador"** y la etiqueta **APP** que salen arriba del mensaje
> son el nombre de la propia cuenta del bot (paso 1.2), no se ponen desde el código.

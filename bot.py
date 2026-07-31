import os
import re
import asyncio
import datetime
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord
from discord.ext import commands
from dotenv import load_dotenv

# --------------------------------------------------------------------------
# Configuracion
# --------------------------------------------------------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1297154053675159552
INPUT_CHANNEL_ID = 1530593580878663700    # canal donde el bot pregunta
OUTPUT_CHANNEL_ID = 1457178591728242698   # canal donde el bot publica

EMBED_COLOR = 0x2F7FE0                     # barra azul del embed
AUTHOR_NAME = "Ordenador"
FOOTER_TEXT = "Uniformes Oficiales"

# --------------------------------------------------------------------------
# Configuracion del comando !armas  (tienda Amazon)
# --------------------------------------------------------------------------
# El comando !armas publica en el MISMO canal donde se escribe.
# (Referencia del server Amazon: guild 1532487997352837160,
#  canal de armas 1532495873781665932.)
ARMAS_AUTHOR = "Encargados | • | Amazon"   # linea de arriba del embed
ARMAS_FOOTER_AUTHOR = "Itachi"             # "Creado por Itachi"
ARMAS_COLOR = 0xED1C24                      # rojo (barra lateral)

# Listas de precios (nombre, precio).  Editables sin tocar la logica.
ARMAS_BLANCAS = [
    ("Cuchillo Nerf", "9k"),
    ("Palanca Nerf", "9k"),
    ("Palo De Nerf", "9k"),
    ("Puño Americano Nerf", "9k"),
    ("Machete", "9k"),
    ("Hacha Nerf", "12k"),
    ("Hacha de batalla Nerf", "12k"),
    ("Daga Nerf", "12k"),
    ("Bate Nerf", "12k"),
    ("Navaja Nerf", "12k"),
]

SEMI_AUTOMATICAS = [
    ("Nerf Vintage", "26K"),
    ("Nerf SNS", "28K"),
    ("Nerf XM3 ( HK )", "38K"),
    ("Nerf 9mm", "68K"),
    ("Nerf Cerámica", "74K"),
    ("Pistola Nerf .50", "148K"),
    ("Revolver Nerf", "255K"),
]

# Orden EXACTO en el que aparecen en la imagen (3 por fila)
COMPONENTS = [
    ("🎭", "Máscara"),
    ("💎", "Bufandas y Cadenas"),
    ("🧥", "Chaquetas"),
    ("👕", "Camisetas"),
    ("🦺", "Chalecos"),
    ("🎒", "Bolsas y Paracaídas"),
    ("💪", "Brazos"),
    ("👖", "Piernas"),
    ("👟", "Zapatos"),
    ("🏷️", "Calcomanías"),
]

# --------------------------------------------------------------------------
# Bot
# --------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True  # necesario para leer las respuestas del wizard
bot = commands.Bot(command_prefix="!", intents=intents)


def parse_valor(texto: str) -> str:
    """Convierte '0/367', '0 367', '0-367'... en '0 / 367'."""
    nums = re.findall(r"\d+", texto)
    if len(nums) >= 2:
        return f"{nums[0]} / {nums[1]}"
    if len(nums) == 1:
        return nums[0]
    return texto.strip()


@bot.event
async def on_ready():
    print(f"✅ Conectado como {bot.user} (id={bot.user.id})")
    print(f"   Canal de entrada:  {INPUT_CHANNEL_ID}")
    print(f"   Canal de salida:   {OUTPUT_CHANNEL_ID}")


@bot.command(name="uniforme")
async def uniforme(ctx: commands.Context):
    """Inicia el asistente para crear una publicacion de uniforme."""
    if ctx.channel.id != INPUT_CHANNEL_ID:
        await ctx.reply(f"⚠️ Usa este comando en <#{INPUT_CHANNEL_ID}>.")
        return

    def check(m: discord.Message) -> bool:
        return m.author == ctx.author and m.channel == ctx.channel

    async def preguntar(texto: str):
        await ctx.send(texto)
        try:
            msg = await bot.wait_for("message", check=check, timeout=300)
        except asyncio.TimeoutError:
            await ctx.send("⏰ Tiempo agotado. Asistente cancelado.")
            return None
        if msg.content.strip().lower() == "cancelar":
            await ctx.send("❌ Asistente cancelado.")
            return None
        return msg

    await ctx.send(
        "📝 **Nuevo uniforme** — responde a cada pregunta.\n"
        "Escribe `cancelar` en cualquier momento para abortar."
    )

    # 1. Titulo
    m = await preguntar("**1.** ✏️ ¿Título del uniforme?\n"
                        "_(ej: `Uniforme Escala Alumna Hombre`)_")
    if not m:
        return
    titulo = m.content.strip()

    # 2. Descripcion
    m = await preguntar("**2.** 📄 ¿Descripción?")
    if not m:
        return
    descripcion = m.content.strip()

    # 3..N Componentes
    valores = []
    for i, (emoji, nombre) in enumerate(COMPONENTS, start=3):
        m = await preguntar(f"**{i}.** {emoji} **{nombre}** — envía `actual/máximo` "
                            f"_(ej: `0/367`)_")
        if not m:
            return
        valores.append(parse_valor(m.content))

    # Codigo
    n = len(COMPONENTS) + 3
    m = await preguntar(f"**{n}.** 📥 ¿**Código**?")
    if not m:
        return
    codigo = m.content.strip()

    # Imagen
    m = await preguntar(f"**{n + 1}.** 🖼️ Adjunta la **imagen** del uniforme.")
    if not m:
        return
    if not m.attachments:
        await ctx.send("❌ No adjuntaste ninguna imagen. Asistente cancelado.")
        return
    att = m.attachments[0]

    # --------------------------------------------------------------
    # Construir embed
    # --------------------------------------------------------------
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    embed = discord.Embed(
        title=f"🔥 {titulo}",
        description=descripcion,
        color=EMBED_COLOR,
    )
    embed.set_author(name=AUTHOR_NAME)
    for (emoji, nombre), valor in zip(COMPONENTS, valores):
        embed.add_field(name=f"{emoji} {nombre}", value=f"`{valor}`", inline=True)
    embed.add_field(name="📥 Código", value=f"`{codigo}`", inline=True)
    embed.set_footer(text=f"{FOOTER_TEXT} · {fecha}")

    # Reenviamos la imagen adjunta (mas fiable que enlazar el CDN)
    ext = att.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("png", "jpg", "jpeg", "gif", "webp"):
        ext = "png"
    nombre_archivo = f"uniforme.{ext}"
    archivo = await att.to_file(filename=nombre_archivo)
    embed.set_image(url=f"attachment://{nombre_archivo}")

    # --------------------------------------------------------------
    # Publicar
    # --------------------------------------------------------------
    salida = bot.get_channel(OUTPUT_CHANNEL_ID)
    if salida is None:
        await ctx.send("❌ No encuentro el canal de salida. ¿El bot tiene acceso a él?")
        return

    await salida.send(embed=embed, file=archivo)
    await ctx.send(f"✅ Publicado en <#{OUTPUT_CHANNEL_ID}>.")


def build_armas_embed(titulo: str, items, minimo: int, emoji: str,
                      logo_url: str = None) -> discord.Embed:
    """Crea un embed con el mismo estilo que las imagenes de la tienda.

    logo_url: icono del autor y miniatura (se usa el icono del server).
    """
    lineas = [f"• **{nombre}** = `{precio}`" for nombre, precio in items]
    descripcion = (
        "\n".join(lineas)
        + "\n\n"
        + "*Para adquirir un producto abra un ticket; nuestros encargados "
        + "anónimos se pondrán en contacto lo antes posible contigo.*"
        + f"\n\n( mínimo pedidos de {minimo} armas )"
    )

    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    embed = discord.Embed(
        title=f"{emoji} {titulo} {emoji}",
        description=descripcion,
        color=ARMAS_COLOR,
    )
    embed.set_author(name=ARMAS_AUTHOR, icon_url=logo_url)
    if logo_url:
        embed.set_thumbnail(url=logo_url)
    embed.set_footer(text=f"Creado por {ARMAS_FOOTER_AUTHOR} · {fecha}")
    return embed


@bot.command(name="armas")
async def armas(ctx: commands.Context, cual: str = "todo"):
    """Publica las listas de armas (Amazon) en el canal donde se escribe.

    Uso:
      !armas          -> publica ambas listas (blancas + semi automaticas)
      !armas blancas  -> solo Armas Blancas
      !armas semi     -> solo Semi Automaticas
    """
    cual = cual.lower()

    # Icono del server (se usa como miniatura e icono del autor del embed).
    logo_url = ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None

    embeds = []
    if cual in ("todo", "blancas", "blanca"):
        embeds.append(
            build_armas_embed("Armas Blancas", ARMAS_BLANCAS, 10, "⚔️", logo_url)
        )
    if cual in ("todo", "semi", "semiautomaticas", "semiauto"):
        embeds.append(
            build_armas_embed("Semi Automaticas", SEMI_AUTOMATICAS, 3, "🔫", logo_url)
        )

    if not embeds:
        await ctx.reply("⚠️ Opción no válida. Usa `!armas`, `!armas blancas` o `!armas semi`.")
        return

    # Se publica en el mismo canal donde se escribio el comando.
    for embed in embeds:
        await ctx.send(embed=embed)


# --------------------------------------------------------------------------
# Mini servidor HTTP (keepalive)
# --------------------------------------------------------------------------
# Render (plan free) solo admite "web services": exigen que el proceso escuche
# en el puerto que Render pasa por la variable PORT. Un bot de Discord no sirve
# HTTP, asi que levantamos aqui un servidor minimo que responde "OK". Ademas,
# un ping externo (UptimeRobot) a esta URL evita que Render lo duerma.
class _KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Ordenador bot online")

    def log_message(self, *args):  # silencia el log de cada peticion
        pass


def start_keepalive_server():
    """Arranca el servidor HTTP en un hilo aparte (solo si Render da PORT)."""
    port = os.getenv("PORT")
    if not port:
        return  # en local no hace falta
    server = HTTPServer(("0.0.0.0", int(port)), _KeepAliveHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"🌐 Keepalive HTTP escuchando en el puerto {port}")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit(
            "❌ Falta el token. Crea un archivo .env con:  DISCORD_TOKEN=tu_token"
        )
    start_keepalive_server()
    bot.run(TOKEN)

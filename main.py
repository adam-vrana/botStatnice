import discord
from discord.ext import tasks
from datetime import date, time
import random
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import datetime

TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID = 1500082105827332116
STATNICE_DATUM = date(2026, 5, 31)
ZACATEK = date(2026, 5, 4)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *args):
        pass

def run_server():
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()

def progress_bar(zbývá):
    celkem = (STATNICE_DATUM - ZACATEK).days
    uplynulo = celkem - zbývá
    procent = max(0, min(100, int((uplynulo / celkem) * 100)))
    hotovo = int(procent / 5)
    zbytek = 20 - hotovo
    bar = "█" * hotovo + "░" * zbytek
    return bar, procent

def get_data(zbývá):
    tydny = zbývá // 7
    dny_navic = zbývá % 7

    if zbývá > 60:
        vzkazy = [
            "Ještě máš čas. Nebo máš?",
            "Netflix počká. Skripta nečekají.",
            "Pohoda. Teoreticky.",
            "Kdo se připravuje předem, ten se připravuje dobře.",
            "Dnes relax. Zítra taky. Ale pak opravdu začni.",
        ]
        motivace = [
            "Každý den bez učení je dar budoucímu tobě... který za to zaplatí.",
            "Říkají, že čas léčí vše. Státnice ne.",
            "Teď můžeš jít spát. Za měsíc ne.",
        ]
        emoji = "😴"
        barva = 0x57F287
        stav = "KLID"
    elif zbývá > 30:
        vzkazy = [
            "Přátelé tě budou minout. Skripta ne.",
            "Čas na kávu a učení. V tomhle pořadí.",
            "Začít dnes? Nebo počkat na 'správný' moment?",
            "Každý otevřený zápisník se počítá.",
            "Pomalu ale jistě. Spíš rychleji.",
        ]
        motivace = [
            "Průměrný člověk začne studovat 2 týdny před státnicemi. Nebuď průměrný.",
            "Zopakoval jsi dnes alespoň jednu věc? Ne? Tak teď.",
            "Comfort zone tě u tabule nezachrání.",
        ]
        emoji = "😬"
        barva = 0xFEE75C
        stav = "POZOR"
    elif zbývá > 14:
        vzkazy = [
            "Tohle není drill. Opakuj.",
            "Každý den se počítá. Vážně.",
            "Spánek je luxus. Znalosti jsou nutnost.",
            "Teď nebo nikdy. Spíš teď.",
            "Méně scrollování, více čtení.",
        ]
        motivace = [
            "Zkoušející si pamatuje ty, kteří přišli připraveni.",
            "Panika je normální. Přestaň panikařit a uč se.",
            "Kdo opakuje, ten vládne. Kdo neopakuje, ten drhne.",
        ]
        emoji = "😰"
        barva = 0xFFA500
        stav = "KRITICKÉ"
    else:
        vzkazy = [
            "PANIKA JE NA MÍSTĚ.",
            "Snad víš co děláš. Snad.",
            "Teď nebo nikdy. Nikdy není možnost.",
            "Všechno nejlepší. Budeš to potřebovat.",
            "Zhluboka dýchej. A pak se uč.",
        ]
        motivace = [
            "Tohle je ten moment. Celý rok vedl sem.",
            "Stres je energie. Přeměň ho na výkon.",
            "Za týden budeš přesně tam, kde chceš být.",
        ]
        emoji = "🔥"
        barva = 0xED4245
        stav = "ALARM"

    return random.choice(vzkazy), random.choice(motivace), emoji, barva, stav, tydny, dny_navic

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Každý den v 8:00 ráno (UTC+1 = Praha, Render běží v UTC takže 7:00 UTC)
@tasks.loop(time=time(hour=7, minute=0, tzinfo=datetime.timezone.utc))
async def daily_message():
    channel = client.get_channel(CHANNEL_ID)
    zbývá = (STATNICE_DATUM - date.today()).days

    if zbývá < 0:
        embed = discord.Embed(
            title="🎓 STÁTNICE JSOU ZA TEBOU!",
            description=(
                "### Přežil jsi.\n"
                "Tohle byl dlouhý boj. A zvládl jsi ho.\n\n"
                "Gratuluju, magistře. 🎉"
            ),
            color=0xA259FF
        )
        embed.set_footer(text="Statnice Sender • Mise splněna.")
        await channel.send(embed=embed)
        return

    vzkaz, motivace, emoji, barva, stav, tydny, dny_navic = get_data(zbývá)
    bar, procent = progress_bar(zbývá)

    embed = discord.Embed(
        title=f"{emoji}  STÁTNICE ZA {zbývá} DNÍ  {emoji}",
        color=barva
    )
    embed.add_field(
        name="⏳  Zbývá",
        value=f"**{zbývá} dní** ({tydny} týdnů a {dny_navic} dní)",
        inline=False
    )
    embed.add_field(
        name="📊  Postup",
        value=f"`{bar}` **{procent}%** odpracováno",
        inline=False
    )
    embed.add_field(
        name="💬  Dnešní zpráva",
        value=f"*{vzkaz}*",
        inline=False
    )
    embed.add_field(
        name="🧠  Zamysli se",
        value=f"_{motivace}_",
        inline=False
    )
    embed.add_field(
        name="🚨  Stav",
        value=f"**{stav}**",
        inline=True
    )
    embed.add_field(
        name="📅  Datum státnic",
        value=f"**{STATNICE_DATUM.strftime('%d. %m. %Y')}**",
        inline=True
    )
    embed.set_footer(text="Statnice Sender • Každý den se počítá. • Dnes je další šance.")

    soubory = [
        f for f in os.listdir("obrazky")
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if soubory:
        soubor = random.choice(soubory)
        cesta = os.path.join("obrazky", soubor)
        pripona = os.path.splitext(soubor)[1].lower()
        filename = f"obrazek{pripona}"
        embed.set_image(url=f"attachment://{filename}")
        with open(cesta, "rb") as f:
            obrazek = discord.File(f, filename=filename)
            await channel.send(file=obrazek, embed=embed)
    else:
        await channel.send(embed=embed)

@daily_message.before_loop
async def before_daily():
    await client.wait_until_ready()

@client.event
async def on_ready():
    print(f"✅ Bot přihlášen jako {client.user}")
    print(f"📅 Státnice: {STATNICE_DATUM} — zbývá {(STATNICE_DATUM - date.today()).days} dní")
    Thread(target=run_server, daemon=True).start()
    if not daily_message.is_running():
        daily_message.start()

client.run(TOKEN)
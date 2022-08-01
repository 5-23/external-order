import asyncio , humanfriendly

from nextcord.ext import commands
from nextcord import *

from datetime import *
import datetime

import func
from func import emojis
import nextwave as wavelink


INTENTS = Intents.all()

client = commands.Bot(command_prefix = "none",intents=INTENTS)

@client.slash_command(description = "공지를 올립니다")
async def 공지(inter : Interaction):
    if not inter.user.guild_permissions.administrator:
        return await inter.response.send_message("당신은 어드민이 아닙니다" , ephemeral=True)
    await inter.response.send_modal(EmbedModal())

class EmbedModal(ui.Modal):
    def __init__(self):
        super().__init__("공지")
        self.Etitle = ui.TextInput(label = "제목" , placeholder="공지사항!" , min_length=1 , max_length=100)
        self.Edescription = ui.TextInput(label = "내용" , placeholder="으악" , style = TextInputStyle.paragraph , min_length=0 , max_length=4000)

        self.add_item(self.Etitle)
        self.add_item(self.Edescription)

    async def callback(self, inter: Interaction):
        await inter.response.send_message(embed = Embed(title = self.Etitle.value , description = self.Edescription.value))


@client.slash_command(description="유저를 벤합니다")
async def 벤(inter : Interaction , 멤버 : Member = SlashOption(description="벤할 유저를 정하세요") , 사유 : str = SlashOption(description = "사유를 써주세요" , required = False)):
    await inter.response.defer()
    if inter.user.guild_permissions.ban_members:
        user = 멤버
        msg = 사유

        try:await user.ban(reason=msg)
        except:
            await inter.followup.send(embed = Embed(title=f"권한오류",color = 0xff0000) , ephemeral = True)
            return
        
        await inter.followup.send(embed = Embed(title=f"{inter.user}님이 {user}을/를 밴했습니다",description=f"사유:{msg}",color = 0xf42f2f) , view = UN(user = 멤버 , type = "ban"))
        
        del user , msg

    else:
        await inter.followup.send(embed = Embed(title="권한이 없어요",color=0xff0000))


@client.slash_command(description="유저를 킥합니다")
async def 킥(inter : Interaction , 유저 : Member = SlashOption(description="킥할 유저를 정하세요") , 사유 : str = SlashOption(description = "사유를 써주세요" , required = False)):
    if inter.user.guild_permissions.kick_members:
        user = 유저
        msg = 사유

        try:await user.kick(reason=msg)
        except:
            await inter.followup.send(embed = Embed(title=f"권한오류",color = 0xff0000) , ephemeral = True)
            return

        await inter.followup.send(embed = Embed(title=f"{inter.user}님이 {user}을/를 킥했습니다",description=f"사유:{msg}",color = 0xd22b2b))

        del user , msg
    else:
        await inter.followup.send(embed = Embed(title="권한이 없어요",color=0xff0000))

@client.slash_command(description = "멤버를 타임아웃(뮤트) 시킴니다.")
async def 타임아웃(inter : Interaction , 멤버 : Member = SlashOption(description = "멤버") , 시간 : str = SlashOption(description = "시간") , 사유 : str = SlashOption(description = "사유")):
        if inter.user.guild_permissions.administrator:
            await inter.response.defer()
            try:
                int(시간)
                시간 = str(시간)+"초"
            except:
                pass
            기간 = str(시간).replace("초","s").replace("분","m").replace("시간","h").replace("일","d").replace("주일","w").replace("주","w").replace("년","y")
            time = humanfriendly.parse_timespan(기간)
            print(time)

            max_time = 2419200.0
            if time > max_time:
                time = max_time
                시간 = "28일"
            
            await 멤버.edit(timeout=utils.utcnow() + datetime.timedelta(seconds=time))
            msg = await inter.followup.send(멤버.mention , embed = Embed(title = "타임아웃!",description = f"{멤버.mention} 님은 ``{시간}``동안 서버이용이 불가능합니다 \n\n사유:\n```\n{사유}\n```" , color= 0xfc3a01) , view =  UN(user = 멤버 , type = "timeout"))

            await asyncio.sleep(time)
            await msg.delete()

            del 기간 , time , max_time
        else:
            await inter.followup.send(content="" , embed = Embed(title="권한오류",color = 0xff0000) , ephemeral = True)



class UN(ui.View):
    def __init__(self , user : Member = None, type : str = None):
        super().__init__(timeout = None)
        self.type = type
        self.user = user

        if self.type == "ban": self.children[0].label = "벤 풀기"
        elif self.type == "timeout": self.children[0].label = "타임아웃 풀기"
    
    @ui.button(style = ButtonStyle.red , label = "load")
    async def sub(self , button : ui.Button , inter : Interaction):
        if self.type == "ban":
            if inter.user.guild_permissions.ban_members:
                try:self.children[0].disabled = True
                except:pass

                await self.user.unban()
                try:
                    await inter.message.edit(embed = inter.message.embeds[0].set_footer(icon_url = inter.user.avatar , text = f"{inter.user}님이 `벤`을 풀었습니다.") , view = self)
                except:
                    await inter.message.edit(embed = inter.message.embeds[0].set_footer(text = f"{inter.user}님이 `벤`을 풀었습니다.") , view = self)
            
            else:
                await inter.response.send_message("`유저 벤`권한이 없습니다!" , ephemeral=True)
        
        elif self.type == "timeout":
            if inter.user.guild_permissions.administrator:
                self.children[0].disabled = True
                await self.user.edit(timeout = None)
                await inter.message.edit(embed = inter.message.embeds[0].set_footer(icon_url = inter.user.avatar , text = f"{inter.user}님이 `타임아웃`을 풀었습니다.") , view = self)
            else:
                await inter.response.send_message("`어드민`권한이 없습니다!" , ephemeral=True)

@client.slash_command(description = "메세지를 삭제합니다")
async def 청소(inter : Interaction , 최대치 : str = SlashOption(description="청소할 양을 써주세요")):
    await inter.response.defer(ephemeral = True)
    await inter.followup.send("청소가 시작됐어요" , ephemeral = True)
    if inter.user.guild_permissions.manage_messages:
        num = 최대치
        if num == "모두":
            num = 9999999999999999999999999999999999999999999999
            int(num)
            await inter.channel.purge(limit = num)
            embed = Embed(title ="모든메세지가 삭제 되었습니다",color = 0x000fff)
            embed.set_footer(text = "by - {}".format(inter.user.name))
            await inter.channel.send(embed=embed)
        else:
            num = int(num)
            if num >= 9999999999999999999999999999999999999999999999:
                num = 9999999999999999999999999999999999999999999999
            await inter.channel.purge(limit = num)
            embed = Embed(description ="메세지{}개가 삭제 되었습니다".format(num),color = 0x000fff)
            embed.set_footer(text = "by - {}".format(inter.user.name))
            await inter.channel.send(embed=embed)
        del num

    else:
        embed = Embed(description ="{}님은 5청소를 사용할권한이 없습니다".format(inter.user.mention),color = 0x000fff)
        await inter.channel.send(embed=embed)
    
    del embed


@client.event
async def on_ready():
    client.loop.create_task(node_connect())

async def node_connect():
    await wavelink.NodePool.create_node(
        bot      = client,
        host     = 'lava.link',
        port     = 80,
        password = 'hydrox'
    )


@client.event
async def on_nextwave_node_ready(node : wavelink.Node):
    print(f"{node.identifier} 실행됨")

@client.event
async def on_nextwave_track_end(player : wavelink.Player , track : wavelink.Track , reason):
    vc : wavelink.Player = player.guild.voice_client
    voice_channel = client.get_channel(player.channel.id)
    if reason != "REPLACED":
        if len(voice_channel.members) == 1:
            return await vc.disconnect()
        if vc.loop:
            await vc.play(track)


@client.slash_command(description = "음악을 재생합니다")
async def 음악(inter : Interaction , 검색 : str = SlashOption(description = "검색할 곡을 쓰세요") , 멀티 : str = SlashOption(description = "다른사람들도 만질수있게 합니다" , choices = ["참" , "거짓"] , required = False)):    
    await inter.response.defer()
    func.musicSearch(user = inter.user , text = 검색).read()
    try: inter.user.voice.channel
    except: return await inter.followup.send("음성채널에 먼저 들어가주세요!")
    
    t = 0
    rmx = 0
    try:
        vc : wavelink.Player = await inter.user.voice.channel.connect(cls = wavelink.Player)
        vc.loop = True
    except:
        for voiceChannel in inter.guild.voice_channels:
            if (client.user in voiceChannel.members):
                t = 1
                if (len(voiceChannel.members) <= 2):
                    vc : wavelink.Player = inter.guild.voice_client
                    break
        if (t == 0):
            vc : wavelink.Player = inter.guild.voice_client
        
        try:vc
        except:return await inter.followup.send(embed = Embed(title = "이미 생성된 플레이어가 있어요!" , description = "자신의서버에서 음악을 듣고싶나요? [여기](https://discord.com/oauth2/authorize?client_id=871348411356545057&permissions=8&scope=bot%20applications.commands)를 클릭하여 초대해보세요!" , color = 0xeeeeee))

    array = await wavelink.YouTubeTrack.search(query = 검색 , return_first = False)
    embed = Embed(title = f"재생할곡을 선택해주세요!" , color = 0x2f3136)

    admin = admin = inter.user
    if 멀티 == "거짓":admin = None
    
    await inter.followup.send(embed = embed , view = MusicPlayer(vc = vc , musicArray = array , q = 검색 , admin = admin))

@음악.on_autocomplete("검색")
async def TagUpdate(inter : Interaction , text : str):
    Text = []
    for t in func.musicSearch(user = inter.user).load():
        if text in t:Text.append(t)
    if Text == []:Text = ["추천검색어가 없습니다."]
    await inter.response.send_autocomplete(Text)
 
class MusicSelect(ui.Select):
    def __init__(self , vc : wavelink.Player ,  musicArray : list , q , admin : Member = None):
        option = []
        i = 0
        for music in musicArray:
            option.append(SelectOption(label = music.title , value = str(i)))
            i += 1
        super().__init__(placeholder = "여기서 음악을 선택하세요!" , options = option)
        vc.loop = True
        self.vc = vc
        self.q = q
        self.musicArray = musicArray
        self.admin = admin

    async def callback(self , inter : Interaction):
        if self.admin == inter.user or self.admin == None:
            await inter.response.defer()
            try:await inter.user.voice.channel.connect(cls = wavelink.Player)
            except:pass
            MUSIC : wavelink.Track = self.musicArray[int(self.values[0])]
            self.play = await self.vc.play(MUSIC)
            if self.vc.volume == 100:
                await self.vc.set_volume(50)
            embed = Embed(title = f"{MUSIC}{emojis.music()}" , description = f"불륨 : {self.vc.volume}" , color = 0x2f3136)
            await inter.message.edit(embed = embed)
            print(MUSIC.uri)
            img = f"https://img.youtube.com/vi/{MUSIC.identifier}/mqdefault.jpg"
            url = MUSIC.uri
            embed.set_image(url = img)
            embed.url = url
            await inter.message.edit(embed = embed)
        else:
            await inter.response.send_message(embed = Embed(title = "자신의것을 사용해주세요!" , description = "혹시 자신의 서버에 봇을 초대하고 싶으신가요? [여기](https://discord.com/oauth2/authorize?client_id=871348411356545057&permissions=8&scope=bot%20applications.commands)를 클릭하여 초대해보세요!" , color = 0xeeeeee) , ephemeral = True)

class MusicModal(ui.Modal):
    def __init__(self , vc : wavelink.Player):
        super().__init__("음악 변경!")
        self.music = ui.TextInput(label = "변경할 곡을 입력하세요" , placeholder = "여기에 입력해주세요!")
        self.vc = vc
        self.add_item(self.music)
        

    async def callback(self, inter : Interaction):
        msg = await inter.response.send_message("변경중..." , ephemeral = True)
        array = await wavelink.YouTubeTrack.search(query = self.music.value , return_first = False)
        embed = Embed(title = f"여기서 음악을 선택해주세요" , color = 0x2f3136)
        await inter.message.edit(embed = embed , view = MusicPlayer(vc = self.vc , musicArray = array , q = self.music.value))
        await msg.delete()
class MusicPlayer(ui.View):
    def __init__(self , vc : wavelink.Player , musicArray : list , q : str , admin : Member = None):
        super().__init__(timeout = 60*60)
        self.add_item(MusicSelect(vc = vc , musicArray = musicArray , q = q , admin = admin))
        # self.add_item(MusicButton(select = select))

        self.vc = vc
        self.admin = admin
    @ui.button(style = ButtonStyle.green , emoji = emojis.musicVloumeD())
    async def down(self , button : ui.Button , inter : Interaction):
        if self.admin == inter.user or self.admin == None:
            if self.vc.volume == 0:return await inter.response.send_message("불륨이 0입니다" , ephemeral = True)
            await self.vc.set_volume(self.vc.volume-10)

            try:
                embed = Embed(title = inter.message.embeds[0].title , description = f"불륨 : {self.vc.volume}" , color = inter.message.embeds[0].color)
                embed.set_image(url = str(inter.message.embeds[0].image.url))
                embed.url = inter.message.embeds[0].url
                await inter.message.edit(embed = embed)
            except:
                embed = Embed(title = inter.message.embeds[0].title , description = f"불륨 : {self.vc.volume}" , color = inter.message.embeds[0].color)
                await inter.message.edit(embed = embed)
        else:
            await inter.response.send_message(embed = Embed(title = "자신의것을 사용해주세요!" , description = "혹시 자신의 서버에 봇을 초대하고 싶으신가요? [여기](https://discord.com/oauth2/authorize?client_id=871348411356545057&permissions=8&scope=bot%20applications.commands)를 클릭하여 초대해보세요!" , color = 0xeeeeee) , ephemeral = True)

    @ui.button(style = ButtonStyle.red , emoji = emojis.musicStop())
    async def stop(self , button : ui.Button , inter : Interaction):
        if self.admin == inter.user or self.admin == None:
            self.vc.loop = False
            try:await inter.user.voice.channel.connect(cls = wavelink.Player)
            except:pass
            await self.vc.stop()
            
            embed = Embed(title = f"재생할곡을 선택해주세요!" , color = 0x2f3136)
            await inter.message.edit(embed = embed) 
        else:
            await inter.response.send_message(embed = Embed(title = "자신의것을 사용해주세요!" , description = "혹시 자신의 서버에 봇을 초대하고 싶으신가요? [여기](https://discord.com/oauth2/authorize?client_id=871348411356545057&permissions=8&scope=bot%20applications.commands)를 클릭하여 초대해보세요!" , color = 0xeeeeee) , ephemeral = True)
    @ui.button(style = ButtonStyle.gray , emoji = emojis.search())
    async def change(self , button : ui.Button , inter : Interaction):
        if self.admin == inter.user or self.admin == None:

            for item in self.children:
                item.disabled = True
            
            await inter.response.send_modal(MusicModal(vc = self.vc))
        else:
            await inter.response.send_message(embed = Embed(title = "자신의것을 사용해주세요!" , description = "혹시 자신의 서버에 봇을 초대하고 싶으신가요? [여기](https://discord.com/oauth2/authorize?client_id=871348411356545057&permissions=8&scope=bot%20applications.commands)를 클릭하여 초대해보세요!" , color = 0xeeeeee) , ephemeral = True)
    
    @ui.button(style = ButtonStyle.red , emoji = emojis.musicDisabled())
    async def kill(self , button : ui.Button , inter : Interaction):
        if self.admin == inter.user or self.admin == None:
            try:await inter.user.voice.channel.connect(cls = wavelink.Player)
            except:pass

            for item in self.children:
                item.disabled = True

            self.vc.loop = False
            await self.vc.stop()
            await self.vc.disconnect()
            
            embed = Embed(title = f"음악재생을 마칩니다." , color = 0x2f3136)
            # embed.set_image(url = MUSIC)

            await inter.message.edit(embed = embed , view = self)
        else:
            await inter.response.send_message(embed = Embed(title = "자신의것을 사용해주세요!" , description = "혹시 자신의 서버에 봇을 초대하고 싶으신가요? [여기](https://discord.com/oauth2/authorize?client_id=871348411356545057&permissions=8&scope=bot%20applications.commands)를 클릭하여 초대해보세요!" , color = 0xeeeeee) , ephemeral = True)
   

    @ui.button(style = ButtonStyle.green , emoji = emojis.musicVloumeU())
    async def up(self , button : ui.Button , inter : Interaction):
        if self.admin == inter.user or self.admin == None:
            await self.vc.set_volume(self.vc.volume+10)
            try:
                embed = Embed(title = inter.message.embeds[0].title , description = f"불륨 : {self.vc.volume}" , color = inter.message.embeds[0].color)
                embed.set_image(url = str(inter.message.embeds[0].image.url))
                embed.url = inter.message.embeds[0].url
                await inter.message.edit(embed = embed)
            except:
                embed = Embed(title = inter.message.embeds[0].title , description = f"불륨 : {self.vc.volume}" , color = inter.message.embeds[0].color)
                await inter.message.edit(embed = embed)
        else:
            await inter.response.send_message(embed = Embed(title = "자신의것을 사용해주세요!" , description = "혹시 자신의 서버에 봇을 초대하고 싶으신가요? [여기](https://discord.com/oauth2/authorize?client_id=871348411356545057&permissions=8&scope=bot%20applications.commands)를 클릭하여 초대해보세요!" , color = 0xeeeeee) , ephemeral = True)












client.run("token")
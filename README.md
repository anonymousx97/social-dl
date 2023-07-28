# Social Media downloader bot.
> Formerly "Lightweight" XD

![Header Image](https://github.com/anonymousx97/social-dl/blob/main/assets/social_downloader.png?raw=true)

<b>A Telegram User-Bot to Download Media from various websites and send in chat.</b>

### Supported Platforms:
  - Facebook
  - Instagram
  - Reddit
  - Threads.net
  - Tiktok
  - Twitter
  - YouTube 


### For android local deploy:
  * Download Latest [Termux](https://github.com/termux/termux-app/releases).
     ```bash
     # Change Default repository of termux.
     termux-change-repo
     # ( Select Single mirror then default )
     # Update local packages.
     yes|apt update && yes|apt upgrade
     ```

### Installation:
  Note: If deploying using Dockerfile add UPSTREAM_REPO var with repo link as it's value.

  ```bash
  # Install required packages.
  apt install -y python3 git curl python-pip ffmpeg

   # Clone Repo.
  git clone -q https://github.com/anonymousx97/social-dl
  cd social-dl

  # Install Pypi packages
  pip install -U setuptools wheel

  # For Termux Env:
  grep -v uvloop req.txt | xargs -n 1 pip install

  # For Non Termux Env:
  pip install -r req.txt

  #Setup config.env
  cp sample-config.env config.env
  # Add your variables after running next command.
  nano config.env
  ```

### Config:
   * Get API_ID and API_HASH from https://my.telegram.org/auth .
   * Generate String Session by running this in Termux: 
     ```bash 
     bash -c "$(curl -fsSL https://raw.githubusercontent.com/ux-termux/string/main/Termux.sh)" 
     ```
     > It will ask you to choose pyrogram version. Select 2.

   * LOG_CHAT: Create A Log Channel and add it's id along with -100 at the beginning.
   * API_KEYS: Optional Instagram scrapping keys from <a href=https://webscraping.ai/>API. </a> recommended to add if you wanna reduce Instagram dl failures.
     
   * <details>
     <summary>Tap here for The Message IDs : </summary>
      Send 2 messages in your log channel, message text is an empty list : []

     * Copy the links of those messages.
     
     * The last digits of these links are the message ids.
     
     * These two are your AUTO_DL_MESSAGE_ID and BLOCKED_USERS_MESSAGE_ID DB.
     * Add their IDs in config respectively.


     Now send another message but this time include your id in the list: [12345678]
     
     * Copy this message's link and add the message id in USERS_MESSAGE_ID var
     </details>
   * Trigger : Trigger to access bot.
   * Dev Mode: Set to 1 if you want access to exec, sh, shell commands.
     > These commands can be dangerous if used carelessly, Turn on at your own risk.
     > if set to 1 both you and sudo users can use these commands.

### Start bot
  ```bash
  cd social-dl && python3 -m app
  ```

  * If everything is correct you will get <b><i>Started</i></b> stdout in terminal and in your channel.
  * Use `.help` to get list of commands in bot.

### Known Instagram limitations:
  * If deployed on a VPS or any server Instragram might block access to some content.  
  After hitting Instagram's rate limit image download might not work because servers and vps usually have static IP and Instagram would block access.
  * Deploying it locally would solve all of those issues because most of us are likely to have dynamic IP.  
  * Bot <s>is</s> was made lightweight with local deploys in mind. So battery life will definitely take a hit.
  * Logging in with your Instagram which would solve the rate-limit issues is not added and won't be added because 2 of my accounts were suspended till manual verification for using scrapping bots like these.

## Contact
 * For any issues or questions related to deploy contact me on  
 [Telegram](https://t.me/anonymousx97)

# Special Thanks:
 - [Dan](https://github.com/delivrance) for [Pyrogram](https://github.com/pyrogram/pyrogram)
 - All Libraries used in the project.
   
 - [Kakashi](https://github.com/AshwinStr) for the Banner and helping with coding concepts.
   
 - [Userge-X](https://github.com/code-rgb/USERGE-X) and [UX-Jutsu](https://github.com/ashwinstr/ux-jutsu) for basic userbot concepts.
  
 - [NotShroud](https://t.me/NotShroudX97) for getting me into userbot stuff.
   
 - [Alicia Dark](https://github.com/Thegreatfoxxgoddess) for Social-DL Idea and inspiring / pushing me to explore modding TG bots.
   
 - [IsthisUser](https://github.com/dishapatel010) for helping with Instagram and threads support.
 
 - [Fnix](https://github.com/fnixdev), [Lucky Jain](https://github.com/lostb053), [Jeel Patel](https://t.me/jeelpatel231) for teaching/helping with code stuff and suggesting improvements.
 - [Avinash Reddy](https://t.me/AvinashReddy3108) for suggesting the use of [Gallery-DL](https://github.com/mikf/gallery-dl)


# Disclaimer:
Social-DL provides a way for users to download and upload media. While I facilitate these actions, it is important to note that the content accessed, downloaded, or uploaded through the bot is entirely the responsibility of the users. I do not distribute or endorse any specific media content.

Users are solely responsible for the types of media they download or upload using the Bot. They should ensure that they have the legal right to access or share the media files in question and comply with all applicable copyright laws and regulations. I do not monitor or control the nature, legality, or appropriateness of the content exchanged through the Bot.

It is essential for users to exercise caution and use our service in accordance with the terms of service and relevant laws. Any activities performed by users utilizing the Bot are done at their own risk. I recommend users to respect intellectual property rights, adhere to copyright laws, and obtain proper permissions when necessary.

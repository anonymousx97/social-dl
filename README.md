# Light weight Social Media downloader bot.
  * Supported Platforms:
    * Videos: Instagram, Tiktok, Twitter, YouTube Shorts
    * Images: Instagram, Reddit
    * Gif : Reddit

## Usage and Commands:
  * Send supported links in any authorised chat/channel.   
  Bot will try to download and send the media.  

  * Owner only commands:
  * `.dl link` to download and send media in any chat.
  * `.bot update` to refresh chat list without restarting bot.
  * `.bot restart` to restart bot.
  * `.bot ids` to get chat / channel / user IDs.
  * `.bot join or leave` to join / leave chat using ID.
  * `.del` reply to a message to delete. 
  * `.purge` to delete all messages between command and replied message.

  These commands can be used anywhere.  

  * Developer Mode Commands:
    * `.sh` to run shell commands.  

        Example: `.sh ls`  

    * `.exec` to run python code.  

        Example: `.exec print(1)` 

    These commands are dangerous and are disabled by default.
    Add `DEV_MODE="yes"` in config to enable these.

## For android local deploy:
  * Download Latest [Termux](https://github.com/termux/termux-app/releases).
     ```bash
     # Change Default repository of termux.
     termux-change-repo
     # ( Select Single mirror then default )
     # Update local packages.
     yes|apt update && yes|apt upgrade
     ```

## Installation:
  ```bash
  # Install required packages.
  apt install -y python git python-pip ffmpeg

   # Clone Repo.
  git clone -q https://github.com/anonymousx97/social-dl
  cd social-dl

  # Install Pypi packages
  pip install -U setuptools wheel
  pip install -r req.txt

  #Setup config.env
  cp sample-config.env config.env
  # Add your variables after running next command.
  nano config.env
  ```

## Config:
   * Get API_ID and API_HASH from https://my.telegram.org/auth .
   * Generate String Session by running this in Termux: 
     ```bash 
     bash -c "$(curl -fsSL https://raw.githubusercontent.com/ux-termux/string/main/Termux.sh)" 
     ```
     * It will ask you to choose pyrogram version. Select 2.

   * <details> 
     <summary> Message_link : </summary>

     * Create a private channel on TG.
     * Send a list of Chat/Channel ids starting with -100 in your log channel like below.
        Edit this message and add chats you want to add in future.
       <p align="right"><img src="https://telegra.ph/file/394daa80fd53c895cbe6e.jpg"</p>
     * Bot will automatically download links in those chats/channels.
     * Now copy that message's link and you will get something like  
       https://t.me/c/123456789/1
     * So your values would be LOG=-100123456789 MESSAGE=1
     </details>

   * User : Your user id to control bot.
   * Trigger : Trigger to access bot.


## Start bot
  ```bash
  python socialbot.py 
  ```

  * If everything is correct you will get <b><i>Started</i></b> stdout in terminal and in your channel.

## Setup a quick run command for bot.
  ```bash
  echo "alias runbot='cd social-dl && python socialbot.py'" >> ~/.bashrc && bash
  ``` 

  Now you can run bot with `runbot`

## Known limitations:
  * If deployed on a VPS or any server Instragram might block access to some content.  
  After hitting Instagram's rate limit image download might not work because servers and vps usually have static IP and Instagram would block access.
  * Deploying it locally would solve all of those issues because most of us are likely to have dynamic IP.  
  Bot is made lightweight with local deploys in mind. But battery life will take some hit anyway.
  * Logging in with your Instagram which would solve the rate-limit issues is not added and won't be added because 2 of my accounts were suspended till manual verification for using scrapping bots like these.  

## Contact
 * For any questions related to deploy or issues contact me on  
 [Telegram](https://t.me/anonymousx97)

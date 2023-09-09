FROM ghcr.io/anonymousx97/build_essentials:main

# adding email and username to the bot
RUN git config --global user.email "88324835+anonymousx97@users.noreply.github" \
    && git config --global user.name "anonymousx97"

# Exposing Ports for Web Server
EXPOSE 8080 22 8022
 
# Adding Remote Container Start Command
CMD bash -c "$(curl -fsSL https://raw.githubusercontent.com/anonymousx97/Docker/main/start)"
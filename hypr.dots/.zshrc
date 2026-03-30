# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc. Initialization code that may require console input (password prompts, [y/n] confirmations, etc.) must go above this block; everything else may go below. if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
 #source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
#fi

# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH
ZSH_DISABLE_COMPFIX=true
export ZSH="$HOME/.oh-my-zsh"

#ZSH_THEME="agnoster"
ZSH_THEME="powerlevel10k/powerlevel10k"
plugins=(
    git
    archlinux
    #zsh-autosuggestions
   # zsh-syntax-highlighting
)

source $ZSH/oh-my-zsh.sh
source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh
# Check archlinux plugin commands here
# https://github.com/ohmyzsh/ohmyzsh/tree/master/plugins/archlinux

# Aliases

# дефолт в файлах удобнее лазить 

alias fileviev='wal -i /home/hexov/Downloads/Untitled.jpg; clear; ranger; zsh'
alias themes='python3 ~/.config/hypr/scripts/hypr.themes-utiliti-v2/menu.py'
alias ls='exa --icons --color=always --group-directories-first'
alias ll='exa -alF --icons --color=always --group-directories-first'
alias la='exa -a --icons --color=always --group-directories-first'
alias l='exa -F --icons --color=always --group-directories-first'
alias l.='exa -a | egrep "^\."'
alias c='clear'
alias mkd='mkdir'

# слишком удобно чтобы не юзать 

alias py='python3'

# ну кому как люди из рф меня понимают 

alias zapret='bash ~/zapret-discord-youtube-linux/main_script.sh'

# обновление системы на постоянке происходит 

alias update='sudo pacman -Syu'

# просто и удобно chmod постоянно нужен 

alias chx='chmod +x'
alias chxa='chmod +x *'
alias ch='chmod'

# алиасы cargo (компилятор rust)

alias cr='cargo run'
alias cb='cargo build'
alias cc='cargo check'
alias cn='cargo new'

# удобные git алиасы (сам только пробую но пока что минусов не вижу)

alias g='git'
alias ga='git add'
alias gaa='git add --all'
alias gc='git commit -v'
alias gcm='git commit -m'
alias gco='git checkout'
alias gcb='git checkout -b'
alias gst='git status'
alias gl='git pull'
alias gp='git push'
alias gpf='git push --force-with-lease'
alias gd='git diff'
alias gds='git diff --staged'
alias glog='git log --oneline --graph --decorate'
alias gundo='git reset --soft HEAD~1'

# очень удобно указываешь файл а он открываетя в выбраной для его формата утилите

# Открывать файлы в нужных программах по расширению
alias -s txt='nvim'          # открыть .txt в neovim
alias -s md='nvim'           # markdown
alias -s py='nvim'
alias -s js='nvim'
alias -s sh='nvim'
alias -s css='nvim'
alias -s scss='nvim'
alias -s rs='nvim'
alias -s qml='nvim'
alias -s conf='nvim'
alias -s html='nvim'
alias -s jpg='feh'           # просмотр изображений
alias -s png='feh'
alias -s pdf='zathura'       # или evince, xdg-open
alias -s toml='nvim'

# Display Pokemon-colorscripts
# Project page: https://gitlab.com/phoneybadger/pokemon-colorscripts#on-other-distros-and-macos
# pokemon-colorscripts --no-title -s -r


### From this line is for pywal-colors
# Import colorscheme from 'wal' asynchronously
# &   # Run the process in the background.
# ( ) # Hide shell job control messages.
# Not supported in the "fish" shell.
(cat ~/.cache/wal/sequences &)

# Alternative (blocks terminal for 0-3ms)
#cat ~/.cache/wal/sequences

# To add support for TTYs this line can be optionally added.
#source ~/.cache/wal/colors-tty.sh

#neofetch
#catnip
hfetch
killall -SIGUSR1 kitty

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
export PATH="$PATH:$HOME/eww/target/release"
source /home/hexov/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# Created by `pipx` on 2026-01-06 17:33:08
export PATH="$PATH:/home/hexov/.local/bin"
export PATH="$PATH:/home/hexov/.config/CustomApps"
export PATH="$HOME/notebooklm-env/bin:$PATH"

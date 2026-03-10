# Hyprland Dotfiles

This repository contains my personal configuration and dotfiles for the Hyprland window manager, aiming to enhance productivity and streamline the user experience. Below you will find detailed instructions on how to install, configure, and make the most of these dotfiles.

## Installation
1. **Clone the Repository**  
   Clone this repository to your local machine:
   ```bash
   git clone https://github.com/userhexov/hypr.dots.git
   cd hypr.dots
   ```

2. **Install Required Packages**  
   Ensure you have `Hyprland` and any necessary dependencies installed. On a typical Linux distro like Arch, you can do:
   ```bash
   sudo pacman -S hyprland
   ```

3. **Symlink Dotfiles**  
   Create symlinks from the dotfiles in this repository to your home directory:
   ```bash
   ln -s $(pwd)/.config/hypr/hyprland.conf ~/.config/hypr/hyprland.conf
   ln -s $(pwd)/.config/hypr/hyprland-theme.conf ~/.config/hypr/hyprland-theme.conf
   ```

## Configuration
- **Hyprland Configuration**  
  Customize the `hyprland.conf` file to fit your personal preferences. Modify aspects such as keybindings, appearance, and window rules.

- **Theme Customization**  
  Use `hyprland-theme.conf` to define your color schemes, fonts, and overall aesthetic. Example configurations are included in the repository.

## Features
- Custom Keybindings  
  Code your own keybindings to streamline your workflow. Easily switch between workspaces or launch applications with ease.

- Multiple Monitors Support  
  This setup is optimized for use with multiple monitors, allowing you to configure layouts and placements effectively.

- Theme Management  
  Supports easy switching between themes with just a command, making customization simple and fast.

## Structure
- `.config/`  
  All configuration files relevant to Hyprland reside in this directory.
- `README.md`  
  Documentation to help you understand and utilize the dotfiles.

### Contributing
Feel free to submit issues or pull requests if you have suggestions for improvements or would like to contribute!

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
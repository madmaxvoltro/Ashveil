#!/bin/bash
if command -v zenity >/dev/null 2>&1; then
  zenity --info --title="Installation Message" --text="Hello! This is your Linux/macOS install script speaking."
else
  echo "zenity is not installed. Please install zenity to see the message box."
fi

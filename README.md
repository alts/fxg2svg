fxg2svg
=======

Tool for converting .fxg files to .svg


## usage
there are two ways to use this tool:
- options 1:
  ```bash
  python fxg2svg.py your-fxg-file-path
  ```
- option 2:
  ```bash
  python fxg2svg.py
  ```
  then follow the on screen instructions
  
## Useful tips for Flash users:
To ensure proper conversion of files with this script ensure the following:
1. Your FXG file source contain only fill types and no lines (can be achieved using convert lines to fill command in flash)
2. Your top-most flash element is a Graphic type and not a raw drawing (or other element)
3. You are using python 3.6+
4. You have installed lxml library using pip

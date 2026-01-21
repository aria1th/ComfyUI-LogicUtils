Logic Utilities for someone who wants

~~prime list calculation in comfyui~~
Proper documentation is being prepared, however there are too many nodes
![image](https://github.com/user-attachments/assets/8e388417-6912-41d7-98fa-798b50eacfda)

## Tests

Run from the repo root:

`python -m unittest discover -s tests`

## Notes

- Auto-install runs when loaded in ComfyUI. To disable it, set `COMFYUI_LOGICUTILS_SKIP_INSTALL=1`.
- To force CPU/GPU tagger dependency selection, set `COMFYUI_LOGICUTILS_IMGUTILS_VARIANT=cpu` or `COMFYUI_LOGICUTILS_IMGUTILS_VARIANT=gpu`.

# <img src="{image.file.url}" alt="{alt_text}"><figcaption>{alt_text}</figcaption>
image_html = f'''
<figure>
    <img src="%s" alt="%s"><figcaption>%s</figcaption>
</figure>
'''

panel_default = f'''<details><summary>%s</summary><p>%s</p></details>'''
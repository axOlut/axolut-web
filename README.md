# axOlut — site officiel

Site statique (HTML, CSS, JavaScript sans framework), hébergé sur GitHub Pages.

- Pages en français à la racine, en anglais dans `en/`.
- Tous les textes sont dans `tools/content_*.py`. Après une modification :

```
python3 tools/build.py
```

Pour un nom de domaine : `SITE_URL=https://axolut.com python3 tools/build.py`, puis ajouter le fichier `CNAME`.

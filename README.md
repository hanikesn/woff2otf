# woff2otf

This is a small utility to convert WOFF files to the OTF font format. It uses Javascript, so you can run it in the browser. It depends on the [port of zlib to javascript](https://github.com/nodeca/pako), you need to include [this file](https://github.com/nodeca/pako/blob/master/dist/pako_inflate.js) in your page. Or just [go to this page to convert WOFF to OTF online](https://arty.name/woff2otf/).

## Usage

```
convert_streams(<ArrayBuffer>)  // returns <ArrayBuffer> containing OTF font
```

## Credits

Big thanks to Steffen Hanikel for his Python implementation of this script, which I later converted to Javascript.
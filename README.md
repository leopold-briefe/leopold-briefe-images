# kalbeck-images

Throw-away code repo to process kalbeck images.

## issues

(checked kalbeck_2 bis kalbeck_2__0100_b)

### Seiten herausgeschnitten?

* kalbeck_2__0041_a.tif -> 14. März
* kalbeck_2__0041_b.tif -> 17. März

### doppelt gescannt

* kalbeck_2__0063_a.tif sameAs kalbeck_2__0064_a.tif
* kalbeck_2__0063_b.tif sameAs kalbeck_2__0064_b.tif

## compress

copied from <https://github.com/acdh-oeaw/arche-curationTools/blob/master/tif_lzw.sh>

```bash
./src/compress_tiffs.sh orig-files
```

## split

written by <https://chatgpt.com/>

```bash
uv run src/split_pages.py orig-files/  --output split/ --threshold 6600 --margin 80
```

## filechecker

adapt input and ouput folder

```bash
./src/arche__filechecker.sh
```

e.g.

```bash
echo "run filechecker"
rm -rf ${PWD}/kalbeck_2 && mkdir ${PWD}/kalbeck_2
docker run \
  --rm \
  --network="host" \
  -v ${PWD}/kalbeck_2:/reports \
  -v /home/csae8092/Schreibtisch/R_kalbeck_27373/kalbeck/kalbeck_2/splitted:/data \
  --entrypoint arche-filechecker \
  acdhch/arche-ingest \
  --overwrite --skipWarnings /data /reports
```

## ARCHE metadaten

`arche/` holds static metadata and `arche__ingest_md.sh` script which calls `src/arche.py` responsible for creating `to_ingest/arche.ttl`
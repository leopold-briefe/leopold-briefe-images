# Leopold Briefe Images

Repo to generate ARCHE-RDF for Leopold-Briefe Facsimiles

copied from <https://github.com/acdh-oeaw/arche-curationTools/blob/master/tif_lzw.sh>

## image processing

```shell
./src/compress_tiffs.sh
```

adapt path to files you want to lzw-compress and run the script

## ARCHE metadaten

`arche/` holds static metadata and `arche__ingest_md.sh` script which calls `src/arche.py` responsible for creating `to_ingest/arche.ttl`

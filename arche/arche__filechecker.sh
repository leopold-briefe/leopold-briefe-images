#/bin/bash
echo "run filechecker"
ARCHIV=OÖLA
mkdir ${PWD}/fc_reports/${ARCHIV}
docker run \
  --rm \
  --network="host" \
  -v ${PWD}/fc_reports/${ARCHIV}:/reports \
  -v /home/csae8092/Schreibtisch/ACDH_DHRI_leopoldBriefe/scans/${ARCHIV}:/data \
  --entrypoint arche-filechecker \
  acdhch/arche-ingest \
  --overwrite --skipWarnings /data /reports

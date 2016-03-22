#!/bin/bash
SOURCE=$1
WORK=`mktemp -d`
# remove path & extension
NAME=${SOURCE%.*}
NAME=${NAME##*/}
#TYPE=$(file -b $SOURCE | awk '{ print $1 }')
TYPE="${SOURCE##*.}"
#DIR=`dirname $SOURCE`
DIR=/tmp
LOG=/home/nxpush/log/ocr.log

pdfToTiff(){
 # conversion TIFF
  gs -q -sDEVICE=tiffg4 -dBATCH -dNOPAUSE -r500 -sOutputFile="$WORK/$NAME.tif" "$SOURCE"
}

doOcr(){
  tesseract -l fra "$WORK/$NAME.tif" "$WORK/$NAME" pdf 2>&1 >/dev/null
}

# $1 code de sortie
clean_exit(){
  rm -r $WORK
  exit $1
}

# $1 level
# $2 message
log(){
  if [ -n "$2" ]
  then
    MSG="$2"
  else
    read MSG
  fi
  if [ -n "$MSG" ]
  then
    echo "$MSG" | sed "s/^/$(date '+[%F %T]') $1 /" >>$LOG
  fi
}

main(){
  log DEBUG "source: $SOURCE"
  log DEBUG "tmp: $WORK"
  log DEBUG "source type: $TYPE" 
  if [ "PDF" == ${TYPE^^} ]
  then 
    pdfToTiff 2> >( log ERROR )
  elif [ "TIF" == ${TYPE^^} ]
  then
    mv "$SOURCE" "$WORK/." 2> >( log ERROR )
  else 
    log DEBUG "$SOURCE is not detected as a PDF"
    echo "$SOURCE"
    clean_exit 0
  fi
  log DEBUG "tmp content: $(ls $WORK)"
  if [ -f "$WORK/$NAME.tif" ]
  then
    doOcr | tr '\n' ' ' | log DEBUG
    cp "$WORK/$NAME.pdf" "$DIR" 2> >( log ERROR )
  fi
  if [ -f "$DIR/$NAME.pdf" ]
  then 
    echo "$DIR/$NAME.pdf"
    clean_exit 0
  else
    clean_exit 1
  fi
}

main

